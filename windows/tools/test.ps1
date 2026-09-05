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
        "Install the contributor toolchain with: .\windows\win-env.ps1 setup-dev"

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

# Every script below windows/ must parse before the suite runs. The suite
# imports the module and drives the entry points, but the end-to-end capture
# cases are skipped without WIN_ENV_E2E, so a syntax error in capture.ps1
# would otherwise reach CI unseen. This step sits after the Pester gate so a
# host without Pester still exits 69 rather than reporting a parse result as
# the suite's; a parse error is a failure of the tools, exit 1.
$parseErrors = @(Get-ChildItem -Path $windowsRoot -Recurse -File |
    Where-Object { $_.Extension -in '.ps1', '.psm1' } |
    ForEach-Object {
        $tokens = $null
        $errors = $null
        [void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$errors)
        if ($errors.Count) { "$($_.FullName): $($errors[0].Message)" }
    })
if ($parseErrors.Count) {
    $parseErrors | ForEach-Object { [Console]::Error.WriteLine("✗ $_") }
    exit 1
}

$tests = Join-Path (Split-Path -Parent $PSScriptRoot) 'tests'
$result = Invoke-Pester -Path $tests -PassThru
if ($result.Result -ne 'Passed') { exit 1 }
# Explicit, because win-env.ps1 runs this in-process and returns
# $LASTEXITCODE, which a script that falls off its end leaves at whatever its
# last native call set. Nothing above sets it (Pester keeps its cases' child
# processes out of this scope), so this makes the status deterministic rather
# than incidental; the entry point's fixture holds every target to a final exit.
exit 0
