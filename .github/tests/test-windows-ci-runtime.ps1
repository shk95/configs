# INV repository/windows-ci-runtime-bound
# Native positive/negative fixtures exercise the real pinned executable and
# inbox entry/bootstrap sources with synthetic dependencies, never Apply.
param([string] $RuntimePath)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$temporary = Join-Path $env:RUNNER_TEMP ('ci-runtime-fixtures-' + [Guid]::NewGuid().ToString('N'))

function Assert-Result {
    param([bool] $Condition, [string] $Message)
    if (-not $Condition) { throw $Message }
}
function Assert-Refused {
    param([scriptblock] $Action, [string] $Message)
    $refused = $false
    try { & $Action | Out-Null }
    catch { $refused = $true }
    Assert-Result $refused $Message
}

try {
    Import-Module (Join-Path $root '.github/scripts/WindowsCiRuntime.psm1') -Force
    $record = Read-CiRuntimeDeclaration -RepositoryRoot $root
    Set-CiRuntimePath -RuntimePath $RuntimePath
    $actual = Assert-CiManagementRuntime -RuntimePath $RuntimePath -Declaration $record
    Write-Host ('Native management fixture: ' + ($actual | ConvertTo-Json -Compress))
    New-Item -ItemType Directory -Path $temporary | Out-Null

    # Hash must be checked before extraction. A harmless synthetic executable
    # name tests archive handling; actual runtime execution is tested above.
    $payload = Join-Path $temporary 'pwsh.exe'
    Set-Content -LiteralPath $payload -Value 'fixture bytes; never executable'
    $archive = Join-Path $temporary 'fixture.zip'
    Compress-Archive -LiteralPath $payload -DestinationPath $archive
    $hash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    $destination = Join-Path $temporary 'verified'
    $expanded = Expand-VerifiedCiRuntime -Archive $archive -Destination $destination -ExpectedSha256 $hash
    Assert-Result (Test-Path -LiteralPath $expanded) 'Matching archive was not extracted.'
    $refusedDestination = Join-Path $temporary 'refused'
    Assert-Refused { Expand-VerifiedCiRuntime -Archive $archive -Destination $refusedDestination -ExpectedSha256 ('0' * 64) } 'Tampered hash was accepted.'
    Assert-Result (-not (Test-Path -LiteralPath $refusedDestination)) 'Hash mismatch extracted untrusted bytes.'
    $emptyZip = Join-Path $temporary 'no-executable.zip'
    $text = Join-Path $temporary 'data.txt'
    Set-Content -LiteralPath $text -Value 'no runtime'
    Compress-Archive -LiteralPath $text -DestinationPath $emptyZip
    $emptyHash = (Get-FileHash -LiteralPath $emptyZip -Algorithm SHA256).Hash.ToLowerInvariant()
    Assert-Refused { Expand-VerifiedCiRuntime -Archive $emptyZip -Destination (Join-Path $temporary 'empty') -ExpectedSha256 $emptyHash } 'ZIP without runtime was accepted.'

    $wrongVersion = ($record | ConvertTo-Json -Depth 6) | ConvertFrom-Json
    $wrongVersion.management.version = '0.0.0'
    Assert-Refused { Assert-CiManagementRuntime -RuntimePath $RuntimePath -Declaration $wrongVersion } 'Wrong native version was accepted.'
    $wrongArchitecture = ($record | ConvertTo-Json -Depth 6) | ConvertFrom-Json
    $wrongArchitecture.management.architecture = 'arm64'
    Assert-Refused { Assert-CiManagementRuntime -RuntimePath $RuntimePath -Declaration $wrongArchitecture } 'Wrong native architecture was accepted.'
    Assert-Refused { Assert-CiManagementRuntime -RuntimePath (Join-Path $temporary 'missing.exe') -Declaration $record } 'Missing executable was accepted.'
    $savedPath = $env:Path
    try {
        # PowerShell may discover its own executable even with empty PATH.
        # An earlier harmless file candidate proves conflicting resolution.
        $env:Path = "$temporary;$savedPath"
        Assert-Refused { Assert-CiManagementRuntime -RuntimePath $RuntimePath -Declaration $record } 'Conflicting nested runtime resolution was accepted.'
    }
    finally { $env:Path = $savedPath }

    # Native child statuses cannot be overwritten by a later command, and 69
    # is unavailable evidence rather than a passing management check.
    $child = Join-Path $temporary 'child.ps1'
    Set-Content -LiteralPath $child -Value 'exit 0'
    Invoke-CiProcess -Executable $RuntimePath -Arguments @('-NoProfile', '-File', $child)
    foreach ($status in @(23, 69)) {
        Set-Content -LiteralPath $child -Value "exit $status"
        Assert-Refused { Invoke-CiProcess -Executable $RuntimePath -Arguments @('-NoProfile', '-File', $child) } "Child status $status was accepted."
    }
    Set-Content -LiteralPath $child -Value "throw 'terminating fixture error'"
    Assert-Refused { Invoke-CiProcess -Executable $RuntimePath -Arguments @('-NoProfile', '-File', $child) } 'Terminating child error was accepted.'

    # Consumption must retain the Windows reader's refusal, not fall back to
    # an independently hardcoded runtime declaration.
    $readerRoot = Join-Path $temporary 'reader-fixture'
    New-Item -ItemType Directory -Path (Join-Path $readerRoot 'windows/tool') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $root 'windows/tool/read-ci-runtime.ps1') -Destination (Join-Path $readerRoot 'windows/tool/read-ci-runtime.ps1')
    Set-Content -LiteralPath (Join-Path $readerRoot 'windows/tool/ci-runtime.json') -Value '{"formatVersion":99}'
    Assert-Refused { Read-CiRuntimeDeclaration -RepositoryRoot $readerRoot } 'Windows reader refusal was ignored.'

    # Exercise the declared inbox engine itself, rather than parsing 5.1
    # scripts under PS7 or treating the existing management suite as 5.1 proof.
    $inbox = Join-Path $env:SystemRoot 'System32/WindowsPowerShell/v1.0/powershell.exe'
    Assert-Result (Test-Path -LiteralPath $inbox) 'Declared inbox bootstrap engine is unavailable.'
    $entry = Join-Path $root $record.bootstrap.entryPoints[0]
    $bootstrap = Join-Path $root $record.bootstrap.entryPoints[1]
    $wrapper = Join-Path $temporary 'inbox-probe.ps1'
    @'
