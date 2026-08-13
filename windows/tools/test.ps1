[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$requiredVersion = [version]'5.7.1'
$module = Get-Module Pester -ListAvailable |
    Where-Object Version -eq $requiredVersion |
    Select-Object -First 1

if (-not $module) {
    throw "Pester $requiredVersion is required. Install it with: Install-Module Pester -RequiredVersion $requiredVersion -Scope CurrentUser"
}

Import-Module -FullyQualifiedName @{
    ModuleName      = 'Pester'
    RequiredVersion = $requiredVersion
} -Force

$tests = Join-Path (Split-Path -Parent $PSScriptRoot) 'tests'
$result = Invoke-Pester -Path $tests -PassThru
if ($result.Result -ne 'Passed') { exit 1 }
