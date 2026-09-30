# INV repository/windows-ci-runtime-bound
# Repository orchestration consumes validated Windows verification data; it
# does not choose platform versions or install a runtime on a consumer host.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Read-CiRuntimeDeclaration {
    param([string] $RepositoryRoot)
    $readerHost = (Get-Process -Id $PID).Path
    $reader = Join-Path $RepositoryRoot 'windows/tool/read-ci-runtime.ps1'
    $json = @(& $readerHost -NoLogo -NoProfile -NonInteractive -File $reader)
    if ($LASTEXITCODE -ne 0) { throw "Windows runtime reader failed: $LASTEXITCODE" }
    return (($json -join "`n") | ConvertFrom-Json -ErrorAction Stop)
}

function Expand-VerifiedCiRuntime {
    param([string] $Archive, [string] $Destination, [string] $ExpectedSha256)
    $actual = (Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -cne $ExpectedSha256) { throw "CI runtime SHA256 mismatch: $actual" }
    # Remove a possible download zone only after the bytes match the reviewed
    # artifact, before extracting the portable Windows ZIP.
    Unblock-File -LiteralPath $Archive -ErrorAction Stop
    Expand-Archive -LiteralPath $Archive -DestinationPath $Destination -ErrorAction Stop
    $executable = Join-Path $Destination 'pwsh.exe'
    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
        throw 'Verified CI runtime ZIP contains no pwsh.exe.'
    }
    return $executable
}

function Set-CiRuntimePath {
    param([string] $RuntimePath)
    $runtimeDirectory = Split-Path -Parent $RuntimePath
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$runtimeDirectory;$machinePath;$userPath;$env:Path"
}

function Assert-CiManagementRuntime {
    param([string] $RuntimePath, $Declaration)
    if (-not (Test-Path -LiteralPath $RuntimePath -PathType Leaf)) {
        throw 'Declared CI runtime executable is missing.'
    }
    $probe = Join-Path $PSScriptRoot 'assert-windows-ci-runtime.ps1'
    $json = @(& $RuntimePath -NoLogo -NoProfile -NonInteractive -File $probe `
            -Version $Declaration.management.version `
            -Architecture $Declaration.management.architecture -Executable $RuntimePath)
    if ($LASTEXITCODE -ne 0) { throw "CI runtime identity probe failed: $LASTEXITCODE" }
    return (($json -join "`n") | ConvertFrom-Json -ErrorAction Stop)
}

function Invoke-CiProcess {
    param([string] $Executable, [string[]] $Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "CI child failed with exit code $LASTEXITCODE`: $Executable" }
}

Export-ModuleMember -Function Read-CiRuntimeDeclaration, Expand-VerifiedCiRuntime,
    Set-CiRuntimePath, Assert-CiManagementRuntime, Invoke-CiProcess