param([string] $Target, [string] $Mode, [string] $ManagementDirectory, [string] $ExpectedVersion)
$ErrorActionPreference = 'Stop'
$actualVersion = '{0}.{1}' -f $PSVersionTable.PSVersion.Major, $PSVersionTable.PSVersion.Minor
if ($PSVersionTable.PSEdition -ne 'Desktop' -or $actualVersion -ne $ExpectedVersion -or [IntPtr]::Size -ne 8) {
    throw 'Inbox bootstrap engine/version/architecture mismatch.'
}
Write-Output ('Inbox bootstrap actual: {0}/{1}/x64/{2}' -f $PSVersionTable.PSEdition, $actualVersion, (Get-Process -Id $PID).Path)
$env:REQUIRE_NATIVE = '1'
if ($Mode -eq 'missing') { $env:Path = '' }
else {
    $env:Path = $ManagementDirectory
    function global:winget.exe { throw 'The fixture must never install anything.' }
}
if ($Mode -eq 'help') { & $Target help }
elseif ($Mode -eq 'unknown') { & $Target unknown-fixture-command }
elseif ($Mode -eq 'entry-check') { & $Target check -Minimal }
else { & $Target -Check -Minimal }
exit $LASTEXITCODE
'@ | Set-Content -LiteralPath $wrapper

    function Invoke-InboxFixture {
        param([string] $Target, [string] $Mode)
        $output = @(& $inbox -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $wrapper `
                -Target $Target -Mode $Mode -ManagementDirectory (Split-Path -Parent $RuntimePath) `
                -ExpectedVersion $record.bootstrap.version 2>&1 | ForEach-Object { "$_" })
        $status = $LASTEXITCODE
        Write-Host ("Inbox fixture $Mode status=$status; " + ($output | Select-Object -First 1))
        return [pscustomobject]@{ ExitCode = $status; Output = ($output -join "`n") }
    }
    Assert-Result ((Invoke-InboxFixture $entry 'help').ExitCode -eq 0) 'Inbox entry help did not succeed.'
    Assert-Result ((Invoke-InboxFixture $entry 'unknown').ExitCode -eq 64) 'Inbox entry did not refuse an unknown command.'
    Assert-Result ((Invoke-InboxFixture $bootstrap 'missing').ExitCode -eq 1) 'Inbox bootstrap accepted missing native prerequisites.'

    # Copy the exact entry/bootstrap source bytes; replace only the downstream
    # setup dependency so success and a child failure can be exercised without
    # touching real host desired state or installing PowerShell.
    $fixtureRoot = Join-Path $temporary 'bootstrap-fixture'
    New-Item -ItemType Directory -Path (Join-Path $fixtureRoot 'tool') -Force | Out-Null
    $copiedEntry = Join-Path $fixtureRoot 'win-env.ps1'
    $copiedBootstrap = Join-Path $fixtureRoot 'tool/bootstrap.ps1'
    Copy-Item -LiteralPath $entry -Destination $copiedEntry
    Copy-Item -LiteralPath $bootstrap -Destination $copiedBootstrap
    Assert-Result ((Get-FileHash $entry).Hash -eq (Get-FileHash $copiedEntry).Hash) 'Entry source copy changed.'
    Assert-Result ((Get-FileHash $bootstrap).Hash -eq (Get-FileHash $copiedBootstrap).Hash) 'Bootstrap source copy changed.'
    $setup = Join-Path $fixtureRoot 'tool/setup.ps1'
    @'
