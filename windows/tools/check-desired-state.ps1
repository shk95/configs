[CmdletBinding()]
param(
    # The merge gate must not accept a payload nobody parsed. CI passes this,
    # and the REQUIRE_NATIVE variable the rest of the repository already uses
    # means the same thing.
    [switch] $RequireNativeTooling
)

# Every source this host can parse is parsed, and only the ones it cannot are
# reported. Requiring zellij.exe and luac up front instead made a Windows
# clone without them fail before validating the JSON, INI and PowerShell
# sources it could have validated perfectly well, and reported "validation
# failed" for state that was never examined.
#
#   exit 0   every declared source parsed
#   exit 1   a parser ran and rejected a source, or native evidence was required
#   exit 69  everything available parsed; the rest is unverified here

$ErrorActionPreference = 'Stop'
$windowsRoot = Split-Path -Parent $PSScriptRoot
$desiredStateRoot = Join-Path $windowsRoot 'desired'
$manifestPath = Join-Path $desiredStateRoot 'manifest.json'

Import-Module (Join-Path $windowsRoot 'src\WinEnv.psm1') -Force

$requireNative = $RequireNativeTooling.IsPresent -or ($env:REQUIRE_NATIVE -eq '1')
$unverified = [System.Collections.Generic.List[string]]::new()

$manifest = Get-WinEnvManifest -Path $manifestPath

foreach ($definition in $manifest.ManagedFiles) {
    $sourcePath = Join-Path $desiredStateRoot $definition.Source
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        throw "Managed source is missing: $sourcePath"
    }

    $reason = Test-WinEnvSourceFile -Definition $definition -RepositoryRoot $desiredStateRoot
    if ($reason) { $unverified.Add("$($definition.Id) [$($definition.Parser)]: $reason") }
}

# Templates are not managed files, but a broken one is still a broken payload.
$luac = Get-WinEnvLuaCompiler
foreach ($example in Get-ChildItem (Join-Path $desiredStateRoot 'files') -Filter '*.lua.example' -File -Recurse) {
    if (-not $luac) {
        $unverified.Add("$($example.Name) [Lua]: no luac compiler is available")
        continue
    }

    $null = & $luac.Source -p $example.FullName 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Lua rejected '$($example.FullName)'." }
}

if ($unverified.Count -eq 0) {
    Write-Host 'Windows desired state is valid.'
    exit 0
}

foreach ($item in $unverified) { Write-Host "· unverified: $item" }

if ($requireNative) {
    [Console]::Error.WriteLine(
        "$($unverified.Count) source(s) could not be parsed here and native evidence was required.")
    exit 1
}

Write-Host ''
Write-Host 'Every source the available tooling can parse is valid. The entries above'
Write-Host 'remain unverified on this host; CI must supply that evidence.'
exit 69
