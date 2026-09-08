BeforeAll {
    $windowsRoot = Split-Path -Parent $PSScriptRoot
    Import-Module (Join-Path $windowsRoot 'src/WinEnv.psm1') -Force
}

Describe 'WSL capture prerequisites' {
    # INV windows/capture-source-policy
    # INV windows/support-boundary-named
    # INV windows/check-exit-contract
    BeforeAll {
        $originalRoot = Join-Path $windowsRoot 'desired'
        $manifest = Get-WinEnvManifest -Path (Join-Path $originalRoot 'manifest.json')
        $wsl = $manifest.ManagedFiles | Where-Object Id -eq 'wslConfig'
        $upperSource = $wsl.Sources[0].Source
        $lowerSource = $wsl.Sources[1].Source
        $upperText = Get-Content (Join-Path $originalRoot $upperSource) -Raw
        $lowerText = Get-Content (Join-Path $originalRoot $lowerSource) -Raw
        $wslRoot = Join-Path $TestDrive 'desired'
        [void](New-Item -ItemType Directory (Join-Path $wslRoot 'files/wsl') -Force)
        $wsl.Target = Join-Path $TestDrive '.wslconfig'
        function Invoke-WslCapture {
            param([AllowNull()][object] $Build = 22621, [string] $Content = $upperText,
                [AllowNull()][version] $Version = '2.2.1')
            [IO.File]::WriteAllText($wsl.Target, $Content)
            $before = @(Get-FileHash (Join-Path $wslRoot $upperSource), (Join-Path $wslRoot $lowerSource))
            $plan = Get-WinEnvCapturePlan -Definition $wsl -RepositoryRoot $wslRoot -Build $Build -WslVersion $Version
            $after = @(Get-FileHash (Join-Path $wslRoot $upperSource), (Join-Path $wslRoot $lowerSource))
            ($after.Hash -join ',') | Should -Be ($before.Hash -join ',')
            (Get-Content -LiteralPath $wsl.Target -Raw) | Should -BeExactly $Content
            return $plan
        }
    }
    BeforeEach {
        [IO.File]::WriteAllText((Join-Path $wslRoot $upperSource), $upperText)
        [IO.File]::WriteAllText((Join-Path $wslRoot $lowerSource), $lowerText)
    }

    It 'accepts matching content at each existing build boundary' -ForEach @(
        @{ Build = 19044; Upper = $false }, @{ Build = 22000; Upper = $false },
        @{ Build = 22620; Upper = $false }, @{ Build = 22621; Upper = $true },
        @{ Build = 26100; Upper = $true }
    ) {
        $text = if ($Upper) { $upperText } else { $lowerText }
        $source = if ($Upper) { $upperSource } else { $lowerSource }
        $plan = Invoke-WslCapture -Build $Build -Content $text
        $plan.Status | Should -Be 'Unchanged'
        $plan.Source | Should -Be $source
    }

    It 'refuses an unknown build with an undetermined-source reason' {
        $plan = Invoke-WslCapture -Build $null
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'build is undetermined'
    }

    It 'refuses modern keys below 22621, including Windows 11 build 22000' -ForEach @(
        @{ Build = 19045; Key = 'networkingMode'; Section = 'wsl2'; Value = 'Mirrored' },
        @{ Build = 22000; Key = 'hostAddressLoopback'; Section = 'experimental'; Value = 'true' },
        @{ Build = 22000; Key = 'bestEffortDnsParsing'; Section = 'experimental'; Value = 'false' },
        @{ Build = 19045; Key = 'dnsTunneling'; Section = 'wsl2'; Value = 'false' }
    ) {
        $plan = Invoke-WslCapture -Build $Build -Content "[$Section]`n$Key=$Value`n"
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match "unsupported setting $Section.$Key"
        $plan.Reason | Should -Match '22621'
        $plan.Reason | Should -Not -Match 'policy mismatch'
    }

    It 'refuses another network policy without calling it invalid Windows configuration' -ForEach @(
        @{ Text = "[wsl2]`nnetworkingMode=NAT`n" },
        @{ Text = "[wsl2]`nmemory=8GB`n" },
        @{ Text = "[wsl2]`nnetworkingMode=none`n" }
    ) {
        $plan = Invoke-WslCapture -Content $Text
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'desired-source-policy mismatch'
        $plan.Reason | Should -Match ([regex]::Escape($upperSource))
        $plan.Reason | Should -Match 'reviewed desired-state edit'
        $plan.Reason | Should -Not -Match 'unsupported setting'
    }

    It 'checks old or unknown application evidence before Unchanged' -ForEach @(
        @{ Build = 22621; Version = $null; Reason = 'version evidence is missing'; Upper = $true },
        @{ Build = 22621; Version = '2.0.4'; Reason = 'wsl2.networkingMode.*2.0.5'; Upper = $true },
        @{ Build = 19045; Version = '1.2.5'; Reason = 'experimental.autoMemoryReclaim.*2.0.0'; Upper = $false },
        @{ Build = 19045; Version = $null; Reason = 'version evidence is missing'; Upper = $false }
    ) {
        $text = if ($Upper) { $upperText } else { $lowerText }
        $plan = Invoke-WslCapture -Build $Build -Content $text -Version $Version
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match $Reason
    }

    It 'accepts the documented application and section boundaries' -ForEach @(
        @{ Build = 19045; Version = '2.0.0'; Legacy = $false },
        @{ Build = 22621; Version = '2.0.0'; Legacy = $true },
        @{ Build = 22621; Version = '2.0.5'; Legacy = $false }
    ) {
        $text = if ($Build -lt 22621) { $lowerText } elseif ($Legacy) {
            "[experimental]`nnetworkingMode=mirrored`ndnsTunneling=true`nhostAddressLoopback=true`nbestEffortDnsParsing=true`nautoMemoryReclaim=gradual`n"
        } else { $upperText }
        (Invoke-WslCapture -Build $Build -Content $text -Version $Version).Status | Should -BeIn @('Captured', 'Unchanged')
    }

    It 'refuses a known key in the wrong section' -ForEach @(
        @{ Key = 'autoMemoryReclaim'; Value = 'gradual' },
        @{ Key = 'bestEffortDnsParsing'; Value = 'true' },
        @{ Key = 'hostAddressLoopback'; Value = 'true' }
    ) {
        $plan = Invoke-WslCapture -Content "[wsl2]`nnetworkingMode=mirrored`n$Key=$Value`n"
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match "unsupported setting wsl2.$Key"
    }

    It 'accepts explicitly inactive DNS options and preserves comments, case and whitespace' {
        $text = "# keep my tuning`r`n[WsL2]`r`n NetworkingMode = `"MiRrOrEd`" # network`r`n dnsTunneling = FALSE`r`n memory=8GB`r`n processors=4`r`n[Experimental]`r`n bestEffortDnsParsing = TRUE`r`n autoMemoryReclaim = Gradual`r`n"
        $plan = Invoke-WslCapture -Content $text
        $plan.Status | Should -Be 'Captured'
        $plan.Content | Should -BeExactly $text
        ($plan.Information -join '; ') | Should -Match 'inactive because dnsTunneling=false'
        [IO.File]::WriteAllText((Join-Path $wslRoot $plan.Source), $plan.Content)
        (Invoke-WslCapture -Content $text).Status | Should -Be 'Unchanged'
        ((Invoke-WslCapture -Content $text).Information -join '; ') | Should -Match 'inactive'
        (Get-Content (Join-Path $wslRoot $lowerSource) -Raw) | Should -BeExactly $lowerText
    }

    It 'preserves an inline comment containing backslashes after an ordinary scalar' {
        $text = $upperText.Replace('networkingMode=Mirrored', 'networkingMode=Mirrored # see C:\temp\wsl')
        $plan = Invoke-WslCapture -Content $text
        $plan.Status | Should -Be 'Captured'
        $plan.Content | Should -BeExactly $text
    }

    It 'keeps quoted trailing whitespace significant for the selected network policy' {
        $plan = Invoke-WslCapture -Content "[wsl2]`nnetworkingMode=mirrored `"`"`n"
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'desired-source-policy mismatch'
        (Invoke-WslCapture -Content "[wsl2]`nnetworkingMode=`"mirrored`"   # space outside quotes`n").Status | Should -Be 'Captured'
    }

    It 'reports an omitted DNS dependency without guessing its historical default' -ForEach @('2.0.5', '2.1.0', '2.1.1', '2.2.1') {
        $plan = Invoke-WslCapture -Version $_
        $plan.Status | Should -Be 'Unchanged'
        ($plan.Information -join '; ') | Should -Match 'dnsTunneling is omitted'
        ($plan.Information -join '; ') | Should -Not -Match 'dependency is enabled'
    }

    It 'preserves compatible lower-payload tuning and unmodelled keys without certifying them' {
        $text = "[wsl2]`nmemory=8GB`nprocessors=4`nfutureOption=custom`n$lowerText"
        $plan = Invoke-WslCapture -Build 22000 -Content $text
        $plan.Status | Should -Be 'Captured'
        $plan.Source | Should -Be $lowerSource
        $plan.Content | Should -BeExactly $text
        ($plan.Information -join '; ') | Should -Match 'futureOption.*without a support claim'
        [IO.File]::WriteAllText((Join-Path $wslRoot $plan.Source), $plan.Content)
        (Invoke-WslCapture -Build 22000 -Content $text).Status | Should -Be 'Unchanged'
        (Get-Content (Join-Path $wslRoot $upperSource) -Raw) | Should -BeExactly $upperText
    }

    It 'uses the first mode occurrence across legacy aliases and preserves duplicate text' {
        $text = "[experimental]`nnetworkingMode=mirrored`n[wsl2]`nnetworkingMode=nat`n"
        $plan = Invoke-WslCapture -Content $text
        $plan.Status | Should -Be 'Captured'
        $plan.Content | Should -BeExactly $text
        ($plan.Information -join '; ') | Should -Match 'first occurrence'
        (Invoke-WslCapture -Content "[wsl2]`nnetworkingMode=nat`n[experimental]`nnetworkingMode=mirrored`n").Status | Should -Be 'Refused'
    }

    It 'keeps a known version unnecessary for ordinary memory and CPU tuning alone' {
        (Invoke-WslCapture -Build 19045 -Content "[wsl2]`nmemory=8GB`nprocessors=4`n" -Version $null).Status | Should -Be 'Captured'
    }

    It 'keeps drift independent of unverified prerequisites in the real check collection loop' -ForEach @(
        @{ Drifted = $false; Native = $false; Expected = 69 },
        @{ Drifted = $true; Native = $false; Expected = 2 },
        @{ Drifted = $false; Native = $true; Expected = 1 },
        @{ Drifted = $true; Native = $true; Expected = 1 }
    ) {
        $desiredStateRoot = $wslRoot
        $hostBuild = 22621
        $managedFiles = @(Resolve-WinEnvManagedFile -Definition $wsl -Build $hostBuild)
        $text = if ($Drifted) { "$upperText`n# drift" } else { $upperText }
        [IO.File]::WriteAllText($wsl.Target, $text)
        $Check = $true
        $drift = [System.Collections.Generic.List[string]]::new()
        $unverified = [System.Collections.Generic.List[string]]::new()
        $wslInformation = [System.Collections.Generic.List[string]]::new()
        Mock Get-WinEnvWslVersion { $null }
        # Run the actual collector without the rest of setup's package,
        # registry and lifecycle operations. Observations are injected; no
        # Windows process, Apply or WSL restart is part of this fixture.
        $ast = [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $windowsRoot 'tools/setup.ps1'), [ref]$null, [ref]$null)
        $loop = $ast.Find({ param($node)
                $node -is [System.Management.Automation.Language.ForEachStatementAst] -and
                $node.Extent.Text.StartsWith('foreach ($definition in $managedFiles)')
            }, $true)
        $loop | Should -Not -BeNullOrEmpty
        . ([scriptblock]::Create($loop.Extent.Text))
        $unverified.Count | Should -BeGreaterThan 0
        $drift.Count | Should -Be ([int]$Drifted)
        (Get-WinEnvCheckStatus -DriftCount $drift.Count -UnverifiedCount $unverified.Count -RequireNative:$Native) | Should -Be $Expected
        ($wslInformation -join '; ') | Should -Match 'source agreement:.*runtime effect: unverified'
    }

    It 'reads the localized WSL application line and ignores other version numbers' -ForEach @(
        @{ Label = 'WSL version' }, @{ Label = 'WSL 버전' }
    ) {
        $query = { "${Label}: 2.2.1.0"; 'WSLg version: 1.0.60'; 'Kernel version: 5.15.146.1'; 'Windows version: 10.0.22631.0' }.GetNewClosure()
        (Get-WinEnvWslVersion -VersionQuery $query) | Should -Be ([version]'2.2.1.0')
    }

    It 'does not guess a version from legacy status, failed queries or missing output' -ForEach @(
        @{ Query = { 'Default Version: 2'; 'Kernel version: 5.15.146.1' } },
        @{ Query = { 'WSLg version: 1.0.60' } },
        @{ Query = { throw 'query failed' } },
        @{ Query = {} },
        @{ Query = { 'WSL version: 0.0.0' } },
        @{ Query = { 'WSL version: 2.0.5'; 'WSL version: 2.2.1' } }
    ) {
        Get-WinEnvWslVersion -VersionQuery $Query | Should -BeNullOrEmpty
    }
}
