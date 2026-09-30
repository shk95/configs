<#
.SYNOPSIS
Reads the Windows-owned CI runtime declaration as validated JSON.
.DESCRIPTION
Validates the declaration format and pinned management artifact separately from
inbox bootstrap coverage. This read-only script does not install a runtime,
assert the current process version, or define a minimum consumer version.
Run this reader under PowerShell 7; inbox 5.1 coverage is a separate bootstrap lane.
.PARAMETER Path
The declaration to inspect. Defaults to ci-runtime.json beside this script.
.EXAMPLE
pwsh -NoProfile -File windows/tool/read-ci-runtime.ps1
#>
[CmdletBinding()]
param([string] $Path = (Join-Path $PSScriptRoot 'ci-runtime.json'))

$ErrorActionPreference = 'Stop'

function Assert-CiRuntimeJsonKeys {
    param([System.Text.Json.JsonElement] $Element)
    if ($Element.ValueKind -eq [System.Text.Json.JsonValueKind]::Object) {
        $names = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
        foreach ($property in $Element.EnumerateObject()) {
            if (-not $names.Add($property.Name)) {
                throw "Duplicate or ambiguous CI runtime JSON key '$($property.Name)'."
            }
            Assert-CiRuntimeJsonKeys $property.Value
        }
    }
    elseif ($Element.ValueKind -eq [System.Text.Json.JsonValueKind]::Array) {
        foreach ($item in $Element.EnumerateArray()) { Assert-CiRuntimeJsonKeys $item }
    }
}

function Assert-CiRuntimeFields {
    param($Record, [string[]] $Fields, [string] $Label)
    if ($null -eq $Record -or $Record -isnot [pscustomobject]) {
        throw "CI runtime $Label must be an object."
    }
    $actual = @($Record.PSObject.Properties.Name)
    foreach ($name in $actual) {
        if ($Fields -cnotcontains $name) { throw "CI runtime $Label has unknown field '$name'." }
    }
    foreach ($name in $Fields) {
        if ($actual -cnotcontains $name) { throw "CI runtime $Label is missing '$name'." }
    }
}

try {
    # INV windows/ci-runtime-declared: readers refuse an unknown format and
    # malformed runtime/artifact contracts before automation consumes them.
    $json = Get-Content -LiteralPath $Path -Raw -Encoding utf8
    # Inspect original keys before ConvertFrom-Json can collapse exact duplicates
    # or case-insensitive PowerShell property lookup can make them ambiguous.
    $document = [System.Text.Json.JsonDocument]::Parse($json)
    try { Assert-CiRuntimeJsonKeys $document.RootElement }
    finally { $document.Dispose() }
    $record = $json | ConvertFrom-Json -ErrorAction Stop
    Assert-CiRuntimeFields $record @('formatVersion', 'management', 'bootstrap') 'root'
    if (($record.formatVersion -isnot [int] -and $record.formatVersion -isnot [long]) -or
        $record.formatVersion -ne 1) { throw 'Unsupported CI runtime formatVersion; expected 1.' }
    Assert-CiRuntimeFields $record.management @('version', 'architecture', 'asset') 'management'
    if ($record.management.version -isnot [string] -or
        $record.management.version -cnotmatch '\A7\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\z') {
        throw 'CI management version must be an exact stable PowerShell 7 version.'
    }
    if ($record.management.architecture -isnot [string] -or $record.management.architecture -cne 'x64') {
        throw 'Unsupported CI management architecture; expected x64.'
    }
    Assert-CiRuntimeFields $record.management.asset @('uri', 'sha256') 'management.asset'
    $version = $record.management.version
    $expectedUri = "https://github.com/PowerShell/PowerShell/releases/download/v$version/PowerShell-$version-win-x64.zip"
    if ($record.management.asset.uri -isnot [string] -or $record.management.asset.uri -cne $expectedUri) {
        throw 'CI management artifact must be the exact official versioned Windows x64 ZIP.'
    }
    if ($record.management.asset.sha256 -isnot [string] -or
        $record.management.asset.sha256 -cnotmatch '\A[0-9a-f]{64}\z') {
        throw 'CI management artifact requires a lowercase SHA256 digest.'
    }
    Assert-CiRuntimeFields $record.bootstrap @('engine', 'version', 'architecture', 'source', 'entryPoints') 'bootstrap'
    foreach ($field in @('engine', 'version', 'architecture', 'source')) {
        if ($record.bootstrap.$field -isnot [string]) {
            throw "CI bootstrap $field must be a string for the separate inbox engine."
        }
    }
    if ($record.bootstrap.engine -cne 'WindowsPowerShell' -or $record.bootstrap.version -cne '5.1' -or
        $record.bootstrap.architecture -cne 'x64' -or $record.bootstrap.source -cne 'inbox') {
        throw 'CI bootstrap coverage must name the separate inbox Windows PowerShell 5.1 x64 engine.'
    }
    $expectedEntries = @('windows/win-env.ps1', 'windows/tool/bootstrap.ps1')
    if ($record.bootstrap.entryPoints -isnot [array] -or $record.bootstrap.entryPoints.Count -ne 2 -or
        @($record.bootstrap.entryPoints | Where-Object { $_ -isnot [string] }).Count -ne 0 -or
        ($record.bootstrap.entryPoints -join "`n") -cne ($expectedEntries -join "`n")) {
        throw 'CI bootstrap entryPoints must name the Windows entry and bootstrap scripts in declared order.'
    }
    $record | ConvertTo-Json -Depth 5
    exit 0
}
catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
