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
$windowsRoot = $PSScriptRoot
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
# missing tool look like broken desired state.
$unverified = [System.Collections.Generic.List[string]]::new()
$selection = $null
$selected = @()
$unmanaged = @()

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
    if (-not $changed.Count -and -not $drift.Count) { Write-Host '  no changes or drift detected' }
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
    $managedFiles = @($manifest.ManagedFiles | Where-Object { $selected -contains [string]$_.Feature })
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
        if ($status.Conflict) { $drift.Add("$($status.Id) detection conflict") }
        elseif ($status.Missing) { $drift.Add("$($status.Id) missing") }
    }

    $fontStatus = $null
    if ($fontSelected) {
        $fontStatus = Get-WinEnvFontStatus -Font $manifest.Font
        if ($fontStatus.Conflict) { $drift.Add('D2Koding font partial/conflicting installation') }
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
        foreach ($failure in (Test-WinEnvFeaturePrecondition -Feature $feature)) {
            $preconditionFailures.Add("$($feature.Id): $failure")
            $drift.Add("$($feature.Id) precondition: $failure")
        }
    }

    foreach ($definition in $managedFiles) {
        if (-not (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot)) {
            $drift.Add("$($definition.Id) settings")
        }
    }
    $hostProfile = Get-WinEnvPowerShellProfilePath
    if (-not (Test-WinEnvProfileHook -ProfilePath $hostProfile)) { $drift.Add('PowerShell profile hook') }
    if ($terminalSelected -and -not (Test-WinEnvTerminalDelegation -Terminal $manifest.Terminal)) {
        $drift.Add('default terminal delegation')
    }

    if (-not $shouldApply) {
        $mode = if ($Check) { 'check' } else { 'verification' }
        Write-Summary -Mode $mode
        if ($drift.Count) { exit 2 }
        exit 0
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
    if ($terminalSelected -and -not (Test-WinEnvTerminalDelegation -Terminal $manifest.Terminal)) {
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
