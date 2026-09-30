# INV repository/windows-ci-runtime-bound
param([string] $RepositoryRoot = (Get-Location).Path, [string] $TemporaryRoot = $env:RUNNER_TEMP)
$ErrorActionPreference = 'Stop'
try {
    Import-Module (Join-Path $PSScriptRoot 'WindowsCiRuntime.psm1') -Force
    $record = Read-CiRuntimeDeclaration -RepositoryRoot $RepositoryRoot
    $directory = Join-Path $TemporaryRoot ('configs-runtime-' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $directory | Out-Null
    $archive = Join-Path $directory 'management.zip'
    Invoke-WebRequest -Uri $record.management.asset.uri -OutFile $archive -ErrorAction Stop
    $executable = Expand-VerifiedCiRuntime -Archive $archive `
        -Destination (Join-Path $directory 'management') -ExpectedSha256 $record.management.asset.sha256
    Set-CiRuntimePath -RuntimePath $executable
    $actual = Assert-CiManagementRuntime -RuntimePath $executable -Declaration $record
    Write-Host ('Acquired management runtime: ' + ($actual | ConvertTo-Json -Compress))
    "pwsh=$executable" | Out-File -LiteralPath $env:GITHUB_OUTPUT -Encoding utf8 -Append
    exit 0
}
catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }
