[CmdletBinding()]
param(
    # CI passes this, as does the REQUIRE_NATIVE variable, so a runner that
    # somehow lacks Pester fails rather than reporting an untested suite.
    [switch] $RequireNativeTooling
)

# A missing Pester is a host that cannot run this suite, not a suite that
# failed. Throwing here blocked pushes from Windows clones that had never
# installed it, and named a cause the message did not distinguish from a real
# test failure.

$ErrorActionPreference = 'Stop'
$windowsRoot = Split-Path -Parent $PSScriptRoot
$requireNative = $RequireNativeTooling.IsPresent -or ($env:REQUIRE_NATIVE -eq '1')

# The version lives in windows/toolchain.json so local verification and CI
# cannot drift apart. It was written out twice before, here and in the
# workflow, with nothing keeping them equal.
$toolchain = (Get-Content -LiteralPath (Join-Path $windowsRoot 'toolchain.json') -Raw |
        ConvertFrom-Json).toolchain
$requiredVersion = [version]($toolchain | Where-Object Id -eq 'Pester').Version

$module = Get-Module Pester -ListAvailable |
    Where-Object Version -eq $requiredVersion |
    Select-Object -First 1

if (-not $module) {
    $message = "Pester $requiredVersion is not installed. " +
        "Install the contributor toolchain with: .\windows\tools\setup-dev.ps1"

    if ($requireNative) {
        [Console]::Error.WriteLine($message)
        exit 1
    }

    Write-Host "· unverified: $message"
    exit 69
}

Import-Module -FullyQualifiedName @{
    ModuleName      = 'Pester'
    RequiredVersion = $requiredVersion
} -Force

# The suite creates fixture repositories; it must never inherit the caller's.
. (Join-Path $PSScriptRoot 'isolate-git.ps1')

$tests = Join-Path (Split-Path -Parent $PSScriptRoot) 'tests'
$result = Invoke-Pester -Path $tests -PassThru
if ($result.Result -ne 'Passed') { exit 1 }
