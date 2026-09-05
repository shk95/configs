[CmdletBinding(DefaultParameterSetName = 'Default')]
param(
    [Parameter(ParameterSetName = 'Check')]
    [switch] $Check,

    [Parameter(ParameterSetName = 'Force')]
    [switch] $Force,

    # Which features this host deploys. Selection is host state, not desired
    # state: the manifest declares what exists, these switches decide how much
    # of it this host takes. Exactly one may be supplied; with none, an applied
    # host keeps its recorded selection and a new host takes everything, which
    # is what this script did before selection existed.
    [string[]] $Feature,
    [string[]] $Add,
    [switch] $Minimal,
    [switch] $All
)

$ErrorActionPreference = 'Stop'
# INV windows/check-exit-contract — Get-WinEnvCheckStatus ranks this run and
# the non-apply path exits with what it returns; nothing else decides the
# status of a -Check.
$windowsRoot = Split-Path -Parent $PSScriptRoot
$repositoryRoot = Split-Path -Parent $windowsRoot
$desiredStateRoot = Join-Path $windowsRoot 'desired'
Import-Module (Join-Path $windowsRoot 'src\WinEnv.psm1') -Force

$stateRoot = Join-Path $env:LOCALAPPDATA 'win-env'
$statePath = Join-Path $stateRoot 'state.json'
$backupRoot = Join-Path $stateRoot 'backups\original'
$mutex = $null
$powerToysWasRunning = $false
$powerToysRestarted = $false
$drift = [System.Collections.Generic.List[string]]::new()
$changed = [System.Collections.Generic.List[string]]::new()
# Sources this host has no parser for. Not drift and not a failure: Apply is a
# deployment, and refusing it because a validator is absent would make the
# missing tool look like broken desired state. They rank the same way the
# detections below do: with no drift, a source nobody here could parse makes
# the check unverified rather than verified (#54).
$unverified = [System.Collections.Generic.List[string]]::new()
# Detections this host could not decide, as opposed to sources it could not
# parse: the Appx module failing to load, which says nothing about whether the
# package is installed, and the terminal delegation's documented boundary
# when the host is below it or an observation it needs could not be made.
$unverifiedDetection = [System.Collections.Generic.List[string]]::new()
# CI sets this so the merge gate never accepts an undecided item; hooks and
# hosts leave it unset so a host that cannot decide one is not blocked.
$requireNative = ($env:REQUIRE_NATIVE -eq '1')
$selection = $null
$selected = @()
$unmanaged = @()
# A managed file may declare alternative sources chosen by the host's Windows
# build. The build is resolved once, reported in the summary, and never
# compared by major version: OSVersion.Version.Major is 10 on Windows 10 and
# Windows 11 alike. $null means the build could not be determined, which
# selects the variant every supported build honours.
$hostBuild = $null
$conditionalFiles = @()

function Test-Sources {
    param([array] $Definitions)
    foreach ($definition in $Definitions) {
        $reason = Test-WinEnvSourceFile -Definition $definition -RepositoryRoot $desiredStateRoot
        if ($reason -and -not $unverified.Contains("$($definition.Id): $reason")) {
            $unverified.Add("$($definition.Id): $reason")
        }
    }
}

function Write-Summary {
    param([string] $Mode)
    Write-Host "win-env $Mode summary"
    Write-Host ('  selected: ' + ($selected -join ', '))
    if ($selection -and $selection.Implied.Count) {
        Write-Host ('  added by dependency: ' + ($selection.Implied -join ', '))
    }
    if ($selection -and $selection.Excluded.Count) {
        Write-Host ('  not selected: ' + ($selection.Excluded -join ', '))
    }
    if ($unmanaged.Count) {
        Write-Warning ('  no longer managed: ' + ($unmanaged -join ', ') +
            ' (installed packages and deployed files were left in place; nothing was removed)')
    }
    if ($changed.Count) { Write-Host ('  changed: ' + ($changed -join ', ')) }
    if ($drift.Count) { Write-Warning ('  drift: ' + ($drift -join ', ')) }
    if ($unverified.Count) { Write-Host ('  unverified: ' + ($unverified -join ', ')) }
    if ($unverifiedDetection.Count) {
        Write-Host ('  unverified detection: ' + ($unverifiedDetection -join ', ') +
            ' (not decided on this host; neither present nor missing was concluded)')
    }
    if ($conditionalFiles.Count) {
        $build = if ($null -ne $hostBuild) { [string]$hostBuild } else { 'undetermined' }
        Write-Host ('  Windows build ' + $build + ': ' +
            (($conditionalFiles | ForEach-Object { "$($_.Id) from $($_.Source)" }) -join ', '))
    }
    # An undecided item is not a clean run, so it suppresses the clean line.
    if (-not $changed.Count -and -not $drift.Count -and -not $unverified.Count -and -not $unverifiedDetection.Count) {
        Write-Host '  no changes or drift detected'
    }
}

