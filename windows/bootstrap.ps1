[CmdletBinding(DefaultParameterSetName = 'Default')]
param(
    [Parameter(ParameterSetName = 'Check')]
    [switch] $Check,

    [Parameter(ParameterSetName = 'Force')]
    [switch] $Force,

    # Feature selection is resolved by setup.ps1; this entry point only forwards
    # it, so a host cannot be told one thing here and another there.
    [string[]] $Feature,
    [string[]] $Add,
    [switch] $Minimal,
    [switch] $All
)

$ErrorActionPreference = 'Stop'
$setupPath = Join-Path $PSScriptRoot 'setup.ps1'

if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
    Write-Error 'WinGet is required. Install or repair Microsoft App Installer first.'
    exit 1
}

$pwsh = Get-Command pwsh.exe -ErrorAction SilentlyContinue
if (-not $pwsh) {
    if ($Check) {
        Write-Warning 'PowerShell 7 is missing. -Check never installs prerequisites.'
        exit 2
    }

    & winget.exe install --id Microsoft.PowerShell --exact --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity
    if ($LASTEXITCODE -ne 0) {
        Write-Error "PowerShell 7 installation failed with exit code $LASTEXITCODE."
        exit 1
    }

    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machinePath;$userPath"
    $pwsh = Get-Command pwsh.exe -ErrorAction SilentlyContinue
    if (-not $pwsh) {
        $candidate = Join-Path $env:ProgramFiles 'PowerShell\7\pwsh.exe'
        if (Test-Path -LiteralPath $candidate) { $pwsh = Get-Item -LiteralPath $candidate }
    }
}

if (-not $pwsh) {
    Write-Error 'PowerShell 7 was installed but pwsh.exe could not be resolved.'
    exit 1
}

# pwsh -File takes literal strings, so the list values are joined here and split
# again in setup.ps1 rather than relying on how -File binds an array parameter.
$arguments = @('-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $setupPath)
if ($Check) { $arguments += '-Check' }
if ($Force) { $arguments += '-Force' }
if ($Minimal) { $arguments += '-Minimal' }
if ($All) { $arguments += '-All' }
if ($PSBoundParameters.ContainsKey('Feature')) { $arguments += @('-Feature', ($Feature -join ',')) }
if ($PSBoundParameters.ContainsKey('Add')) { $arguments += @('-Add', ($Add -join ',')) }
if ($VerbosePreference -ne 'SilentlyContinue') { $arguments += '-Verbose' }

$pwshPath = if ($pwsh.PSObject.Properties['Source']) { $pwsh.Source } else { $pwsh.FullName }
& $pwshPath @arguments
$setupExitCode = $LASTEXITCODE
exit $setupExitCode
