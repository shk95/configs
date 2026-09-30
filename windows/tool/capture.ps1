<#
.SYNOPSIS
Previews or explicitly saves supported app settings into host originals.
.DESCRIPTION
An explicit clean provider clone and version1 host environment choose selected,
enabled units. Default capture prints the host document/connection preview as
JSON and changes no original. Save writes host originals only, never provider
payloads, Git history, generated output or app settings. Every requested unit
prepares before saving; first documents are saved before their connection, so a
connection failure reports an inert document to inspect on explicit retry.
.PARAMETER SourceRoot
Exact clean local provider clone named by Environment.provider.commit.
.PARAMETER Environment
Existing version1 host declaration outside the provider/generated tree.
.PARAMETER Unit
Case-sensitive selected/enabled managed unit IDs to capture explicitly.
.PARAMETER Document
Relative first-document paths, aligned with Unit IDs when supplied. An existing
connection can be omitted or supplied unchanged, never renamed by capture.
.PARAMETER Save
Explicitly save the previewed host documents and connections. WhatIf keeps the
same prepared preview and writes no original.
.EXAMPLE
pwsh -NoProfile -File windows/win-env.ps1 capture -SourceRoot C:\provider -Environment C:\host\environment.json -Unit advancedPaste -Document settings/paste.json
.EXAMPLE
pwsh -NoProfile -File windows/win-env.ps1 capture -SourceRoot C:\provider -Environment C:\host\environment.json -Unit advancedPaste -Document settings/paste.json -Save
.NOTES
Legacy Feature/Id/Branch/Publish arguments are unsupported. Export selection and
write an explicit host declaration before capture. Publication is independently
owned by the host repository, never performed by this command. No Apply occurs.
#>
#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess)]
param([string] $SourceRoot, [string] $Environment, [string[]] $Unit, [string[]] $Document=@(), [switch] $Save)
$ErrorActionPreference='Stop'
Import-Module (Join-Path (Split-Path -Parent $PSScriptRoot) 'src/WinEnvCapture.psm1') -Force
Import-Module (Join-Path (Split-Path -Parent $PSScriptRoot) 'src/WinEnv.psm1')
try {
    if (-not $SourceRoot -or -not $Environment -or -not $Unit.Count) {
        [Console]::Error.WriteLine('capture requires SourceRoot, Environment and explicit Unit; use Document for first connections. Legacy publication is removed.')
        exit 64
    }
    if (-not (Test-WinEnvWindowsHost)) { throw 'capture.ps1 only runs on Windows.' }
    $plan = Get-WinEnvHostCapturePlan -SourceRoot $SourceRoot -Environment $Environment -Unit $Unit -Document $Document
    if ($Save) { $plan = Save-WinEnvHostCapture -Plan $plan -WhatIf:$WhatIfPreference }
    ConvertTo-WinEnvHostCapturePreview $plan | ConvertTo-Json -Depth 100
    if (@($plan.Units | Where-Object { $_.Status -in @('refused','failed','unconnected','pending') }).Count) {
        if (@($plan.Units | Where-Object { $_.Status -eq 'refused' -and -not $_.Unavailable }).Count -or
            @($plan.Units | Where-Object { $_.Status -in @('failed','unconnected','pending') }).Count) { exit 1 }
        if ($env:REQUIRE_NATIVE -eq '1') { exit 1 }
        exit 69
    }
}
catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }
exit 0
