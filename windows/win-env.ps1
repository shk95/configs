<#
.SYNOPSIS
Runs one public Windows environment command.

.DESCRIPTION
This is the single entry point for the Windows domain. The first positional
argument selects a target script and every remaining argument is forwarded to
that script unchanged. Use the help verb to list the targets, then use
Get-Help on the target script for its parameters and examples.

The check, validate, test, font, and help verbs do not apply desired state.
The apply verb can install packages and write managed host files. The capture
verb can write repository payloads and create commits after confirmation. The
setup-dev verb installs contributor tooling.

.PARAMETER Command
One of check, apply, capture, validate, test, setup-dev, font, or help. A
missing or unknown command exits 64.

.EXAMPLE
PS> .\windows\win-env.ps1 help

Lists every verb and the Get-Help commands for detailed documentation.

.EXAMPLE
PS> .\windows\win-env.ps1 check -Feature terminal

Read-only. Checks the terminal selection and its dependencies. The target
status is returned unchanged: 0 converged, 2 drift, 69 unverified, or 1 failed.

.EXAMPLE
PS> .\windows\win-env.ps1 apply -Feature terminal

Changes the host. Runs bootstrap.ps1, which can install PowerShell 7, and then
deploys the terminal selection after its checks pass.

.NOTES
The entry point runs under Windows PowerShell 5.1 as well as PowerShell 7 so a
new host can bootstrap PowerShell 7. It does not implement target-specific
policy and it never turns check status 2 into a generic failure.

.LINK
https://github.com/shk95/configs/blob/dev/README.md#windows

.LINK
https://github.com/shk95/configs/blob/dev/CONTRIBUTING.md#windows-changes
#>
# win-env: the Windows domain's one entry point.
#
# Every verb runs exactly one script under tools\ and returns that script's
# exit status unchanged, so the check contract -- 0 converged, 2 drifted,
# 69 unverified, 1 failed -- reaches the operator through this file exactly
# as it does through the script. The verb table below is the whole policy
# this file holds: what -Check means, which selections are valid, when Apply
# may run and what capture refuses are decided by the scripts it forwards
# to, never here.
#
# No [CmdletBinding()], on purpose: an argument this file does not declare
# then lands in $args and is splatted onto the target, so `check -Feature
# terminal` reaches bootstrap.ps1 as `-Check -Feature terminal` and
# bootstrap's own parameter sets refuse `check -Force`. The fixed arguments
# a verb adds are a hashtable, because an array splat hands '-Check' over as
# a positional value rather than a parameter name. No #Requires either:
# `apply` has to run under Windows PowerShell 5.1 on a host with no pwsh 7
# yet, which is what bootstrap.ps1 installs; capture.ps1 carries its own
# version requirement and refuses for itself.
#
# The target runs in this process, so the status handed back is
# $LASTEXITCODE, which a script that falls off its end leaves at whatever
# its last child process set. Every script the table names therefore ends
# in an explicit exit, and the suite holds it there.
#
# The usage status is 64 (EX_USAGE) rather than 2, because 2 is drift and 69
# is already EX_UNAVAILABLE: a caller must never read "no such verb" as a
# check outcome.
#
# INV windows/entry-point-forwards-status
param([string] $Command)

$ErrorActionPreference = 'Stop'
$toolsRoot = Join-Path $PSScriptRoot 'tools'

$verbs = [ordered]@{
    'check'     = @{ Script = 'bootstrap.ps1'; Arguments = @{ Check = $true }; Summary = 'read-only: is an Apply needed; exits 0 converged, 2 drift, 69 unverified' }
    'apply'     = @{ Script = 'bootstrap.ps1'; Arguments = @{}; Summary = 'deploy the selection; explicit request only' }
    'capture'   = @{ Script = 'capture.ps1'; Arguments = @{}; Summary = 'move a change made in an application into desired state' }
    'validate'  = @{ Script = 'check-desired-state.ps1'; Arguments = @{}; Summary = 'parse every declared payload' }
    'test'      = @{ Script = 'test.ps1'; Arguments = @{}; Summary = 'run the Pester suite' }
    'setup-dev' = @{ Script = 'setup-dev.ps1'; Arguments = @{}; Summary = 'install the contributor toolchain' }
    'font'      = @{ Script = 'Test-FontRendering.ps1'; Arguments = @{}; Summary = 'print the glyph check for the terminal font' }
}

function Get-Usage {
    $lines = @('usage: win-env.ps1 <verb> [arguments for the script]', '')
    foreach ($name in $verbs.Keys) {
        $verb = $verbs[$name]
        $fixed = @($verb.Arguments.Keys | ForEach-Object { '-' + $_ })
        $target = 'tools\' + $verb.Script
        if ($fixed.Count) { $target += ' ' + ($fixed -join ' ') }
        $lines += ('  {0,-10} {1,-36} {2}' -f $name, $target, $verb.Summary)
    }
    $lines += ('  {0,-10} {1,-36} {2}' -f 'help', '', 'print this text')
    $lines += ''
    $lines += 'Arguments after the verb reach the script unchanged, for example:'
    $lines += '  win-env.ps1 check -Feature terminal'
    $lines += '  win-env.ps1 capture -Feature powertoys -Publish'
    $lines += ''
    $lines += 'Detailed help (these commands do not run the target script):'
    $lines += '  Get-Help .\windows\win-env.ps1 -Detailed'
    $lines += '  Get-Help .\windows\tools\bootstrap.ps1 -Full'
    $lines += '  Get-Help .\windows\tools\capture.ps1 -Examples'
    return ($lines -join [Environment]::NewLine)
}

if ($Command -eq 'help') {
    Write-Output (Get-Usage)
    exit 0
}

if (-not $Command) {
    [Console]::Error.WriteLine((Get-Usage))
    exit 64
}

if (-not $verbs.Contains($Command)) {
    [Console]::Error.WriteLine("win-env: unknown verb '$Command'")
    [Console]::Error.WriteLine((Get-Usage))
    exit 64
}

$verb = $verbs[$Command]
$scriptPath = Join-Path $toolsRoot $verb.Script
$fixed = $verb.Arguments

$global:LASTEXITCODE = 0
try {
    & $scriptPath @fixed @args
}
catch {
    [Console]::Error.WriteLine("win-env $Command`: $($_.Exception.Message)")
    exit 1
}
exit $LASTEXITCODE
