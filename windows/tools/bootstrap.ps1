<#
.SYNOPSIS
Checks prerequisites and starts the PowerShell 7 desired-state runner.

.DESCRIPTION
bootstrap.ps1 is the Windows PowerShell 5.1-compatible bridge to setup.ps1.
With -Check it performs no installation and reports a missing WinGet or
PowerShell 7 prerequisite as unverified. Without -Check it requires WinGet,
installs PowerShell 7 when missing, and forwards the selected operation to
setup.ps1.

Choose at most one of -Feature, -Add, -Minimal, and -All. With no selector, an
already-applied host keeps its recorded selection and a new host selects every
declared feature. Feature dependencies and the required core feature are added
by setup.ps1.

.PARAMETER Check
Performs a read-only desired-state check. It cannot be combined with -Force.

.PARAMETER Force
Runs deployment even when version, hash, and selection gates would otherwise
skip it. It does not bypass selection conflicts, prerequisite failures, package
detection conflicts, feature preconditions, or font safety checks. It cannot
be combined with -Check.

.PARAMETER Feature
Replaces the host selection with the named feature IDs. Comma-separated values
or a PowerShell string array are accepted.

.PARAMETER Add
Adds the named feature IDs to the selection recorded on this host.

.PARAMETER Minimal
Selects only required features, currently core.

.PARAMETER All
Selects every feature declared by the manifest.

.EXAMPLE
PS> .\windows\tools\bootstrap.ps1 -Check -Feature terminal

Read-only. Checks terminal plus its required font, zellij, and core features.

.EXAMPLE
PS> $env:REQUIRE_NATIVE = '1'; .\windows\tools\bootstrap.ps1 -Check

Read-only. Treats evidence that this host cannot obtain as failure instead of
exit 69. Remove the environment variable when that policy is no longer wanted.

.EXAMPLE
PS> .\windows\tools\bootstrap.ps1 -Add wezterm

Changes the host. Installs PowerShell 7 if necessary and adds WezTerm plus its
dependencies to the recorded selection.

.NOTES
WinGet is required. Under -Check, exit 0 means converged, 2 means drift, 69
means unverified, and 1 means failure; drift outranks unverified evidence.
REQUIRE_NATIVE=1 changes an otherwise-unverified prerequisite or result into
exit 1. Without -Check, a missing PowerShell 7 may be installed and successful
deployment exits 0. See setup.ps1 for the complete deployment behavior.

.LINK
https://github.com/shk95/configs/blob/dev/README.md#windows

.LINK
https://github.com/shk95/configs/blob/dev/CONTRIBUTING.md#windows-changes
#>
[CmdletBinding(DefaultParameterSetName = 'Default')]
param(
    [Parameter(ParameterSetName = 'Check')]
    [switch] $Check,

    [Parameter(ParameterSetName = 'Force')]
    [switch] $Force,

    # Feature selection is resolved by setup.ps1; this script only forwards
    # it, so a host cannot be told one thing here and another there.
    [string[]] $Feature,
    [string[]] $Add,
    [switch] $Minimal,
    [switch] $All
)

$ErrorActionPreference = 'Stop'
$setupPath = Join-Path $PSScriptRoot 'setup.ps1'

# INV windows/check-exit-contract — a prerequisite this host lacks is reported
# under -Check as unverified (69), or as a failure (1) when REQUIRE_NATIVE asks
# for native evidence; -Check never installs anything, so it can only report.
# Without -Check a missing WinGet is the failure it always was, and a missing
# pwsh is installed below.
$requireNative = $env:REQUIRE_NATIVE -eq '1'
function Exit-Unverified {
    param([string] $Message)
    if ($requireNative) {
        [Console]::Error.WriteLine("$Message REQUIRE_NATIVE is set, so this counts as a failure.")
        exit 1
    }
    Write-Host "unverified: $Message"
    exit 69
}

if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
    if ($Check) { Exit-Unverified 'WinGet is missing; -Check never installs prerequisites.' }
    Write-Error 'WinGet is required. Install or repair Microsoft App Installer first.'
    exit 1
}

$pwsh = Get-Command pwsh.exe -ErrorAction SilentlyContinue
if (-not $pwsh) {
    if ($Check) { Exit-Unverified 'PowerShell 7 is missing; -Check never installs prerequisites.' }

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