param([switch] $Check, [switch] $Minimal)
if (-not $Check -or -not $Minimal) { throw 'Bootstrap fixture did not forward read-only selection.' }
if ($PSVersionTable.PSVersion.ToString() -ne $env:CI_FIXTURE_MANAGEMENT_VERSION -or
    (Get-Process -Id $PID).Path -ne $env:CI_FIXTURE_MANAGEMENT_EXECUTABLE) {
    throw 'Inbox bootstrap selected the wrong management child.'
}
Write-Output ('Forwarded management child: ' + $PSVersionTable.PSVersion.ToString())
exit ([int]$env:CI_FIXTURE_CHILD_STATUS)
'@ | Set-Content -LiteralPath $setup
    $env:CI_FIXTURE_MANAGEMENT_VERSION = $record.management.version
    $env:CI_FIXTURE_MANAGEMENT_EXECUTABLE = $RuntimePath
    foreach ($status in @(0, 37)) {
        $env:CI_FIXTURE_CHILD_STATUS = "$status"
        foreach ($case in @(@{ Target = $copiedBootstrap; Mode = 'bootstrap-check' }, @{ Target = $copiedEntry; Mode = 'entry-check' })) {
            $result = Invoke-InboxFixture $case.Target $case.Mode
            Assert-Result ($result.ExitCode -eq $status -and $result.Output -match 'Forwarded management child:') 'Inbox entry/bootstrap did not preserve the actual management child result.'
        }
    }
    Write-Host 'CI runtime fixtures passed: verified archive/refusals, actual management identity, nested resolution, child failures, Windows reader refusal, and separate inbox entry/bootstrap execution.'
    exit 0
}
catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }
finally {
    Remove-Item -LiteralPath $temporary -Recurse -Force -ErrorAction SilentlyContinue
}
