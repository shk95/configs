# INV repository/windows-ci-runtime-bound
param([string] $RuntimePath, [string] $RepositoryRoot = (Get-Location).Path)
$ErrorActionPreference = 'Stop'
try {
    Import-Module (Join-Path $PSScriptRoot 'WindowsCiRuntime.psm1') -Force
    $record = Read-CiRuntimeDeclaration -RepositoryRoot $RepositoryRoot
    Set-CiRuntimePath -RuntimePath $RuntimePath
    $actual = Assert-CiManagementRuntime -RuntimePath $RuntimePath -Declaration $record
    if (-not [string]::Equals((Get-Process -Id $PID).Path, $RuntimePath, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'The management CI orchestrator itself must use the declared executable.'
    }
    Write-Host ('Management CI runtime: ' + ($actual | ConvertTo-Json -Compress))
    Invoke-CiProcess -Executable $RuntimePath -Arguments @('-NoProfile', '-NonInteractive', '-File',
        (Join-Path $RepositoryRoot '.github/tests/test-windows-ci-runtime.ps1'), '-RuntimePath', $RuntimePath)
    Invoke-CiProcess -Executable $RuntimePath -Arguments @('-NoProfile', '-NonInteractive', '-File',
        (Join-Path $RepositoryRoot 'windows/tool/setup-dev.ps1'))
    & winget.exe install --id Zellij.Zellij --exact --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity
    if ($LASTEXITCODE -ne 0) { throw "Zellij CI prerequisite failed: $LASTEXITCODE" }
    # setup-dev refreshes its child's PATH and WinGet can change machine/user
    # PATH. Preserve portable-runtime precedence when those changes are read.
    Set-CiRuntimePath -RuntimePath $RuntimePath
    $actual = Assert-CiManagementRuntime -RuntimePath $RuntimePath -Declaration $record
    Write-Host ('Management runtime after PATH refresh: ' + ($actual | ConvertTo-Json -Compress))
    Invoke-CiProcess -Executable $RuntimePath -Arguments @('-NoProfile', '-NonInteractive', '-File',
        (Join-Path $RepositoryRoot 'windows/tool/check-desired-state.ps1'))
    Invoke-CiProcess -Executable $RuntimePath -Arguments @('-NoProfile', '-NonInteractive', '-File',
        (Join-Path $RepositoryRoot 'windows/tool/test.ps1'))
    exit 0
}
catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }
