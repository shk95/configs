BeforeAll {
    $windowsRoot = Split-Path -Parent $PSScriptRoot
    Import-Module (Join-Path $windowsRoot 'src/WinEnv.psm1') -Force
    Import-Module (Join-Path $windowsRoot 'src/WinEnvGeneration.psm1') -Force
    $provider = Join-Path $TestDrive 'provider'
    [void](New-Item -ItemType Directory $provider)
    Copy-Item -LiteralPath $windowsRoot -Destination (Join-Path $provider 'windows') -Recurse
    & git init -q $provider
    & git -C $provider config core.autocrlf false
    & git -C $provider add windows
    & git -C $provider -c user.name=Fixture -c user.email=fixture@example.invalid -c core.hooksPath=disabled commit -qm 'fixture provider'
    if ($LASTEXITCODE -ne 0) { throw 'Provider fixture commit failed.' }
    $commit = (& git -C $provider rev-parse HEAD).Trim()
    $originals = Join-Path $TestDrive 'host'
    [void](New-Item -ItemType Directory $originals)
    $environment = Join-Path $originals 'environment.json'
    $output = Join-Path $TestDrive 'generation'
    function Write-FixtureJson($Path, $Value) {
        [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 100), [Text.UTF8Encoding]::new($false))
    }
    function New-FixtureEnvironment([object[]] $Features = @(), [hashtable] $Units = @{}) {
        Write-FixtureJson $environment ([ordered]@{ formatVersion = 1; provider = @{ commit = $commit }; features = @($Features); units = $Units })
    }
    function Clear-FixtureGitObjectReadOnly {
        # Pester owns TestDrive. Never traverse junctions into real runtime or
        # host directories; only synthetic repositories directly below it.
        foreach ($directory in (Get-ChildItem -LiteralPath $TestDrive -Directory -Force)) {
            if ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
            $gitDirectory = Join-Path $directory.FullName '.git'
            $objects = Join-Path $gitDirectory 'objects'
            if (-not (Test-Path -LiteralPath $objects -PathType Container)) { continue }
            if ((Get-Item -LiteralPath $gitDirectory -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
            if ((Get-Item -LiteralPath $objects -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
            foreach ($objectDirectory in (Get-ChildItem -LiteralPath $objects -Directory -Force)) {
                if ($objectDirectory.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
                foreach ($file in (Get-ChildItem -LiteralPath $objectDirectory.FullName -File -Force)) {
                    if ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
                    if ($file.Attributes -band [IO.FileAttributes]::ReadOnly) {
                        $file.Attributes = $file.Attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
                    }
                }
            }
        }
    }
}
AfterAll { Clear-FixtureGitObjectReadOnly }

Describe 'Host declaration and generation contract' {
    # INV windows/host-generation-bound
    BeforeEach {
        New-FixtureEnvironment
        if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Recurse -Force }
    }
    It 'exposes source-bound formats, actual unit identities and excluded LTSC capabilities' {
        $contract = Get-WinEnvConsumerContract $provider
        $contract.provider.commit | Should -BeExactly $commit
        $contract.formats.environment | Should -Be 1
        $contract.clientBaseline.build | Should -Be 19044
        $contract.excludedCapabilities | Should -Contain defaultTerminalDelegation
        $contract.units.id | Should -Not -Contain wslConfig
        $contract.units.id | Should -Not -Contain fancyZonesCustomLayouts
        $contract.units.id | Should -Not -Contain fancyZonesLayoutHotkeys
        $contract.units.id | Should -Contain fancyZonesDefaultLayouts
    }
    It 'selects <Feature> with exactly its dependency closure' -ForEach @(
        @{ Feature = ''; Expected = 'core' }, @{ Feature = 'font'; Expected = 'core,font' },
        @{ Feature = 'zellij'; Expected = 'core,zellij' }, @{ Feature = 'terminal'; Expected = 'core,font,zellij,terminal' },
        @{ Feature = 'wezterm'; Expected = 'core,font,wezterm' }, @{ Feature = 'powertoys'; Expected = 'core,powertoys' }
    ) {
        [object[]] $asked = @()
        if ($Feature) { $asked = @($Feature) }
        New-FixtureEnvironment -Features $asked
        $plan = Get-WinEnvEnvironmentPlan $environment $provider
        ($plan.Selection.Selected -join ',') | Should -BeExactly $Expected
    }
    It 'materializes core only and binds exact originals, provider, native tools and selected payloads' {
        $before = Get-WinEnvFileDigest $environment
        $result = New-WinEnvGeneration $environment $provider $output
        $record = Assert-WinEnvGeneratedIntegrity $output
        $result.identity | Should -BeExactly $record.identity
        $record.provider.commit | Should -BeExactly $commit
        ($record.selected -join ',') | Should -BeExactly core
        ($record.units.id -join ',') | Should -BeExactly powershellProfile
        $record.files.path | Should -Contain 'windows/tool/setup.ps1'
        $record.files.path | Should -Not -Contain 'windows/desired/files/terminal/settings.json'
        (Get-WinEnvFileDigest $environment) | Should -BeExactly $before
    }
    It 'chooses complete host content without inserting provider default keys' {
        $document = Join-Path $originals 'powertoys.json'
        Write-FixtureJson $document @{ formatVersion = 1; source = 'host'; settings = @{ properties = @{ customHostSetting = 9 } } }
        New-FixtureEnvironment -Features powertoys -Units @{ awake = @{ enabled = $true; document = 'powertoys.json' } }
        [void](New-WinEnvGeneration $environment $provider $output)
        $chosen = Read-WinEnvContractJson (Join-Path $output 'windows/desired/files/powertoys/Awake/settings.json')
        $chosen.properties.customHostSetting | Should -Be 9
        $chosen.Keys.Count | Should -Be 1
        (Assert-WinEnvGeneratedIntegrity $output).units | Where-Object id -CEQ awake | ForEach-Object source | Should -BeExactly host
    }
    It 'can explicitly return a connected unit to configs defaults' {
        Write-FixtureJson (Join-Path $originals 'profile.json') @{ formatVersion = 1; source = 'configs'; settings = $null }
        New-FixtureEnvironment -Units @{ powershellProfile = @{ enabled = $true; document = 'profile.json' } }
        [void](New-WinEnvGeneration $environment $provider $output)
        (Get-WinEnvFileDigest (Join-Path $output 'windows/desired/files/powershell/profile.ps1')) | Should -BeExactly (Get-WinEnvFileDigest (Join-Path $provider 'windows/desired/files/powershell/profile.ps1'))
    }
    It 'disabled units keep originals and omit their payload while retaining core package selection' {
        $document = Join-Path $originals 'profile.json'
        Write-FixtureJson $document @{ formatVersion = 1; source = 'host'; settings = 'invalid PowerShell (' }
        $before = Get-WinEnvFileDigest $document
        New-FixtureEnvironment -Units @{ powershellProfile = @{ enabled = $false; document = 'profile.json' }; retiredPersonalUnit = @{ enabled = $false } }
        [void](New-WinEnvGeneration $environment $provider $output)
        $record = Assert-WinEnvGeneratedIntegrity $output
        @($record.units).Count | Should -Be 0
        (Get-WinEnvFileDigest $document) | Should -BeExactly $before
        $record.files.path | Should -Not -Contain 'windows/desired/files/powershell/profile.ps1'
        $manifest = Get-WinEnvManifest (Join-Path $output 'windows/desired/manifest.json')
        $manifest.Packages.Id | Should -Contain Microsoft.PowerShell
        New-FixtureEnvironment -Units @{ powershellProfile = @{ enabled = $true; document = 'profile.json' } }
        { New-WinEnvGeneration $environment $provider $output } | Should -Throw '*syntax error*'
        { Assert-WinEnvGeneratedIntegrity $output } | Should -Throw '*input changed*'
    }
    It 'refuses <Name> before publishing a result' -ForEach @(
        @{ Name = 'unknown environment version'; Change = { param($v) $v.formatVersion = 2 }; Reason = '*formatVersion*' },
        @{ Name = 'unknown field'; Change = { param($v) $v.unexpectedField = 'synthetic' }; Reason = '*unknown field*' },
        @{ Name = 'short provider reference'; Change = { param($v) $v.provider.commit = 'main' }; Reason = '*full 40*' },
        @{ Name = 'wrong exact provider'; Change = { param($v) $v.provider.commit = '0000000000000000000000000000000000000000' }; Reason = '*does not match*' },
        @{ Name = 'scalar features'; Change = { param($v) $v.features = 'terminal' }; Reason = '*must be an array*' },
        @{ Name = 'unknown feature'; Change = { param($v) $v.features = @('unknown') }; Reason = '*Unknown active feature*' },
        @{ Name = 'wrong-case feature'; Change = { param($v) $v.features = @('Terminal') }; Reason = '*Unknown active feature*' },
        @{ Name = 'duplicate feature'; Change = { param($v) $v.features = @('terminal','terminal') }; Reason = '*Duplicate*' },
        @{ Name = 'unknown active unit'; Change = { param($v) $v.units.unknown = @{ enabled = $true } }; Reason = '*Unknown active unit*' },
        @{ Name = 'nonboolean enabled'; Change = { param($v) $v.units.powershellProfile = @{ enabled = 'false' } }; Reason = '*boolean*' },
        @{ Name = 'missing connected document'; Change = { param($v) $v.units.powershellProfile = @{ enabled = $true; document = 'missing.json' } }; Reason = '*missing*' },
        @{ Name = 'path traversal'; Change = { param($v) $v.units.powershellProfile = @{ enabled = $true; document = '../escape.json' } }; Reason = '*traversal*' }
    ) {
        $value = Read-WinEnvContractJson $environment
        & $Change $value
        Write-FixtureJson $environment $value
        { New-WinEnvGeneration $environment $provider $output } | Should -Throw $Reason
        (Test-Path -LiteralPath $output) | Should -BeFalse
    }
    It 'refuses duplicate and case-ambiguous JSON keys before conversion' -ForEach @(
        @{ Extra = '"formatVersion":1' }, @{ Extra = '"FormatVersion":1' }, @{ Extra = '"format\u0056ersion":1' }
    ) {
        $text = [IO.File]::ReadAllText($environment)
        [IO.File]::WriteAllText($environment, [regex]::Replace($text, '\A\{', ('{' + $Extra + ',')))
        { Get-WinEnvEnvironmentPlan $environment $provider } | Should -Throw '*Duplicate or ambiguous*'
    }
    It 'refuses unknown settings formats even when disabled' {
        Write-FixtureJson (Join-Path $originals 'inactive.json') @{ formatVersion = 2; source = 'host'; settings = 'text' }
        New-FixtureEnvironment -Units @{ powershellProfile = @{ enabled = $false; document = 'inactive.json' } }
        { Get-WinEnvEnvironmentPlan $environment $provider } | Should -Throw '*formatVersion*'
    }
    It 'refuses host values connected with configs source and duplicate document ownership' {
        Write-FixtureJson (Join-Path $originals 'settings.json') @{ formatVersion = 1; source = 'configs'; settings = 'ignored' }
        New-FixtureEnvironment -Units @{ powershellProfile = @{ enabled = $true; document = 'settings.json' } }
        { Get-WinEnvEnvironmentPlan $environment $provider } | Should -Throw '*must be null*'
        Write-FixtureJson (Join-Path $originals 'settings.json') @{ formatVersion = 1; source = 'configs'; settings = $null }
        New-FixtureEnvironment -Features powertoys -Units @{ awake = @{ enabled = $true; document = 'settings.json' }; powershellProfile = @{ enabled = $true; document = './settings.json' } }
        { Get-WinEnvEnvironmentPlan $environment $provider } | Should -Throw '*Duplicate resolved*'
    }
    It 'refuses stale originals, metadata and matching native tool corruption' {
        [void](New-WinEnvGeneration $environment $provider $output)
        [IO.File]::AppendAllText($environment, ' ')
        { Assert-WinEnvGeneratedIntegrity $output } | Should -Throw '*input changed*'
        New-FixtureEnvironment
        $runner = Join-Path $output 'windows/tool/setup.ps1'
        [IO.File]::AppendAllText($runner, '# changed')
        { Assert-WinEnvGeneratedIntegrity $output } | Should -Throw '*tool*changed*'
        [void](New-WinEnvGeneration $environment $provider $output)
        $path = Join-Path $output 'generation.json'
        $record = Read-WinEnvContractJson $path
        $record.selected = @('core','powertoys')
        Write-FixtureJson $path $record
        { Assert-WinEnvGeneratedIntegrity $output } | Should -Throw '*metadata identity changed*'
    }
    It 'failed regeneration preserves the previous directory but refuses it for changed inputs' {
        [void](New-WinEnvGeneration $environment $provider $output)
        $before = Get-WinEnvFileDigest (Join-Path $output 'generation.json')
        New-FixtureEnvironment -Units @{ powershellProfile = @{ enabled = $true; document = 'missing.json' } }
        { New-WinEnvGeneration $environment $provider $output } | Should -Throw
        (Get-WinEnvFileDigest (Join-Path $output 'generation.json')) | Should -BeExactly $before
        { Assert-WinEnvGeneratedIntegrity $output } | Should -Throw '*input changed*'
    }
    It 'publishes a fully validated replacement when originals change successfully' {
        [void](New-WinEnvGeneration $environment $provider $output)
        $previous = (Assert-WinEnvGeneratedIntegrity $output).identity
        Write-FixtureJson (Join-Path $originals 'profile.json') @{ formatVersion = 1; source = 'host'; settings = '# synthetic host profile' }
        New-FixtureEnvironment -Units @{ powershellProfile = @{ enabled = $true; document = 'profile.json' } }
        [void](New-WinEnvGeneration $environment $provider $output)
        (Assert-WinEnvGeneratedIntegrity $output).identity | Should -Not -Be $previous
        [IO.File]::ReadAllText((Join-Path $output 'windows/desired/files/powershell/profile.ps1')) | Should -BeExactly '# synthetic host profile'
    }
    It 'refuses unavailable selected parsers without publishing' {
        Mock Test-WinEnvSourceFile -ModuleName WinEnvGeneration { 'required parser unavailable' }
        { New-WinEnvGeneration $environment $provider $output } | Should -Throw '*requires the active parser*'
        (Test-Path -LiteralPath $output) | Should -BeFalse
    }
    It 'refuses output overlapping originals or an existing unrelated directory' {
        { New-WinEnvGeneration $environment $provider (Join-Path $originals 'generation') } | Should -Throw '*overlap*'
        [void](New-Item -ItemType Directory $output)
        [IO.File]::WriteAllText((Join-Path $output 'preserved.txt'), 'existing data')
        { New-WinEnvGeneration $environment $provider $output } | Should -Throw '*not a generation*'
        [IO.File]::ReadAllText((Join-Path $output 'preserved.txt')) | Should -BeExactly 'existing data'
    }
    It 'exports first-use core-only and exact legacy selection without editing state' {
        (Get-WinEnvLegacySelectionProposal $provider).environment.features.Count | Should -Be 0
        $state = Join-Path $TestDrive 'legacy.json'
        Write-WinEnvState -Path $state -ProjectVersion 0.6.0 -GitCommit $commit -DesiredStateHash ('a'*64) -Feature @('core','wsl')
        $before = Get-WinEnvFileDigest $state
        $proposal = Get-WinEnvLegacySelectionProposal $provider $state
        ($proposal.environment.features -join ',') | Should -BeExactly 'core,wsl'
        $proposal.blocked | Should -BeTrue
        $proposal.actions[0] | Should -Match 'wsl.*explicit correction'
        (Get-WinEnvFileDigest $state) | Should -BeExactly $before
        [IO.File]::WriteAllText($state, '{broken')
        { Get-WinEnvLegacySelectionProposal $provider $state } | Should -Throw '*invalid*'
    }
    It 'schema 1 selection requires its exact recorded source rather than current optional defaults' {
        $state = Join-Path $TestDrive 'schema1.json'
        Write-FixtureJson $state @{ schemaVersion = 1; projectVersion = '0.6.0'; appliedAtUtc = '2026-01-01T00:00:00Z'; gitCommit = $commit }
        $proposal = Get-WinEnvLegacySelectionProposal $provider $state
        ($proposal.environment.features -join ',') | Should -BeExactly 'core,font,zellij,terminal,wezterm,powertoys'
        $value = Read-WinEnvContractJson $state
        $value.gitCommit = '0000000000000000000000000000000000000000'
        Write-FixtureJson $state $value
        { Get-WinEnvLegacySelectionProposal $provider $state } | Should -Throw '*provenance unavailable*'
    }
    It 'records partial failure separately from success for the exact generation' {
        [void](New-WinEnvGeneration $environment $provider $output)
        $generation = Assert-WinEnvGeneratedIntegrity $output
        $state = Join-Path $TestDrive 'attempt.json'
        Write-WinEnvGenerationAttempt -Path $state -Generation $generation -ProjectVersion 0.7.0 -BundleHash ('a'*64) -Feature core -Outcome success -Completed powershellProfile
        (Get-WinEnvState $state).outcome | Should -BeExactly success
        Write-WinEnvGenerationAttempt -Path $state -Generation $generation -ProjectVersion 0.7.0 -BundleHash ('a'*64) -Feature core -Outcome failed -Completed Microsoft.PowerShell
        $result = Get-WinEnvState $state
        $result.generationIdentity | Should -BeExactly $generation.identity
        $result.outcome | Should -BeExactly failed
        $result.appliedAtUtc | Should -BeNullOrEmpty
        ($result.completed -join ',') | Should -BeExactly Microsoft.PowerShell
    }
    It 'writes only the chosen JsonSubset projection and leaves unmanaged application keys' {
        $source = Join-Path $TestDrive 'payload.json'
        $target = Join-Path $TestDrive 'application.json'
        [IO.File]::WriteAllText($source, '{"owned":{"value":7,"list":[1]},"hostChoice":true}')
        [IO.File]::WriteAllText($target, '{"owned":{"value":2,"list":[9,8],"external":4},"outside":{"keep":true}}')
        Set-WinEnvManagedFile -Definition @{ Source = 'payload.json'; Target = $target; Compare = 'JsonSubset' } -RepositoryRoot $TestDrive
        $actual = Read-WinEnvContractJson $target
        $actual.owned.value | Should -Be 7
        ($actual.owned.list -join ',') | Should -BeExactly '1'
        $actual.owned.external | Should -Be 4
        $actual.outside.keep | Should -BeTrue
        $actual.hostChoice | Should -BeTrue
        [IO.File]::WriteAllText($target, '{invalid')
        { Set-WinEnvManagedFile -Definition @{ Source = 'payload.json'; Target = $target; Compare = 'JsonSubset' } -RepositoryRoot $TestDrive } | Should -Throw
        [IO.File]::ReadAllText($target) | Should -BeExactly '{invalid'
    }
}

Describe 'Generated reconciliation fixture' {
    # INV windows/host-generation-bound
    BeforeEach {
        New-FixtureEnvironment -Units @{ powershellProfile = @{ enabled = $false } }
        if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Recurse -Force }
        [void](New-WinEnvGeneration $environment $provider $output)
        $savedLocal = $env:LOCALAPPDATA
        $savedRequired = $env:REQUIRE_NATIVE
        $env:LOCALAPPDATA = Join-Path $TestDrive ('appdata-' + [guid]::NewGuid().ToString('N'))
        $env:REQUIRE_NATIVE = $null
        $setup = Join-Path $windowsRoot 'tool/setup.ps1'
        Mock Import-Module {}
        Mock Get-Command { [pscustomobject]@{ Source = 'fixture-winget' } } -ParameterFilter { $Name -eq 'winget.exe' }
        Mock Enter-WinEnvLock { [pscustomobject]@{} }
        Mock Exit-WinEnvLock {}
        Mock Get-WinEnvWindowsBuild { 19044 }
        Mock Get-WinEnvPackageStatus {
            param($Package)
            [pscustomobject]@{ Id = $Package.Id; Registered = $true; Detected = $true; Unverified = $null; Conflict = $false; Missing = $false }
        }
        Mock Test-WinEnvFeaturePrecondition { [pscustomobject]@{ Failures = @(); Unverified = @() } }
        Mock Update-WinEnvProcessPath {}
        Mock Get-WinEnvPowerShellProfilePath { throw 'disabled profile hook must not be accessed' }
        Mock Test-WinEnvProfileHook { throw 'disabled profile hook must not be checked' }
        Mock Set-WinEnvProfileHook { throw 'disabled profile hook must not be written' }
        Mock Install-WinEnvPackage { throw 'already present fixture package must not install' }
        Mock Set-WinEnvTerminalDelegation { throw 'excluded capability must not be written' }
        Mock Test-WinEnvTerminalDelegation { throw 'excluded capability must not be queried' }
    }
    AfterEach {
        $env:LOCALAPPDATA = $savedLocal
        $env:REQUIRE_NATIVE = $savedRequired
    }
    It 'Check remains read-only and disabled profile hooks are absent from observation' {
        & $setup -Generation $output -Check *> (Join-Path $TestDrive 'check.log')
        $LASTEXITCODE | Should -Be 2
        (Test-Path -LiteralPath (Join-Path $env:LOCALAPPDATA 'win-env/state.json')) | Should -BeFalse
        Should -Invoke Test-WinEnvProfileHook -Times 0 -Exactly
        Should -Invoke Set-WinEnvProfileHook -Times 0 -Exactly
    }
    It 'Apply in the fixture records success without disabled hook or package writes' {
        & $setup -Generation $output *> (Join-Path $TestDrive 'apply.log')
        $LASTEXITCODE | Should -Be 0
        $state = Get-WinEnvState (Join-Path $env:LOCALAPPDATA 'win-env/state.json')
        $state.outcome | Should -BeExactly success
        $state.generationIdentity | Should -BeExactly (Assert-WinEnvGeneratedIntegrity $output).identity
        Should -Invoke Set-WinEnvProfileHook -Times 0 -Exactly
        Should -Invoke Install-WinEnvPackage -Times 0 -Exactly
    }
    It 'stale originals and selector flags refuse before reconciliation or first write' {
        [IO.File]::AppendAllText($environment, ' ')
        & $setup -Generation $output *> (Join-Path $TestDrive 'stale.log')
        $LASTEXITCODE | Should -Be 1
        Should -Invoke Get-WinEnvPackageStatus -Times 0 -Exactly
        Should -Invoke Update-WinEnvProcessPath -Times 0 -Exactly
        & $setup -Generation $output -All *> (Join-Path $TestDrive 'selector.log')
        $LASTEXITCODE | Should -Be 1
        (Test-Path -LiteralPath (Join-Path $env:LOCALAPPDATA 'win-env/state.json')) | Should -BeFalse
    }
    It 'partial fixture Apply replaces a prior success claim with failed outcome' {
        & $setup -Generation $output *> (Join-Path $TestDrive 'first-apply.log')
        $LASTEXITCODE | Should -Be 0
        Mock Update-WinEnvProcessPath { throw 'synthetic partial failure' }
        & $setup -Generation $output -Force *> (Join-Path $TestDrive 'failed-apply.log')
        $LASTEXITCODE | Should -Be 1
        $state = Get-WinEnvState (Join-Path $env:LOCALAPPDATA 'win-env/state.json')
        $state.outcome | Should -BeExactly failed
        $state.appliedAtUtc | Should -BeNullOrEmpty
    }
    It 'terminal remains selected while excluded delegation is neither observed nor written' {
        Mock Test-WinEnvSourceFile -ModuleName WinEnvGeneration { $null }
        New-FixtureEnvironment -Features terminal -Units @{ powershellProfile = @{ enabled = $false } }
        [void](New-WinEnvGeneration $environment $provider $output)
        Mock Test-WinEnvSourceFile { $null }
        Mock Test-WinEnvManagedFile { $true }
        Mock Set-WinEnvManagedFile {}
        Mock Backup-WinEnvFile {}
        Mock Get-WinEnvFontStatus { [pscustomobject]@{ Conflict=$false; Incomplete=$false; RegistrationRepairable=$false; Missing=$false; Installed=$true } }
        Mock Test-WinEnvWindowsTerminalFontCache { $true }
        $log = Join-Path $TestDrive 'terminal-check.log'
        & $setup -Generation $output -Check *> $log
        $LASTEXITCODE | Should -Be 2
        [IO.File]::ReadAllText($log) | Should -Match 'excluded capability: defaultTerminalDelegation'
        Should -Invoke Test-WinEnvTerminalDelegation -Times 0 -Exactly
        & $setup -Generation $output *> (Join-Path $TestDrive 'terminal-apply.log')
        $LASTEXITCODE | Should -Be 0
        Should -Invoke Set-WinEnvTerminalDelegation -Times 0 -Exactly
    }
}

Describe 'Generation edge and compatibility fixtures' {
    # INV windows/host-generation-bound
    # INV windows/support-boundary-named
    BeforeEach { New-FixtureEnvironment }
    AfterEach { Clear-FixtureGitObjectReadOnly }
    It 'future optional features remain unselected and schema 1 export uses its historical manifest' {
        $future = Join-Path $TestDrive 'future-provider'
        Copy-Item -LiteralPath $provider -Destination $future -Recurse
        $path = Join-Path $future 'windows/desired/manifest.json'
        $manifest = Read-WinEnvContractJson $path
        $manifest.Features += @{ Id = 'futureOptional'; Name = 'Synthetic future optional feature' }
        Write-FixtureJson $path $manifest
        & git -C $future add windows/desired/manifest.json
        & git -C $future -c user.name=Fixture -c user.email=fixture@example.invalid -c core.hooksPath=disabled commit -qm 'fixture future feature'
        $futureCommit = (& git -C $future rev-parse HEAD).Trim()
        $value = Read-WinEnvContractJson $environment
        $value.provider.commit = $futureCommit
        Write-FixtureJson $environment $value
        ((Get-WinEnvEnvironmentPlan $environment $future).Selection.Selected -join ',') | Should -BeExactly core
        $legacy = Join-Path $TestDrive 'historical-selection.json'
        Write-FixtureJson $legacy @{ schemaVersion=1; projectVersion='0.6.0'; appliedAtUtc='2026-01-01T00:00:00Z'; gitCommit=$commit }
        (Get-WinEnvLegacySelectionProposal $future $legacy).environment.features | Should -Not -Contain futureOptional
    }
    It 'unselected documents retain structure checks and refuse incompatible payload on reselection' {
        Write-FixtureJson (Join-Path $originals 'inactive.json') @{ formatVersion=1; source='host'; settings='string instead of Json object' }
        New-FixtureEnvironment -Units @{ awake=@{ enabled=$true; document='inactive.json' } }
        ((Get-WinEnvEnvironmentPlan $environment $provider).Selection.Selected -join ',') | Should -BeExactly core
        New-FixtureEnvironment -Features powertoys -Units @{ awake=@{ enabled=$true; document='inactive.json' } }
        { Get-WinEnvEnvironmentPlan $environment $provider } | Should -Throw '*requires object settings*'
    }
    It 'refuses symbolic-link/junction connections without reading or changing outside documents' {
        $external = Join-Path $TestDrive 'outside'
        [void](New-Item -ItemType Directory $external)
        Write-FixtureJson (Join-Path $external 'settings.json') @{ formatVersion=1; source='configs'; settings=$null }
        $link = Join-Path $originals 'linked'
        $kind = if ($IsWindows) { 'Junction' } else { 'SymbolicLink' }
        [void](New-Item -ItemType $kind -Path $link -Target $external)
        New-FixtureEnvironment -Units @{ powershellProfile=@{ enabled=$true; document='linked/settings.json' } }
        { Get-WinEnvEnvironmentPlan $environment $provider } | Should -Throw '*symbolic link/reparse*'
    }
    It 'refuses modified source tools and unsupported provider formats before generation' {
        $changed = Join-Path $TestDrive 'changed-provider'
        Copy-Item -LiteralPath $provider -Destination $changed -Recurse
        [IO.File]::AppendAllText((Join-Path $changed 'windows/tool/consumer.ps1'), '# changed')
        { Get-WinEnvConsumerContract $changed } | Should -Throw '*differ from the pinned commit*'
        & git -C $changed add windows/tool/consumer.ps1
        & git -C $changed -c user.name=Fixture -c user.email=fixture@example.invalid -c core.hooksPath=disabled commit -qm 'fixture tool change'
        { Get-WinEnvConsumerContract $changed } | Should -Throw '*execution tools differ*'
        Copy-Item -LiteralPath (Join-Path $provider 'windows/tool/consumer.ps1') -Destination (Join-Path $changed 'windows/tool/consumer.ps1') -Force
        & git -C $changed add windows/tool/consumer.ps1
        & git -C $changed -c user.name=Fixture -c user.email=fixture@example.invalid -c core.hooksPath=disabled commit -qm 'fixture restore entry'
        $format = Join-Path $changed 'windows/tool/consumer-format.json'
        $record = Read-WinEnvContractJson $format
        $record.environment = 2
        Write-FixtureJson $format $record
        & git -C $changed add windows/tool/consumer-format.json
        & git -C $changed -c user.name=Fixture -c user.email=fixture@example.invalid -c core.hooksPath=disabled commit -qm 'fixture future format'
        { Get-WinEnvConsumerContract $changed } | Should -Throw '*formatVersion*'
    }
    It 'refuses a different imported provider module even with an identical generation module' {
        $changed = Join-Path $TestDrive 'module-provider'
        Copy-Item -LiteralPath $provider -Destination $changed -Recurse
        [IO.File]::AppendAllText((Join-Path $changed 'windows/src/WinEnv.psm1'), '# different imported module')
        & git -C $changed add windows/src/WinEnv.psm1
        & git -C $changed -c user.name=Fixture -c user.email=fixture@example.invalid -c core.hooksPath=disabled commit -qm 'fixture different module'
        (Get-WinEnvFileDigest (Join-Path $changed 'windows/src/WinEnvGeneration.psm1')) | Should -BeExactly (Get-WinEnvFileDigest (Join-Path $provider 'windows/src/WinEnvGeneration.psm1'))
        { Get-WinEnvConsumerContract $changed } | Should -Throw '*execution tools differ*WinEnv.psm1*'
    }
    It 'refuses status-hidden provider edits through <Flag>' -ForEach @(
        @{ Flag='--assume-unchanged' }, @{ Flag='--skip-worktree' }
    ) {
        $changed = Join-Path $TestDrive ('flag-provider-' + $Flag.TrimStart('-'))
        Copy-Item -LiteralPath $provider -Destination $changed -Recurse
        & git -C $changed update-index $Flag windows/desired/files/powershell/profile.ps1
        $LASTEXITCODE | Should -Be 0
        [IO.File]::AppendAllText((Join-Path $changed 'windows/desired/files/powershell/profile.ps1'), '# hidden edit')
        (& git -C $changed status --porcelain -- windows | Out-String).Trim() | Should -BeNullOrEmpty
        { Get-WinEnvConsumerContract $changed } | Should -Throw '*index flags*'
    }
    It 'accepts UTF-8 BOM and refuses malformed UTF-8 or UTF-16 before generation' {
        $text = [IO.File]::ReadAllText($environment)
        [IO.File]::WriteAllText($environment, $text, [Text.UTF8Encoding]::new($true))
        (Get-WinEnvEnvironmentPlan $environment $provider).Source.Commit | Should -BeExactly $commit
        [IO.File]::WriteAllBytes($environment, [byte[]](123,34,120,34,58,34,195,40,34,125))
        { New-WinEnvGeneration $environment $provider $output } | Should -Throw '*strict UTF-8*'
        (Test-Path -LiteralPath $output) | Should -BeFalse
        [IO.File]::WriteAllText($environment, $text, [Text.Encoding]::Unicode)
        { New-WinEnvGeneration $environment $provider $output } | Should -Throw '*strict UTF-8*'
        (Test-Path -LiteralPath $output) | Should -BeFalse
        New-FixtureEnvironment -Units @{ powershellProfile=@{ enabled=$true; document='malformed-settings.json' } }
        [IO.File]::WriteAllText((Join-Path $originals 'malformed-settings.json'), '{"formatVersion":1,"source":"configs","settings":null}', [Text.Encoding]::Unicode)
        { New-WinEnvGeneration $environment $provider $output } | Should -Throw '*strict UTF-8*'
        (Test-Path -LiteralPath $output) | Should -BeFalse
    }
    It 'preserves externally generated Terminal profiles on whole-unit writes' {
        $source = Join-Path $TestDrive 'terminal-payload.json'
        $target = Join-Path $TestDrive 'terminal-app.json'
        [IO.File]::WriteAllText($source, '{"profiles":{"list":[{"guid":"owned","name":"new"}]}}')
        [IO.File]::WriteAllText($target, '{"profiles":{"list":[{"guid":"owned","name":"old"},{"guid":"dynamic","source":"externalGenerator","name":"keep"}]}}')
        Set-WinEnvManagedFile -Definition @{ Source='terminal-payload.json'; Target=$target; Compare='ExactJsonWithGeneratedProfiles' } -RepositoryRoot $TestDrive
        $value = Read-WinEnvContractJson $target
        ($value.profiles.list | Where-Object guid -CEQ owned).name | Should -BeExactly new
        ($value.profiles.list | Where-Object guid -CEQ dynamic).name | Should -BeExactly keep
        (Test-WinEnvJsonWithGeneratedProfiles -Expected ([IO.File]::ReadAllText($source)) -Actual ([IO.File]::ReadAllText($target))) | Should -BeTrue
    }
    It 'preserves foreign PowerShell blocks and refuses unmatched owned markers' {
        $profile = Join-Path $TestDrive 'profile.ps1'
        $foreign = "#region ExternalOwner`n`$external = 4`n#endregion ExternalOwner"
        [IO.File]::WriteAllText($profile, $foreign)
        Set-WinEnvProfileHook $profile
        [IO.File]::ReadAllText($profile).Contains($foreign) | Should -BeTrue
        [IO.File]::WriteAllText($profile, $foreign + "`n#region win-env`n")
        $before = Get-WinEnvFileDigest $profile
        { Set-WinEnvProfileHook $profile } | Should -Throw '*unmatched*'
        (Get-WinEnvFileDigest $profile) | Should -BeExactly $before
    }
}

Describe 'Generation publication and public command fixtures' {
    # INV windows/host-generation-bound
    # INV windows/entry-point-forwards-status
    BeforeEach { New-FixtureEnvironment }
    It 'bootstrap selects the first actual PATH application and forwards its child status' {
        $executable = (Get-Process -Id $PID).Path
        $runtimeDigest = Get-WinEnvFileDigest $executable
        $first = Join-Path $TestDrive 'first-management'
        $second = Join-Path $TestDrive 'second-management'
        foreach ($candidate in @($first, $second)) {
            if ($IsWindows) {
                [void](New-Item -ItemType Junction -Path $candidate -Target (Split-Path -Parent $executable))
            }
            else {
                [void](New-Item -ItemType Directory -Path $candidate)
                [void](New-Item -ItemType SymbolicLink -Path (Join-Path $candidate 'pwsh.exe') -Target $executable)
            }
        }
        $fixtureRoot = Join-Path $TestDrive 'bootstrap-provider'
        $fixtureTools = Join-Path $fixtureRoot 'windows/tool'
        [void](New-Item -ItemType Directory -Path $fixtureTools -Force)
        [IO.File]::WriteAllText((Join-Path $fixtureRoot '.git'), 'gitdir: synthetic-linked-worktree')
        Copy-Item -LiteralPath (Join-Path $windowsRoot 'tool/bootstrap.ps1') -Destination $fixtureTools
        $marker = Join-Path $fixtureRoot 'forwarded.json'
        [IO.File]::WriteAllText((Join-Path $fixtureTools 'setup.ps1'), @'
param([switch]$Check, [string]$Generation)
[IO.File]::WriteAllText((Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'forwarded.json'), (@{ check=[bool]$Check; generation=$Generation } | ConvertTo-Json))
exit 37
'@)
        $previousPath = $env:PATH
        try {
            $wrapper = Join-Path $fixtureRoot 'path-probe.ps1'
            [IO.File]::WriteAllText($wrapper, @'
param([string]$First, [string]$Second, [string]$Bootstrap)
$ErrorActionPreference = 'Stop'
# A fresh PowerShell can prepend PSHOME. Arrange the competing PATH after
# startup so the actual command lookup under test sees these two candidates.
$env:PATH = $First + [IO.Path]::PathSeparator + $Second + [IO.Path]::PathSeparator + $env:PATH
$candidates = @(Get-Command pwsh.exe -CommandType Application -All)
if ($candidates.Count -lt 2 -or $candidates[0].Source -cne (Join-Path $First 'pwsh.exe')) { throw 'Fixture did not arrange two ordered actual applications.' }
& $Bootstrap -Generation synthetic-generation -Check -Verbose
exit $LASTEXITCODE
'@)
            $stdout = Join-Path $TestDrive 'bootstrap-path.stdout'
            & $executable -NoLogo -NoProfile -File $wrapper -First $first -Second $second -Bootstrap (Join-Path $fixtureTools 'bootstrap.ps1') > $stdout 2> (Join-Path $TestDrive 'bootstrap-path.stderr')
            $LASTEXITCODE | Should -Be 37
            ([IO.File]::ReadAllText($stdout)) | Should -Match ([regex]::Escape((Join-Path $first 'pwsh.exe')))
            $forwarded = Read-WinEnvContractJson $marker
            $forwarded.check | Should -BeTrue
            $forwarded.generation | Should -BeExactly synthetic-generation
        }
        finally {
            $env:PATH = $previousPath
            if ($IsWindows) {
                foreach ($candidate in @($first,$second)) {
                    if ((Test-Path -LiteralPath $candidate) -and ((Get-Item -LiteralPath $candidate -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
                        [IO.Directory]::Delete($candidate)
                    }
                }
            }
            (Test-Path -LiteralPath $executable -PathType Leaf) | Should -BeTrue
            (Get-WinEnvFileDigest $executable) | Should -BeExactly $runtimeDigest
            & $executable -NoLogo -NoProfile -Command 'exit 0' *> (Join-Path $TestDrive 'runtime-after-cleanup.log')
            $LASTEXITCODE | Should -Be 0
        }
    }
    It 'restores the prior directory when publication fails after moving it aside' {
        $current = Join-Path $TestDrive 'publish-current'
        $prepared = Join-Path $TestDrive 'publish-prepared'
        [void](New-Item -ItemType Directory $current)
        [void](New-Item -ItemType Directory $prepared)
        [IO.File]::WriteAllText((Join-Path $current 'preserved.txt'), 'previous applicable result')
        Mock Move-WinEnvGenerationDirectory -ModuleName WinEnvGeneration -ParameterFilter { $Source -like '*publish-prepared' } { throw 'synthetic publication failure' }
        { Publish-WinEnvGenerationDirectory $prepared $current } | Should -Throw '*publication failure*'
        [IO.File]::ReadAllText((Join-Path $current 'preserved.txt')) | Should -BeExactly 'previous applicable result'
    }
    It 'public inspect and malformed generation return explicit JSON success or failure status' {
        $executable = (Get-Process -Id $PID).Path
        $entry = Join-Path $windowsRoot 'win-env.ps1'
        $log = Join-Path $TestDrive 'inspect.stdout'
        & $executable -NoLogo -NoProfile -File $entry inspect -SourceRoot $provider > $log 2> (Join-Path $TestDrive 'inspect.stderr')
        $LASTEXITCODE | Should -Be 0
        (Read-WinEnvContractJson $log).provider.commit | Should -BeExactly $commit
        $value = Read-WinEnvContractJson $environment
        $value.formatVersion = 2
        Write-FixtureJson $environment $value
        & $executable -NoLogo -NoProfile -File $entry generate -SourceRoot $provider -Environment $environment -Output (Join-Path $TestDrive 'invalid-public-result') > (Join-Path $TestDrive 'generate.stdout') 2> (Join-Path $TestDrive 'generate.stderr')
        $LASTEXITCODE | Should -Be 1
        (Test-Path -LiteralPath (Join-Path $TestDrive 'invalid-public-result')) | Should -BeFalse
    }
    It 'refuses structurally forged generation enums and identities before comparison' {
        $generated = Join-Path $TestDrive 'shape-generation'
        [void](New-WinEnvGeneration $environment $provider $generated)
        $path = Join-Path $generated 'generation.json'
        $value = Read-WinEnvContractJson $path
        $value.units[0].source = @('configs')
        Write-FixtureJson $path $value
        { Assert-WinEnvGeneratedIntegrity $generated } | Should -Throw '*Invalid or duplicate generation unit*'
    }
}