try {
    if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'setup.ps1 requires PowerShell 7 or newer.' }
    if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) { throw 'WinGet is required.' }

    $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')

    $mutex = Enter-WinEnvLock
    $state = Get-WinEnvState -Path $statePath
    $appliedFeatures = Get-WinEnvAppliedFeature -Manifest $manifest -State $state

    $requested = Get-WinEnvRequestedFeature -Manifest $manifest -Applied $appliedFeatures -HasState ([bool]$state) `
        -Feature $Feature -Add $Add -Minimal:$Minimal -All:$All

    $selection = Get-WinEnvFeatureSelection -Manifest $manifest -Requested $requested
    $selected = $selection.Selected
    # Deselection stops management; it never uninstalls a package or deletes a
    # deployed file. Removing what a previous Apply put on the host is a
    # separate, destructive operation this script does not perform.
    $unmanaged = @($appliedFeatures | Where-Object { $selected -notcontains $_ })

    $packages = @($manifest.Packages | Where-Object { $selected -contains [string]$_.Feature })
    # Resolved once, here and nowhere else: everything downstream keeps taking a
    # definition with a scalar Source, exactly as it did before a managed file
    # could declare alternatives.
    $hostBuild = Get-WinEnvWindowsBuild
    $conditionalIds = @($manifest.ManagedFiles |
            Where-Object { $_.ContainsKey('Sources') } |
            ForEach-Object { [string]$_.Id })
    $managedFiles = @($manifest.ManagedFiles |
            Where-Object { $selected -contains [string]$_.Feature } |
            ForEach-Object { Resolve-WinEnvManagedFile -Definition $_ -Build $hostBuild })
    $conditionalFiles = @($managedFiles | Where-Object { $conditionalIds -contains [string]$_.Id })
    $fontSelected = $selected -contains [string]$manifest.Font.Feature
    $terminalSelected = $selected -contains [string]$manifest.Terminal.Feature
    # PowerToys rewrites its own settings when it exits, so its files can only
    # be deployed while it is stopped. A host that did not select the feature
    # keeps its running PowerToys untouched.
    $managesPowerToys = @(
        $manifest.Features |
            Where-Object { $selected -contains [string]$_.Id -and $_.ContainsKey('Lifecycle') } |
            ForEach-Object { [string]$_.Lifecycle }) -contains 'PowerToys'

    $desiredStateHash = Get-WinEnvDesiredStateHash -Root $desiredStateRoot -Manifest $manifest -Feature $selected
    Test-Sources -Definitions $managedFiles

    $fontRegisteredAtUtc = if ($state -and $state.PSObject.Properties['fontRegisteredAtUtc']) {
        ([DateTimeOffset]$state.fontRegisteredAtUtc).ToString('o')
    }
    elseif ($state) {
        ([DateTimeOffset]$state.appliedAtUtc).ToString('o')
    }
    else {
        $null
    }
    $appliedVersion = if ($state) { [string]$state.projectVersion } else { '0.0.0' }
    $appliedDesiredStateHash = if ($state -and $state.PSObject.Properties['bundleHash']) {
        [string]$state.bundleHash
    }
    else {
        ''
    }
    $comparison = Compare-WinEnvVersion -RepositoryVersion $manifest.ProjectVersion -AppliedVersion $appliedVersion
    $desiredStateChanged = $appliedDesiredStateHash -ne $desiredStateHash
    $featureSetChanged = (($appliedFeatures | Sort-Object) -join ',') -ne (($selected | Sort-Object) -join ',')
    $shouldApply = -not $Check -and ($Force -or -not $state -or $comparison -gt 0 -or $desiredStateChanged -or $featureSetChanged)

    if (-not $state) { $drift.Add('state missing') }
    elseif ($comparison -lt 0) { Write-Warning "Repository version $($manifest.ProjectVersion) is lower than applied version $appliedVersion; downgrade is disabled." }
    else {
        if ($featureSetChanged) { $drift.Add('feature selection changed') }
        if ($desiredStateChanged) { $drift.Add('desired state changed') }
    }

    $packageStatuses = @()
    foreach ($package in $packages) {
        $status = Get-WinEnvPackageStatus -Package $package
        $packageStatuses += $status
        Write-Verbose "$($status.Id): registered=$($status.Registered), detected=$($status.Detected)"
        if ($status.Unverified) { $unverifiedDetection.Add("$($status.Id): $($status.Unverified)") }
        if ($status.Conflict) { $drift.Add("$($status.Id) detection conflict") }
        elseif ($status.Missing) { $drift.Add("$($status.Id) missing") }
    }

    $fontStatus = $null
    if ($fontSelected) {
        $fontStatus = Get-WinEnvFontStatus -Font $manifest.Font
        if ($fontStatus.Conflict) { $drift.Add('D2Koding font partial/conflicting installation') }
        elseif ($fontStatus.Incomplete) {
            # Named apart from a conflict on purpose: this host has nothing
            # wrong on it, the manifest simply lists faces it has not installed
            # yet, and Apply installs them.
            $drift.Add("D2Koding font incomplete: $($fontStatus.InstalledFaceCount) of $($fontStatus.FaceCount) faces installed")
        }
        elseif ($fontStatus.RegistrationRepairable) { $drift.Add('D2Koding font registration') }
        elseif ($fontStatus.Missing) { $drift.Add('D2Koding font missing') }
        elseif (-not (Test-WinEnvWindowsTerminalFontCache -FontRegisteredAtUtc $fontRegisteredAtUtc)) {
            $drift.Add('Windows Terminal restart required for D2Koding')
        }
    }

    # A precondition belongs to the feature that needs it. An unselected
    # feature must not make this host look broken.
    $preconditionFailures = [System.Collections.Generic.List[string]]::new()
    foreach ($feature in $manifest.Features) {
        if ($selected -notcontains [string]$feature.Id) { continue }
        $preconditionResult = Test-WinEnvFeaturePrecondition -Feature $feature
        foreach ($failure in $preconditionResult.Failures) {
            $preconditionFailures.Add("$($feature.Id): $failure")
            $drift.Add("$($feature.Id) precondition: $failure")
        }
        # An undecidable precondition is not a failed one. Blocking Apply on it
        # would make a host that cannot ask the question look like a host that
        # answered no.
        foreach ($item in $preconditionResult.Unverified) {
            $unverifiedDetection.Add("$($feature.Id) precondition: $item")
        }
    }

    foreach ($definition in $managedFiles) {
        if (-not (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot)) {
            $drift.Add("$($definition.Id) settings")
        }
    }
    $hostProfile = Get-WinEnvPowerShellProfilePath
    if (-not (Test-WinEnvProfileHook -ProfilePath $hostProfile)) { $drift.Add('PowerShell profile hook') }
    if ($terminalSelected) {
        # INV windows/support-boundary-named — decided against the documented
        # condition, not the write: a read-back the host accepts below the
        # boundary is undecided, never verified. A mismatch is drift on either
        # side, because Apply writes the values regardless.
        $delegation = Test-WinEnvTerminalDelegation -Terminal $manifest.Terminal -Build $hostBuild
        if (-not $delegation.Matches) { $drift.Add('default terminal delegation') }
        if ($delegation.Unverified) { $unverifiedDetection.Add("default terminal delegation: $($delegation.Unverified)") }
    }

    # One place decides what this run's status is, so Apply and the check rank
    # drift, undecided items, and REQUIRE_NATIVE the same way. Everything that
    # can drift or go undecided has been collected by here.
    $runStatus = Get-WinEnvCheckStatus -DriftCount $drift.Count -UnverifiedCount ($unverified.Count + $unverifiedDetection.Count) -RequireNative:$requireNative
    $mode = if ($Check) { 'check' } else { 'verification' }
    if ($runStatus -eq 1) {
        # The summary comes first on the one path where completeness is the
        # point: the operator loses the selection and the drift list otherwise.
        Write-Summary -Mode $mode
        throw ('Detection could not be completed on this host and REQUIRE_NATIVE is set: ' +
            (@($unverified) + @($unverifiedDetection) -join '; ') + '.')
    }

    if (-not $shouldApply) {
        Write-Summary -Mode $mode
        exit $runStatus
    }

    if ($packageStatuses.Conflict -contains $true) { throw 'Package detection conflicts must be resolved before applying.' }
    if ($fontSelected -and $fontStatus.Conflict) { throw 'The D2Koding font is partially installed; automatic overwrite is disabled.' }
    if ($preconditionFailures.Count) { throw "Selected features are not ready to apply: $($preconditionFailures -join '; ')." }

    foreach ($package in $packages) {
        $status = $packageStatuses | Where-Object Id -eq $package.Id
        if ($status.Missing) {
            Install-WinEnvPackage -Package $package
            $changed.Add($package.Id)
        }
    }
    Update-WinEnvProcessPath

    if ($fontSelected) {
        if ($fontStatus.Missing) {
            Install-WinEnvFont -Font $manifest.Font
            $fontRegisteredAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
            $changed.Add('D2Koding font')
        }
        elseif ($fontStatus.Incomplete) {
            # The same installer: it fetches the pinned archive, leaves every
            # face this host already holds byte for byte alone, and writes and
            # registers the rest.
            Install-WinEnvFont -Font $manifest.Font
            $fontRegisteredAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
            $changed.Add('D2Koding font (missing faces)')
        }
        elseif ($fontStatus.RegistrationRepairable) {
            Register-WinEnvFont -Font $manifest.Font
            $fontRegisteredAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
            $changed.Add('D2Koding font registration')
        }
    }

    if ($managesPowerToys) { $powerToysWasRunning = Stop-WinEnvPowerToys }
    foreach ($definition in $managedFiles) {
        $target = Resolve-WinEnvPath $definition.Target
        Backup-WinEnvFile -Id $definition.Id -Target $target -BackupRoot $backupRoot
        Set-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot
        $changed.Add($definition.Id)
    }

    Backup-WinEnvFile -Id 'HostPowerShellProfile' -Target $hostProfile -BackupRoot $backupRoot
    Set-WinEnvProfileHook -ProfilePath $hostProfile
    if ($terminalSelected) { Set-WinEnvTerminalDelegation -Terminal $manifest.Terminal }
    if ($powerToysWasRunning) {
        Start-WinEnvPowerToys
        $powerToysRestarted = $true
    }

    $drift.Clear()
    foreach ($package in $packages) {
        $status = Get-WinEnvPackageStatus -Package $package
        if ($status.Missing -or $status.Conflict) { $drift.Add($package.Id) }
    }
    if ($fontSelected) {
        $fontStatus = Get-WinEnvFontStatus -Font $manifest.Font
        if (-not $fontStatus.Installed) { $drift.Add('D2Koding font') }
    }
    Test-Sources -Definitions $managedFiles
    foreach ($definition in $managedFiles) {
        if (-not (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot)) { $drift.Add($definition.Id) }
    }
    if (-not (Test-WinEnvProfileHook -ProfilePath $hostProfile)) { $drift.Add('PowerShell profile hook') }
    if ($terminalSelected -and -not (Test-WinEnvTerminalDelegation -Terminal $manifest.Terminal -Build $hostBuild).Matches) {
        $drift.Add('default terminal delegation')
    }
    if ($drift.Count) { throw "Post-apply validation failed: $($drift -join ', ')" }

    $commit = Get-WinEnvGitCommit -RepositoryRoot $repositoryRoot
    Write-WinEnvState -Path $statePath -ProjectVersion $manifest.ProjectVersion -GitCommit $commit -DesiredStateHash $desiredStateHash -Feature $selected -FontRegisteredAtUtc $fontRegisteredAtUtc
    if ($fontSelected -and -not (Test-WinEnvWindowsTerminalFontCache -FontRegisteredAtUtc $fontRegisteredAtUtc)) {
        Write-Warning 'Close every Windows Terminal window and start it again so its per-process font cache can load D2Koding.'
    }
    Write-Summary -Mode 'apply'
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
finally {
    if ($powerToysWasRunning -and -not $powerToysRestarted) {
        try { Start-WinEnvPowerToys } catch { Write-Warning "PowerToys could not be restarted after failure: $($_.Exception.Message)" }
    }
    if ($mutex) { Exit-WinEnvLock -Mutex $mutex }
}
