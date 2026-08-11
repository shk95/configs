[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$windowsRoot = Split-Path -Parent $PSScriptRoot
$desiredStateRoot = Join-Path $windowsRoot 'desired'
$manifestPath = Join-Path $desiredStateRoot 'manifest.json'

Import-Module (Join-Path $windowsRoot 'src\WinEnv.psm1') -Force

$manifest = Get-WinEnvManifest -Path $manifestPath
$zellij = Get-Command zellij.exe -ErrorAction SilentlyContinue
$luac = Get-Command luac.exe, luac5.4.exe, luac54.exe, luac5.1.exe, luac51.exe, luac -ErrorAction SilentlyContinue |
    Select-Object -First 1

if (-not $zellij) {
    throw 'zellij.exe is required to validate Windows Zellij KDL.'
}
if (-not $luac) {
    throw 'A luac compiler is required to validate Windows WezTerm Lua.'
}

foreach ($definition in $manifest.ManagedFiles) {
    $sourcePath = Join-Path $desiredStateRoot $definition.Source
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        throw "Managed source is missing: $sourcePath"
    }

    if ($definition.Parser -eq 'Lua') {
        $null = & $luac.Source -p $sourcePath 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Lua rejected '$sourcePath'." }
        continue
    }

    Test-WinEnvSourceFile -Definition $definition -RepositoryRoot $desiredStateRoot
}

foreach ($example in Get-ChildItem (Join-Path $desiredStateRoot 'files') -Filter '*.lua.example' -File -Recurse) {
    $null = & $luac.Source -p $example.FullName 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Lua rejected '$($example.FullName)'." }
}

Write-Host 'Windows desired state is valid.'
