[CmdletBinding(DefaultParameterSetName = 'Default')]
param(
    [Parameter(ParameterSetName = 'Check')]
    [switch] $Check,

    [Parameter(ParameterSetName = 'Force')]
    [switch] $Force
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
    if ($changed.Count) { Write-Host ('  changed: ' + ($changed -join ', ')) }
    if ($drift.Count) { Write-Warning ('  drift: ' + ($drift -join ', ')) }
    if ($unverified.Count) { Write-Host ('  unverified: ' + ($unverified -join ', ')) }
    if (-not $changed.Count -and -not $drift.Count) { Write-Host '  no changes or drift detected' }
}

try {
    if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'setup.ps1 requires PowerShell 7 or newer.' }
    if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) { throw 'WinGet is required.' }

    $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
    $desiredStateHash = Get-WinEnvDesiredStateHash -Root $desiredStateRoot
    Test-Sources -Definitions $manifest.ManagedFiles

    $mutex = Enter-WinEnvLock
    $state = Get-WinEnvState -Path $statePath
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
    $shouldApply = -not $Check -and ($Force -or -not $state -or $comparison -gt 0 -or $desiredStateChanged)

    if (-not $state) { $drift.Add('state missing') }
    elseif ($comparison -lt 0) { Write-Warning "Repository version $($manifest.ProjectVersion) is lower than applied version $appliedVersion; downgrade is disabled." }
    elseif ($desiredStateChanged) { $drift.Add('desired state changed') }

    $packageStatuses = @()
    foreach ($package in $manifest.Packages) {
        $status = Get-WinEnvPackageStatus -Package $package
        $packageStatuses += $status
        Write-Verbose "$($status.Id): registered=$($status.Registered), detected=$($status.Detected)"
        if ($status.Conflict) { $drift.Add("$($status.Id) detection conflict") }
        elseif ($status.Missing) { $drift.Add("$($status.Id) missing") }
    }

    $fontStatus = Get-WinEnvFontStatus -Font $manifest.Font
    if ($fontStatus.Conflict) { $drift.Add('D2Koding font partial/conflicting installation') }
    elseif ($fontStatus.RegistrationRepairable) { $drift.Add('D2Koding font registration') }
    elseif ($fontStatus.Missing) { $drift.Add('D2Koding font missing') }
    elseif (-not (Test-WinEnvWindowsTerminalFontCache -FontRegisteredAtUtc $fontRegisteredAtUtc)) {
        $drift.Add('Windows Terminal restart required for D2Koding')
    }

    $commandPaletteInstalled = [bool](Get-AppxPackage -Name Microsoft.CommandPalette -ErrorAction SilentlyContinue)
    if (-not $commandPaletteInstalled) { $drift.Add('Microsoft.CommandPalette Appx missing') }

    foreach ($definition in $manifest.ManagedFiles) {
        if (-not (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot)) {
            $drift.Add("$($definition.Id) settings")
        }
    }
    $hostProfile = Get-WinEnvPowerShellProfilePath
    if (-not (Test-WinEnvProfileHook -ProfilePath $hostProfile)) { $drift.Add('PowerShell profile hook') }
    if (-not (Test-WinEnvTerminalDelegation -Terminal $manifest.Terminal)) { $drift.Add('default terminal delegation') }

    if (-not $shouldApply) {
        $mode = if ($Check) { 'check' } else { 'verification' }
        Write-Summary -Mode $mode
        if ($drift.Count) { exit 2 }
        exit 0
    }

    if ($packageStatuses.Conflict -contains $true) { throw 'Package detection conflicts must be resolved before applying.' }
    if ($fontStatus.Conflict) { throw 'The D2Koding font is partially installed; automatic overwrite is disabled.' }
    if (-not $commandPaletteInstalled) { throw 'PowerToys Command Palette Appx is missing; update or repair PowerToys before applying.' }

    foreach ($package in $manifest.Packages) {
        $status = $packageStatuses | Where-Object Id -eq $package.Id
        if ($status.Missing) {
            Install-WinEnvPackage -Package $package
            $changed.Add($package.Id)
        }
    }
    Update-WinEnvProcessPath

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

    $powerToysWasRunning = Stop-WinEnvPowerToys
    foreach ($definition in $manifest.ManagedFiles) {
        $target = Resolve-WinEnvPath $definition.Target
        Backup-WinEnvFile -Id $definition.Id -Target $target -BackupRoot $backupRoot
        Set-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot
        $changed.Add($definition.Id)
    }

    Backup-WinEnvFile -Id 'HostPowerShellProfile' -Target $hostProfile -BackupRoot $backupRoot
    Set-WinEnvProfileHook -ProfilePath $hostProfile
    Set-WinEnvTerminalDelegation -Terminal $manifest.Terminal
    if ($powerToysWasRunning) {
        Start-WinEnvPowerToys
        $powerToysRestarted = $true
    }

    $drift.Clear()
    foreach ($package in $manifest.Packages) {
        $status = Get-WinEnvPackageStatus -Package $package
        if ($status.Missing -or $status.Conflict) { $drift.Add($package.Id) }
    }
    $fontStatus = Get-WinEnvFontStatus -Font $manifest.Font
    if (-not $fontStatus.Installed) { $drift.Add('D2Koding font') }
    Test-Sources -Definitions $manifest.ManagedFiles
    foreach ($definition in $manifest.ManagedFiles) {
        if (-not (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot)) { $drift.Add($definition.Id) }
    }
    if (-not (Test-WinEnvProfileHook -ProfilePath $hostProfile)) { $drift.Add('PowerShell profile hook') }
    if (-not (Test-WinEnvTerminalDelegation -Terminal $manifest.Terminal)) { $drift.Add('default terminal delegation') }
    if ($drift.Count) { throw "Post-apply validation failed: $($drift -join ', ')" }

    $commit = Get-WinEnvGitCommit -RepositoryRoot $repositoryRoot
    Write-WinEnvState -Path $statePath -ProjectVersion $manifest.ProjectVersion -GitCommit $commit -DesiredStateHash $desiredStateHash -FontRegisteredAtUtc $fontRegisteredAtUtc
    if (-not (Test-WinEnvWindowsTerminalFontCache -FontRegisteredAtUtc $fontRegisteredAtUtc)) {
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
