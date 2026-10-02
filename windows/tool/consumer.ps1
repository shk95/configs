<#
.SYNOPSIS
Inspects, generates or previews host selection without applying Windows state.
.DESCRIPTION
Use an explicit clean local provider clone at the full environment provider SHA.
Settings documents are explicit relative connections; originals are never edited.
Generation requires native parsers for every selected payload. Inspect and export
emit JSON to stdout; generate emits the result identity after atomic publication.
.PARAMETER Operation
inspect, generate or export-selection, normally supplied by win-env.ps1.
.PARAMETER SourceRoot
Local clean provider checkout. No fetch, clone or source update is performed.
.PARAMETER Environment
Version 1 host environment JSON, required for generate.
.PARAMETER Output
Dedicated generation directory outside the provider and host originals.
.PARAMETER State
Optional legacy state file for export-selection; malformed existing state refuses.
.EXAMPLE
pwsh -NoProfile -File windows/win-env.ps1 inspect -SourceRoot C:\provider
.EXAMPLE
pwsh -NoProfile -File windows/win-env.ps1 generate -SourceRoot C:\provider -Environment C:\host\environment.json -Output C:\generated\current
#>
#Requires -Version 7.0
[CmdletBinding()]
param([Parameter(Mandatory)][ValidateSet('inspect', 'generate', 'export-selection')][string] $Operation,
    [Parameter(Mandatory)][string] $SourceRoot, [string] $Environment, [string] $Output, [string] $State)
$ErrorActionPreference = 'Stop'
# INV windows/automation-tools-standalone: direct invocation exits explicitly.
Import-Module (Join-Path (Split-Path -Parent $PSScriptRoot) 'src/WinEnvGeneration.psm1') -Force
try {
    switch ($Operation) {
        'inspect' {
            if ($Environment -or $Output -or $State) { throw 'inspect accepts SourceRoot only.' }
            $result = Get-WinEnvConsumerContract $SourceRoot
        }
        'generate' {
            if (-not $Environment -or -not $Output -or $State) { throw 'generate requires Environment and Output, and accepts no State.' }
            $result = New-WinEnvGeneration -Environment $Environment -SourceRoot $SourceRoot -Output $Output
        }
        'export-selection' {
            if ($Environment -or $Output) { throw 'export-selection accepts SourceRoot and optional State only.' }
            $result = Get-WinEnvLegacySelectionProposal -SourceRoot $SourceRoot -State $State
        }
    }
    $result | ConvertTo-Json -Depth 100
}
catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }
exit 0
