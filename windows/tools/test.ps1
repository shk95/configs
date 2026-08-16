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
$requiredVersion = [version]'5.7.1'
$requireNative = $RequireNativeTooling.IsPresent -or ($env:REQUIRE_NATIVE -eq '1')

$module = Get-Module Pester -ListAvailable |
    Where-Object Version -eq $requiredVersion |
    Select-Object -First 1

if (-not $module) {
    $message = "Pester $requiredVersion is not installed. Install it with: " +
        "Install-Module Pester -RequiredVersion $requiredVersion -Scope CurrentUser"

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

$tests = Join-Path (Split-Path -Parent $PSScriptRoot) 'tests'
$result = Invoke-Pester -Path $tests -PassThru
if ($result.Result -ne 'Passed') { exit 1 }
