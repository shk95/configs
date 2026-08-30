BeforeAll {
    $testsRoot = Split-Path -Parent $PSCommandPath
    $repositoryRoot = Split-Path -Parent $testsRoot
    $monorepoRoot = Split-Path -Parent $repositoryRoot
    $desiredStateRoot = Join-Path $repositoryRoot 'desired'
    Import-Module (Join-Path $repositoryRoot 'src\WinEnv.psm1') -Force

    function Test-Throws {
        param([scriptblock] $ScriptBlock)
        try { & $ScriptBlock; return $false } catch { return $true }
    }

    # A synthetic manifest keeps the feature-model rules testable without
    # asserting them against the repository's own current selection, which is
    # allowed to change without changing the rules.
    function New-FeatureManifest {
        param([hashtable] $Override = @{})
        $manifest = @{
            SchemaVersion  = 3
            ProjectVersion = '1.0.0'
            Features       = @(
                @{ Id = 'core'; Name = 'Core'; Required = $true },
                @{ Id = 'font'; Name = 'Font' },
                @{ Id = 'zellij'; Name = 'Zellij' },
                @{ Id = 'terminal'; Name = 'Terminal'; Requires = @('font', 'zellij') }
            )
            Packages       = @(
                @{ Id = 'Vendor.Shell'; Feature = 'core'; Bootstrap = $true; Detection = 'Command'; Command = 'pwsh.exe' }
            )
            ManagedFiles   = @(
                @{ Id = 'profile'; Feature = 'core'; Source = 'files/profile.ps1'; Target = 'profile'; Compare = 'Text'; Parser = 'PowerShell' },
                @{ Id = 'terminalSettings'; Feature = 'terminal'; Source = 'files/settings.json'; Target = 'settings'; Compare = 'ExactJson'; Parser = 'Json' }
            )
            Font           = @{ Feature = 'font'; Name = 'Test Font' }
            Terminal       = @{ Feature = 'terminal' }
        }
        foreach ($key in $Override.Keys) { $manifest[$key] = $Override[$key] }
        return $manifest
    }

    # A leaked Windows account path can appear in two spellings depending on
    # the payload's file format, and both are deliberate, not accidental:
    #   - Raw text (PowerShell, Lua, .lua.example templates, INI, KDL) carries
    #     the Windows path separator once, e.g. C:\Users\<name>.
    #   - A JSON payload escapes its own separators, so the same leak appears
    #     in the file's raw bytes as C:\\Users\\<name>, two literal backslashes.
    # This is a PowerShell single-quoted string, so it is not itself escaped;
    # every backslash below is a literal character handed straight to the
    # regex engine. `\\` (two literal backslash characters) is that engine's
    # own escape for one literal backslash, so `\\{1,2}` matches one or two
    # literal backslashes and covers both spellings in one pattern. `(?i)`
    # makes the match explicitly case-insensitive rather than relying on
    # -Match's default behaviour.
    #
    # Self-match exclusion rule: this pattern is only ever evaluated against
    # content read from windows/desired/files (the payload tree). The file
    # that declares the pattern lives under windows/tests/ and is never part
    # of that scan, so the scanner cannot match its own source text. Keep any
    # fixture that exercises this pattern under windows/desired/files (or a
    # $TestDrive stand-in for it), never under windows/tests/, or that
    # exclusion stops holding by construction.
    $WindowsHomePathPattern = '(?i)C:\\{1,2}Users\\{1,2}[A-Za-z0-9._-]+'
}

Describe 'win-env manifest' {
    It 'loads schema 3 and the desired-state compatibility version' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $manifest.SchemaVersion | Should -Be 3
        $manifest.ProjectVersion | Should -Be '0.4.0'
    }

    It 'pins the v3.5.0 D2Koding asset and hashes' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $manifest.Font.Version | Should -Be '3.5.0'
        $manifest.Font.Name | Should -Be 'D2KodingLigature Nerd Font Mono'
        $manifest.Font.Sha256 | Should -Match '^[0-9a-f]{64}$'
        $manifest.Font.Files.Count | Should -Be 2
    }

    It 'uses exact expected WinGet IDs' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        (($manifest.Packages.Id | Sort-Object) -join ',') | Should -Be 'Microsoft.PowerShell,Microsoft.PowerToys,Microsoft.WindowsTerminal,wez.wezterm,Zellij.Zellij'
    }

    It 'connects the Terminal profile to the pinned font and GUIDs' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $terminal = Get-Content (Join-Path $desiredStateRoot 'files\terminal\settings.json') -Raw | ConvertFrom-Json
        $terminal.defaultProfile | Should -Be $manifest.Terminal.DefaultProfileGuid
        $terminal.profiles.defaults.font.face | Should -Be $manifest.Font.Name
        ($terminal.profiles.list | Where-Object name -eq 'Zellij Workspace').guid | Should -Be $manifest.Terminal.ZellijProfileGuid
    }

    It 'splits the Windows-side WSL configuration by the build each key needs' {
        # Reworked from the single-payload assertion this replaces. The four
        # keys did not all move together, so asserting them against one source
        # would now pin the wrong thing: three carry Microsoft's "require
        # Windows 11 version 22H2 or higher" footnote and one carries no
        # footnote at all. Every assertion below traces to a row of the per-key
        # gate table in docs/status.md.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $wsl = $manifest.ManagedFiles | Where-Object Id -eq 'wslConfig'
        $wsl.Target | Should -Be '{USERPROFILE}\.wslconfig'
        $wsl.Feature | Should -Be 'wsl'
        $wsl.Parser | Should -Be 'Ini'
        # One entry with alternative sources, not two entries competing for one
        # Target, so drift, backup and deselection still see one logical file.
        $wsl.ContainsKey('Source') | Should -Be $false
        $wsl.Sources.Count | Should -Be 2

        $mirrored = Get-Content (Join-Path $desiredStateRoot 'files/wsl/mirrored-networking.wslconfig') -Raw
        $nat = Get-Content (Join-Path $desiredStateRoot 'files/wsl/nat-networking.wslconfig') -Raw

        # At or above the bound: every key, and this is the content this
        # repository already deployed.
        $mirrored | Should -Match '(?m)^networkingMode=Mirrored$'
        $mirrored | Should -Match '(?m)^hostAddressLoopback=true$'
        $mirrored | Should -Match '(?m)^bestEffortDnsParsing=true$'
        $mirrored | Should -Match '(?m)^autoMemoryReclaim=Gradual$'

        # Below the bound: no key gated on Windows 11 22H2 survives, including
        # networkingMode in any spelling, because the host would ignore it in
        # silence rather than report it.
        $nat | Should -Not -Match '(?m)^networkingMode='
        $nat | Should -Not -Match '(?m)^hostAddressLoopback='
        $nat | Should -Not -Match '(?m)^bestEffortDnsParsing='
        # autoMemoryReclaim carries no Windows footnote: it is gated by the
        # installed WSL application, so it stays. Dropping it here would remove
        # a setting the host honours, a regression dressed as a version fix.
        $nat | Should -Match '(?m)^autoMemoryReclaim=Gradual$'

        # AGENTS.md: no .wslconfig firewall value without explicit direction.
        $mirrored | Should -Not -Match '(?m)^firewall\s*='
        $nat | Should -Not -Match '(?m)^firewall\s*='
    }
}

Describe 'version gate' {
    It 'orders repository versions correctly' {
        (Compare-WinEnvVersion -RepositoryVersion '0.1.0' -AppliedVersion '0.0.0') | Should -BeGreaterThan 0
        (Compare-WinEnvVersion -RepositoryVersion '0.1.0' -AppliedVersion '0.1.0') | Should -Be 0
        (Compare-WinEnvVersion -RepositoryVersion '0.1.0' -AppliedVersion '0.2.0') | Should -BeLessThan 0
    }

    It 'rejects an invalid semantic version' {
        (Test-Throws { Compare-WinEnvVersion -RepositoryVersion 'not-semver' -AppliedVersion '0.1.0' }) | Should -Be $true
    }
}

Describe 'JSON ownership' {
    It 'allows runtime properties in subset mode' {
        $expected = '{"enabled":true,"nested":{"value":7}}' | ConvertFrom-Json
        $actual = '{"enabled":true,"nested":{"value":7,"runtime":"ignored"},"version":"dynamic"}' | ConvertFrom-Json
        (Test-WinEnvJsonSubset -Expected $expected -Actual $actual) | Should -Be $true
    }

    It 'detects changed managed properties' {
        $expected = '{"enabled":true,"items":[1,2]}' | ConvertFrom-Json
        $actual = '{"enabled":false,"items":[1,2]}' | ConvertFrom-Json
        (Test-WinEnvJsonSubset -Expected $expected -Actual $actual) | Should -Be $false
    }
}

Describe 'PowerShell profile marker' {
    It 'adds one block and preserves existing external blocks' {
        $profile = Join-Path $TestDrive 'profile.ps1'
        [IO.File]::WriteAllText($profile, "#region sysmon-banner`r`n'SysMon'`r`n#endregion sysmon-banner`r`n")
        Set-WinEnvProfileHook -ProfilePath $profile
        Set-WinEnvProfileHook -ProfilePath $profile
        $content = Get-Content -LiteralPath $profile -Raw
        ([regex]::Matches($content, '(?m)^#region win-env\r?$')).Count | Should -Be 1
        $content | Should -Match '#region sysmon-banner'
        (Test-WinEnvProfileHook -ProfilePath $profile) | Should -Be $true
    }

    It 'refuses unmatched markers' {
        $profile = Join-Path $TestDrive 'broken-profile.ps1'
        [IO.File]::WriteAllText($profile, "#region win-env`r`n")
        (Test-Throws { Set-WinEnvProfileHook -ProfilePath $profile }) | Should -Be $true
    }
}

Describe 'managed PowerShell profile' {
    It 'loads silently in a non-interactive PowerShell process' {
        $profile = Join-Path $desiredStateRoot 'files\powershell\profile.ps1'
        $pwsh = (Get-Process -Id $PID).Path
        $output = @(& $pwsh -NoLogo -NoProfile -NonInteractive -File $profile 2>&1)
        $LASTEXITCODE | Should -Be 0
        $output.Count | Should -Be 0
    }
}

Describe 'state safety' {
    It 'resolves the repository commit without trusting Windows Git safe-directory state' {
        (Get-WinEnvGitCommit -RepositoryRoot $monorepoRoot) | Should -Match '^(unborn|[0-9a-f]{40})$'
    }

    It 'treats a missing state as uninitialized' {
        (Get-WinEnvState -Path (Join-Path $TestDrive 'missing.json')) | Should -Be $null
    }

    It 'rejects corrupt state instead of applying' {
        $path = Join-Path $TestDrive 'state.json'
        [IO.File]::WriteAllText($path, '{broken')
        (Test-Throws { Get-WinEnvState -Path $path }) | Should -Be $true
    }

    It 'atomically writes valid state' {
        $path = Join-Path $TestDrive 'state\state.json'
        $fontRegisteredAtUtc = '2026-08-10T07:42:46.5260930+00:00'
        $desiredStateHash = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
        Write-WinEnvState -Path $path -ProjectVersion '0.1.0' -GitCommit '0123456789abcdef' -DesiredStateHash $desiredStateHash -Feature @('core', 'font') -FontRegisteredAtUtc $fontRegisteredAtUtc
        $state = Get-WinEnvState -Path $path
        $state.schemaVersion | Should -Be 2
        $state.projectVersion | Should -Be '0.1.0'
        $state.gitCommit | Should -Be '0123456789abcdef'
        $state.bundleHash | Should -Be $desiredStateHash
        (@($state.features) -join ',') | Should -Be 'core,font'
        ([DateTimeOffset]$state.fontRegisteredAtUtc).UtcTicks | Should -Be ([DateTimeOffset]$fontRegisteredAtUtc).UtcTicks
    }

    It 'refuses a schema 2 state that records no selection' {
        $path = Join-Path $TestDrive 'selectionless.json'
        [IO.File]::WriteAllText($path, '{"schemaVersion":2,"projectVersion":"0.1.0","appliedAtUtc":"2026-01-01T00:00:00+00:00","gitCommit":"0123456789abcdef"}')
        (Test-Throws { Get-WinEnvState -Path $path }) | Should -Be $true
    }

    It 'changes the desired-state hash when content changes' {
        $manifest = New-FeatureManifest
        $root = Join-Path $TestDrive 'desired'
        [void](New-Item -ItemType Directory -Path (Join-Path $root 'files') -Force)
        [IO.File]::WriteAllText((Join-Path $root 'manifest.json'), '{}')
        [IO.File]::WriteAllText((Join-Path $root 'files\profile.ps1'), 'core')
        $before = Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core')
        [IO.File]::WriteAllText((Join-Path $root 'files\profile.ps1'), 'changed')
        $after = Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core')
        $before | Should -Match '^[0-9a-f]{64}$'
        $after | Should -Match '^[0-9a-f]{64}$'
        $after | Should -Not -Be $before
    }

    It 'ignores a payload the selection excludes' {
        # A whole-tree hash reported drift for material this host never
        # deploys, and every such edit forced an Apply that could not change
        # anything on it.
        $manifest = New-FeatureManifest
        $root = Join-Path $TestDrive 'scoped'
        [void](New-Item -ItemType Directory -Path (Join-Path $root 'files') -Force)
        [IO.File]::WriteAllText((Join-Path $root 'manifest.json'), '{}')
        [IO.File]::WriteAllText((Join-Path $root 'files\profile.ps1'), 'core')
        [IO.File]::WriteAllText((Join-Path $root 'files\settings.json'), '{}')
        $before = Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core')
        [IO.File]::WriteAllText((Join-Path $root 'files\settings.json'), '{"changed":true}')
        (Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core')) | Should -Be $before
        (Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core', 'terminal')) | Should -Not -Be $before
    }

    It 'reads a schema 1 state as the full feature set' {
        # Schema 1 predates selection and could only have been written by a
        # full deployment, so an already applied host keeps what it has.
        $manifest = New-FeatureManifest
        $state = [pscustomobject]@{ schemaVersion = 1; projectVersion = '1.0.0' }
        ((Get-WinEnvAppliedFeature -Manifest $manifest -State $state) -join ',') | Should -Be 'core,font,zellij,terminal'
    }

    It 'reads a recorded selection back unchanged' {
        $manifest = New-FeatureManifest
        $state = [pscustomobject]@{ schemaVersion = 2; projectVersion = '1.0.0'; features = @('core', 'zellij') }
        ((Get-WinEnvAppliedFeature -Manifest $manifest -State $state) -join ',') | Should -Be 'core,zellij'
    }

    It 'treats an uninitialized host as having applied nothing' {
        (Get-WinEnvAppliedFeature -Manifest (New-FeatureManifest) -State $null).Count | Should -Be 0
    }
}

Describe 'managed sources' {
    It 'parses every source without throwing for a parser it does not have' {
        # No Parser is excluded any more. A source whose parser is unavailable
        # reports a reason instead of throwing, so the suite no longer has to
        # carry a list of the formats this host might be unable to check.
        # Every declared variant, matching check-desired-state.ps1: a managed
        # file whose source depends on the Windows build has a payload that is
        # never this host's answer, and it must still be parsed here.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        foreach ($definition in $manifest.ManagedFiles) {
            foreach ($variant in (Get-WinEnvManagedFileVariant -Definition $definition)) {
                { Test-WinEnvSourceFile -Definition $variant -RepositoryRoot $desiredStateRoot } |
                    Should -Not -Throw
            }
        }
    }

    It 'names the missing parser rather than reporting the source as valid' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        foreach ($definition in $manifest.ManagedFiles) {
            foreach ($variant in (Get-WinEnvManagedFileVariant -Definition $definition)) {
                $reason = Test-WinEnvSourceFile -Definition $variant -RepositoryRoot $desiredStateRoot
                if ($null -ne $reason) {
                    $reason | Should -BeOfType [string]
                    $reason | Should -Not -BeNullOrEmpty
                }
            }
        }
    }

    It 'does not contain excluded host and runtime files' {
        (Test-Path (Join-Path $desiredStateRoot 'files\powertoys\Workspaces\workspaces.json')) | Should -Be $false
        (Test-Path (Join-Path $desiredStateRoot 'files\powertoys\FancyZones\applied-layouts.json')) | Should -Be $false
        # Scans the whole payload tree, not just powertoys: every directory
        # under files\ can carry a leaked absolute path, and -Recurse with no
        # extension filter also reaches the .lua.example templates that the
        # payload-declaration assertion below deliberately skips.
        $all = Get-ChildItem (Join-Path $desiredStateRoot 'files') -File -Recurse |
            ForEach-Object { Get-Content $_.FullName -Raw }
        ($all -join "`n") | Should -Not -Match $WindowsHomePathPattern
    }

    It 'flags a payload that leaks an absolute Windows account path' {
        # Negative fixture (AGENTS.md: "Every enforceable invariant needs
        # positive and negative fixtures"). The fixture lives under $TestDrive,
        # never under windows/desired/files, which is what keeps the self-match
        # exclusion rule above true rather than coincidental.
        #
        # The leaked text below is assembled from separate literals rather
        # than written out whole. A drive letter, colon, one-or-two
        # backslashes, "Users", one-or-two backslashes, and an account name,
        # written contiguously in this committed source, would itself be an
        # absolute home path under tool/version-control/hygiene's
        # repository-wide axis 1 (issue #30) -- a different scanner, over the
        # whole tracked tree, that this issue is deliberately not merged with.
        # Assembling it at runtime keeps the committed source free of the
        # shape either scanner looks for while still producing genuine
        # leaked-path text for Get-Content to return.
        $accountName = 'alice'
        $rawLeak = 'C' + ':' + '\' + 'Users' + '\' + $accountName
        $jsonLeak = 'C' + ':' + '\\' + 'Users' + '\\' + $accountName

        $leakRoot = Join-Path $TestDrive 'leaky-files'
        [void](New-Item -ItemType Directory -Path $leakRoot -Force)

        # Raw-text spelling: one backslash, as it would appear in a
        # PowerShell, Lua, or .lua.example payload.
        [IO.File]::WriteAllText((Join-Path $leakRoot 'profile.ps1'), '$env:UserProfile = "' + $rawLeak + '"')
        $rawContent = Get-Content (Join-Path $leakRoot 'profile.ps1') -Raw
        (Test-Throws { $rawContent | Should -Not -Match $WindowsHomePathPattern }) | Should -Be $true

        # JSON-escaped spelling: two backslashes, as the same leak appears in
        # a JSON payload's raw bytes once its separators are escaped.
        [IO.File]::WriteAllText((Join-Path $leakRoot 'settings.json'), '{"home":"' + $jsonLeak + '"}')
        $jsonContent = Get-Content (Join-Path $leakRoot 'settings.json') -Raw
        (Test-Throws { $jsonContent | Should -Not -Match $WindowsHomePathPattern }) | Should -Be $true
    }

    It 'declares every deployable desired-state payload exactly once' {
        # Reworked for schema 3, not loosened. A managed file may now declare
        # alternative sources selected by the host's Windows build, so the
        # declared set is every variant of every entry rather than one scalar
        # Source per entry. Reading $manifest.ManagedFiles.Source instead would
        # have returned nothing for a conditional entry and silently stopped
        # seeing both of its payloads. The match is still exact in both
        # directions, so an undeclared payload and a declared-but-absent one
        # each still fail.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')

        # Payload -> owning feature. Building the map rather than a flat list
        # is what keeps the "exactly once" and the "exactly one owning feature"
        # halves of this assertion enforced together: a second declaration of
        # the same payload, by the same entry or by another one, collides here
        # before the tree comparison below ever runs.
        $declaredFeature = @{}
        foreach ($definition in $manifest.ManagedFiles) {
            foreach ($variant in (Get-WinEnvManagedFileVariant -Definition $definition)) {
                $source = ([string]$variant.Source).Replace('\', '/')
                $declaredFeature.ContainsKey($source) | Should -Be $false
                ([string]$variant.Feature) | Should -Not -BeNullOrEmpty
                $declaredFeature[$source] = [string]$variant.Feature
            }
        }
        $declared = @($declaredFeature.Keys | Sort-Object)

        $filesRoot = Join-Path $desiredStateRoot 'files'
        # -Force so a payload whose name begins with a dot is scanned. Without
        # it Get-ChildItem skips a hidden file on Windows and a dotfile on
        # Linux alike, which is why files/wsl/.wslconfig was the one payload
        # this assertion never saw. Nothing under files/ is hidden today; the
        # switch keeps that from being load-bearing.
        $actual = @(Get-ChildItem $filesRoot -File -Recurse -Force | Where-Object Extension -ne '.example' | ForEach-Object {
            'files/' + [IO.Path]::GetRelativePath($filesRoot, $_.FullName).Replace('\', '/')
        } | Sort-Object)
        ($declared -join "`n") | Should -Be ($actual -join "`n")

        # Both .wslconfig variants belong to one entry, so they share one
        # Feature by construction rather than by agreement between two entries
        # that could drift apart.
        $declaredFeature['files/wsl/mirrored-networking.wslconfig'] | Should -Be 'wsl'
        $declaredFeature['files/wsl/nat-networking.wslconfig'] | Should -Be 'wsl'
    }
}

Describe 'feature model' {
    It 'owns every deployable item with a declared feature' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $declared = Get-WinEnvFeatureId -Manifest $manifest
        foreach ($package in $manifest.Packages) { $declared | Should -Contain $package.Feature }
        foreach ($definition in $manifest.ManagedFiles) { $declared | Should -Contain $definition.Feature }
        $declared | Should -Contain $manifest.Font.Feature
        $declared | Should -Contain $manifest.Terminal.Feature
    }

    It 'rejects a deployable item that names no feature' {
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(@{ Id = 'orphan'; Source = 'files/orphan.txt'; Target = 'orphan'; Compare = 'Text'; Parser = 'Text' })
        }
        (Test-Throws { Assert-WinEnvFeatureModel -Manifest $manifest }) | Should -Be $true
    }

    It 'rejects an item that names an undeclared feature' {
        $manifest = New-FeatureManifest -Override @{
            Packages = @(@{ Id = 'Vendor.Ghost'; Feature = 'ghost'; Detection = 'WinGet' })
        }
        (Test-Throws { Assert-WinEnvFeatureModel -Manifest $manifest }) | Should -Be $true
    }

    It 'rejects a dependency on an undeclared feature' {
        $manifest = New-FeatureManifest -Override @{
            Features = @(
                @{ Id = 'core'; Name = 'Core'; Required = $true },
                @{ Id = 'font'; Name = 'Font' },
                @{ Id = 'zellij'; Name = 'Zellij' },
                @{ Id = 'terminal'; Name = 'Terminal'; Requires = @('font', 'zellij', 'ghost') }
            )
        }
        (Test-Throws { Assert-WinEnvFeatureModel -Manifest $manifest }) | Should -Be $true
    }

    It 'rejects a Requires cycle' {
        $manifest = New-FeatureManifest -Override @{
            Features = @(
                @{ Id = 'core'; Name = 'Core'; Required = $true },
                @{ Id = 'font'; Name = 'Font'; Requires = @('terminal') },
                @{ Id = 'zellij'; Name = 'Zellij' },
                @{ Id = 'terminal'; Name = 'Terminal'; Requires = @('font', 'zellij') }
            )
        }
        (Test-Throws { Assert-WinEnvFeatureModel -Manifest $manifest }) | Should -Be $true
    }

    It 'rejects a manifest in which nothing is required' {
        $manifest = New-FeatureManifest -Override @{
            Features = @(
                @{ Id = 'core'; Name = 'Core' },
                @{ Id = 'font'; Name = 'Font' },
                @{ Id = 'zellij'; Name = 'Zellij' },
                @{ Id = 'terminal'; Name = 'Terminal'; Requires = @('font', 'zellij') }
            )
        }
        (Test-Throws { Assert-WinEnvFeatureModel -Manifest $manifest }) | Should -Be $true
    }

    It 'refuses to let a bootstrap package become optional' {
        # bootstrap.ps1 installs it before setup.ps1 can run at all, so a
        # selection that excluded it would describe a host that cannot exist.
        $manifest = New-FeatureManifest -Override @{
            Packages = @(@{ Id = 'Vendor.Shell'; Feature = 'font'; Bootstrap = $true; Detection = 'Command'; Command = 'pwsh.exe' })
        }
        (Test-Throws { Assert-WinEnvFeatureModel -Manifest $manifest }) | Should -Be $true
    }

    It 'declares the PowerToys lifecycle on the feature that owns those files' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $owner = @($manifest.Features | Where-Object { $_.ContainsKey('Lifecycle') })
        $owner.Count | Should -Be 1
        $owner[0].Id | Should -Be 'powertoys'
        @($manifest.ManagedFiles | Where-Object Feature -eq 'powertoys').Count | Should -Be 18
    }
}

Describe 'feature selection' {
    It 'reduces a bare selection to the required features' {
        $selection = Get-WinEnvFeatureSelection -Manifest (New-FeatureManifest)
        ($selection.Selected -join ',') | Should -Be 'core'
        $selection.Excluded | Should -Contain 'terminal'
    }

    It 'closes over declared dependencies and reports what it added' {
        $selection = Get-WinEnvFeatureSelection -Manifest (New-FeatureManifest) -Requested @('terminal')
        ($selection.Selected -join ',') | Should -Be 'core,font,zellij,terminal'
        (($selection.Implied | Sort-Object) -join ',') | Should -Be 'font,zellij'
        $selection.Excluded.Count | Should -Be 0
    }

    It 'keeps a dependency selectable on its own' {
        $selection = Get-WinEnvFeatureSelection -Manifest (New-FeatureManifest) -Requested @('zellij')
        ($selection.Selected -join ',') | Should -Be 'core,zellij'
        $selection.Excluded | Should -Contain 'terminal'
    }

    It 'rejects an unknown feature instead of silently ignoring it' {
        (Test-Throws { Get-WinEnvFeatureSelection -Manifest (New-FeatureManifest) -Requested @('ghost') }) | Should -Be $true
    }

    It 'leaves the host untouched beyond PowerShell in a minimal selection' {
        # The point of a minimal bootstrap: no font, no registry delegation,
        # no application settings, no Appx precondition.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $selection = Get-WinEnvFeatureSelection -Manifest $manifest
        ($selection.Selected -join ',') | Should -Be 'core'
        (@($manifest.Packages | Where-Object { $selection.Selected -contains $_.Feature }).Id -join ',') |
            Should -Be 'Microsoft.PowerShell'
        (@($manifest.ManagedFiles | Where-Object { $selection.Selected -contains $_.Feature }).Id -join ',') |
            Should -Be 'powershellProfile'
        $selection.Selected | Should -Not -Contain $manifest.Font.Feature
        $selection.Selected | Should -Not -Contain $manifest.Terminal.Feature
        @($manifest.Features | Where-Object { $selection.Selected -contains $_.Id -and $_.ContainsKey('Preconditions') }).Count |
            Should -Be 0
    }

    It 'binds the Windows Terminal payload to the zellij profile it declares' {
        # files/terminal/settings.json is owned whole, and it launches
        # zellij.exe from a profile, so terminal cannot be selected without it.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $selection = Get-WinEnvFeatureSelection -Manifest $manifest -Requested @('terminal')
        $selection.Selected | Should -Contain 'zellij'
        $selection.Selected | Should -Contain 'font'
        (($selection.Implied | Sort-Object) -join ',') | Should -Be 'font,zellij'
    }

    It 'keeps a fresh host on the full set and an applied host on its record' {
        # Selection is new; the deployment this repository already performed is
        # not. A host that applied before must not silently gain or lose
        # anything because the mechanism arrived.
        $manifest = New-FeatureManifest
        ((Get-WinEnvRequestedFeature -Manifest $manifest) -join ',') | Should -Be 'core,font,zellij,terminal'
        ((Get-WinEnvRequestedFeature -Manifest $manifest -Applied @('core', 'zellij') -HasState $true) -join ',') |
            Should -Be 'core,zellij'
    }

    It 'reads -Minimal, -All, -Feature and -Add as selections' {
        $manifest = New-FeatureManifest
        (Get-WinEnvRequestedFeature -Manifest $manifest -Minimal).Count | Should -Be 0
        ((Get-WinEnvRequestedFeature -Manifest $manifest -All) -join ',') | Should -Be 'core,font,zellij,terminal'
        ((Get-WinEnvRequestedFeature -Manifest $manifest -Feature @('terminal')) -join ',') | Should -Be 'terminal'
        ((Get-WinEnvRequestedFeature -Manifest $manifest -Applied @('core') -HasState $true -Add @('zellij')) -join ',') |
            Should -Be 'core,zellij'
    }

    It 'splits a comma-joined argument from bootstrap.ps1' {
        # pwsh -File passes every value as one literal string.
        ((Expand-WinEnvFeatureArgument -Value @('wezterm, wsl')) -join ',') | Should -Be 'wezterm,wsl'
        (Expand-WinEnvFeatureArgument -Value $null).Count | Should -Be 0
    }

    It 'refuses two selections at once rather than guessing' {
        $manifest = New-FeatureManifest
        (Test-Throws { Get-WinEnvRequestedFeature -Manifest $manifest -Minimal -All }) | Should -Be $true
        (Test-Throws { Get-WinEnvRequestedFeature -Manifest $manifest -Feature @('font') -Add @('font') }) | Should -Be $true
    }

    It 'does not pull Windows Terminal into a WezTerm selection, but does pull the font' {
        # wezterm's fonts.json falls back to D2KodingLigature Nerd Font Mono
        # for Hangul, which only the font feature installs, so wezterm
        # requires font the same way terminal requires zellij.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $selection = Get-WinEnvFeatureSelection -Manifest $manifest -Requested @('wezterm')
        ($selection.Selected -join ',') | Should -Be 'core,font,wezterm'
        ($selection.Implied -join ',') | Should -Be 'font'
        $selection.Excluded | Should -Contain 'terminal'
    }
}

Describe 'Appx detection capability' {
    BeforeAll {
        # The three answers the Appx module can give, as fixtures. No single
        # host can produce all three: a host whose module loads cannot produce
        # the third, and a host whose module does not load cannot produce the
        # first two.
        $PresentQuery = { param([string] $PackageName) [pscustomobject]@{ Name = $PackageName } }
        $AbsentQuery = { param([string] $PackageName) }
        # Reproduces the reported Windows 10 text. PowerShell 7 raises this
        # while autoloading the module, before Get-AppxPackage is bound, which
        # is why -ErrorAction cannot suppress it and only a try/catch sees it.
        $UnusableQuery = {
            param([string] $PackageName)
            throw ("The 'Get-AppxPackage' command was found in the module 'Appx', but the module " +
                'could not be loaded due to the following error: ' +
                '[Operation is not supported on this platform. (0x80131539)]')
        }
        $Registered = { param([string] $PackageId) $true }
        $Unregistered = { param([string] $PackageId) $false }

        $AppxFeature = @{
            Id            = 'appxFeature'
            Name          = 'Appx Feature'
            Preconditions = @(
                @{ Type = 'Appx'; Name = 'Vendor.Palette'; Message = 'repair the vendor suite before applying' }
            )
        }
        $AppxPackage = @{
            Id        = 'Vendor.Terminal'
            Name      = 'Vendor Terminal'
            Detection = 'Appx'
            AppxName  = 'Vendor.Terminal'
        }
    }

    It 'distinguishes present, absent and an unusable module' {
        $present = Get-WinEnvAppxPresence -Name 'Vendor.Terminal' -Query $PresentQuery
        $present.Usable | Should -Be $true
        $present.Present | Should -Be $true
        ($null -eq $present.Reason) | Should -Be $true

        $absent = Get-WinEnvAppxPresence -Name 'Vendor.Terminal' -Query $AbsentQuery
        $absent.Usable | Should -Be $true
        $absent.Present | Should -Be $false

        # Presence is unknowable here, so it is not representable either.
        $unusable = Get-WinEnvAppxPresence -Name 'Vendor.Terminal' -Query $UnusableQuery
        $unusable.Usable | Should -Be $false
        ($null -eq $unusable.Present) | Should -Be $true
        $unusable.Reason | Should -Match 'could not be loaded'
    }

    It 'reports a precondition it could not decide as unverified, not as a failure' {
        $satisfied = Test-WinEnvFeaturePrecondition -Feature $AppxFeature -AppxQuery $PresentQuery
        $satisfied.Failures.Count | Should -Be 0
        $satisfied.Unverified.Count | Should -Be 0

        $failed = Test-WinEnvFeaturePrecondition -Feature $AppxFeature -AppxQuery $AbsentQuery
        $failed.Failures.Count | Should -Be 1
        $failed.Failures[0] | Should -Match 'Appx is missing'
        $failed.Unverified.Count | Should -Be 0

        $undecided = Test-WinEnvFeaturePrecondition -Feature $AppxFeature -AppxQuery $UnusableQuery
        $undecided.Failures.Count | Should -Be 0
        $undecided.Unverified.Count | Should -Be 1
        $undecided.Unverified[0] | Should -Match 'undecidable on this host'
        $undecided.Unverified[0] | Should -Not -Match 'is missing'
    }

    It 'keeps a feature without preconditions and an undeclared type as they were' {
        $none = Test-WinEnvFeaturePrecondition -Feature @{ Id = 'core'; Name = 'Core' } -AppxQuery $UnusableQuery
        $none.Failures.Count | Should -Be 0
        $none.Unverified.Count | Should -Be 0

        # An undeclared type is a broken manifest, not an undecidable host, so
        # the evaluator stays strict about it.
        $unknown = @{
            Id            = 'unknown'
            Name          = 'Unknown'
            Preconditions = @(@{ Type = 'Ouija'; Name = 'Vendor.Palette'; Message = 'ask again later' })
        }
        (Test-Throws { Test-WinEnvFeaturePrecondition -Feature $unknown }) | Should -Be $true
    }

    It 'leaves Appx package detection unchanged while the module answers' {
        $present = Get-WinEnvPackageStatus -Package $AppxPackage -AppxQuery $PresentQuery -RegistrationQuery $Registered
        $present.Detected | Should -Be $true
        $present.Conflict | Should -Be $false
        $present.Missing | Should -Be $false
        ($null -eq $present.Unverified) | Should -Be $true

        $absent = Get-WinEnvPackageStatus -Package $AppxPackage -AppxQuery $AbsentQuery -RegistrationQuery $Registered
        $absent.Detected | Should -Be $false
        $absent.Conflict | Should -Be $true
        ($null -eq $absent.Unverified) | Should -Be $true

        $uninstalled = Get-WinEnvPackageStatus -Package $AppxPackage -AppxQuery $AbsentQuery -RegistrationQuery $Unregistered
        $uninstalled.Missing | Should -Be $true
        $uninstalled.Conflict | Should -Be $false
    }

    It 'reports an unusable module as unverified instead of a missing package' {
        # The reported failure: an installed Windows Terminal read as missing,
        # or as a detection conflict, because the module could not be loaded.
        $status = Get-WinEnvPackageStatus -Package $AppxPackage -AppxQuery $UnusableQuery -RegistrationQuery $Registered
        $status.Missing | Should -Be $false
        $status.Conflict | Should -Be $false
        $status.Unverified | Should -Match 'undecidable on this host'
    }

    It 'still reports a package WinGet does not know as missing when Appx cannot answer' {
        # Only the Appx half is unverified. WinGet answered, and its answer is
        # the same claim a WinGet-detected package already makes, so Apply can
        # still install a package that is genuinely absent.
        $status = Get-WinEnvPackageStatus -Package $AppxPackage -AppxQuery $UnusableQuery -RegistrationQuery $Unregistered
        $status.Missing | Should -Be $true
        $status.Conflict | Should -Be $false
        $status.Unverified | Should -Match 'undecidable on this host'
    }

    It 'ranks drift above an undecidable item in the check exit contract' {
        (Get-WinEnvCheckStatus -DriftCount 0 -UnverifiedCount 0) | Should -Be 0
        (Get-WinEnvCheckStatus -DriftCount 1 -UnverifiedCount 0) | Should -Be 2
        (Get-WinEnvCheckStatus -DriftCount 0 -UnverifiedCount 1) | Should -Be 69
        # A host with both answers the actionable question first.
        (Get-WinEnvCheckStatus -DriftCount 1 -UnverifiedCount 1) | Should -Be 2
    }

    It 'keeps the injected query seams name-only' {
        # The seams exist so the three outcomes have fixtures. Declaring a
        # position on the primary parameter is what stops a caller binding a
        # scriptblock into one by accident.
        foreach ($command in 'Get-WinEnvAppxPresence', 'Test-WinEnvFeaturePrecondition', 'Get-WinEnvPackageStatus') {
            foreach ($seam in 'Query', 'AppxQuery', 'RegistrationQuery') {
                $parameter = (Get-Command $command).Parameters[$seam]
                if (-not $parameter) { continue }
                $attribute = @($parameter.Attributes |
                        Where-Object { $_ -is [System.Management.Automation.ParameterAttribute] })[0]
                $attribute.Position | Should -Be ([int]::MinValue)
            }
        }
    }

    It 'turns an undecidable item into a failure when native evidence is required' {
        # REQUIRE_NATIVE is the flag that says incompleteness must not pass,
        # and a failure outranks both drift and an unverified result.
        (Get-WinEnvCheckStatus -DriftCount 0 -UnverifiedCount 1 -RequireNative) | Should -Be 1
        (Get-WinEnvCheckStatus -DriftCount 1 -UnverifiedCount 1 -RequireNative) | Should -Be 1
        # It promotes nothing that was decided.
        (Get-WinEnvCheckStatus -DriftCount 0 -UnverifiedCount 0 -RequireNative) | Should -Be 0
        (Get-WinEnvCheckStatus -DriftCount 1 -UnverifiedCount 0 -RequireNative) | Should -Be 2
    }
}

Describe 'Windows build condition' {
    BeforeAll {
        # The bound for this payload's option set is Windows 11 22H2, build
        # 22621. Every build below it is one payload and every build at or
        # above it is the other.
        #
        # All four builds below report OSVersion.Version.Major = 10, which is
        # precisely why the major version is never compared: no major-version
        # test can tell 19045 from 22000 from 22631, and the cases here demand
        # two different answers from builds that share a major version. A
        # Windows 11 21H2 host is unmistakably Windows 11 and still belongs on
        # the lower side, so a Windows 10 versus Windows 11 test would be wrong
        # in the same way.
        $Windows10_22H2 = 19045
        $Windows11_21H2 = 22000
        $Windows11_22H2 = 22621
        $Windows11_23H2 = 22631

        $Upper = 'files/wsl/mirrored-networking.wslconfig'
        $Lower = 'files/wsl/nat-networking.wslconfig'

        function New-ConditionalFile {
            param([array] $Sources)
            return @{
                Id      = 'conditional'
                Feature = 'core'
                Compare = 'Text'
                Parser  = 'Ini'
                Target  = 'target'
                Sources = $Sources
            }
        }

        function New-WslFile {
            $definition = New-ConditionalFile -Sources @(
                @{ MinimumBuild = 22621; Source = 'files/wsl/mirrored-networking.wslconfig' },
                @{ Source = 'files/wsl/nat-networking.wslconfig' })
            $definition.Id = 'wslConfig'
            $definition.Feature = 'wsl'
            return $definition
        }
    }

    It 'resolves a host at or above the 22H2 bound to the mirrored payload' {
        $definition = New-WslFile
        (Resolve-WinEnvManagedFile -Definition $definition -Build $Windows11_23H2).Source | Should -Be $Upper
        # The bound itself is inclusive: 22H2 "or higher".
        (Resolve-WinEnvManagedFile -Definition $definition -Build $Windows11_22H2).Source | Should -Be $Upper
    }

    It 'resolves a host below the bound, Windows 10 or Windows 11 21H2, to the NAT payload' {
        $definition = New-WslFile
        (Resolve-WinEnvManagedFile -Definition $definition -Build $Windows10_22H2).Source | Should -Be $Lower
        # Windows 11, and still below the bound. This is the case that makes a
        # release-name split wrong rather than merely imprecise.
        (Resolve-WinEnvManagedFile -Definition $definition -Build $Windows11_21H2).Source | Should -Be $Lower
    }

    It 'resolves an undetectable build to the payload every supported build honours' {
        # Not an arbitrary default: the last variant is the only one whose
        # every key is honoured on every supported build, so a key is never
        # deployed to a host that was not shown to honour it.
        (Resolve-WinEnvManagedFile -Definition (New-WslFile) -Build $null).Source | Should -Be $Lower
    }

    It 'answers with a build number or an honest null, never a major version' {
        $build = Get-WinEnvWindowsBuild
        if ([Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT) {
            $build | Should -Be ([Environment]::OSVersion.Version.Build)
            $build | Should -BeGreaterThan 0
        }
        else {
            # Off Windows the honest answer is that the build is unknown, not a
            # guess and not a foreign kernel's build number. This is also what
            # makes the undetectable branch reachable from a Unix-like clone.
            ($null -eq $build) | Should -Be $true
        }
    }

    It 'leaves an unconditional managed file exactly as declared' {
        $definition = @{ Id = 'plain'; Feature = 'core'; Source = 'files/plain.ini'; Target = 'target'; Compare = 'Text'; Parser = 'Ini' }
        (Resolve-WinEnvManagedFile -Definition $definition -Build $Windows10_22H2).Source | Should -Be 'files/plain.ini'
        (Resolve-WinEnvManagedFile -Definition $definition -Build $null).Source | Should -Be 'files/plain.ini'
        @(Get-WinEnvManagedFileVariant -Definition $definition).Count | Should -Be 1
    }

    It 'exposes every declared variant, in declaration order, with a scalar Source' {
        $variants = @(Get-WinEnvManagedFileVariant -Definition (New-WslFile))
        $variants.Count | Should -Be 2
        $variants[0].Source | Should -Be $Upper
        $variants[1].Source | Should -Be $Lower
        # Each variant is a definition the unchanged consumers can take.
        foreach ($variant in $variants) {
            $variant.ContainsKey('Sources') | Should -Be $false
            $variant.Id | Should -Be 'wslConfig'
            $variant.Target | Should -Be 'target'
            $variant.Feature | Should -Be 'wsl'
        }
    }

    It 'hashes every declared variant so the desired state cannot depend on the host' {
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(New-ConditionalFile -Sources @(
                    @{ MinimumBuild = 22621; Source = 'files/upper.ini' },
                    @{ Source = 'files/lower.ini' }))
        }
        $root = Join-Path $TestDrive 'conditional'
        [void](New-Item -ItemType Directory -Path (Join-Path $root 'files') -Force)
        [IO.File]::WriteAllText((Join-Path $root 'manifest.json'), '{}')
        [IO.File]::WriteAllText((Join-Path $root 'files\upper.ini'), 'upper')
        [IO.File]::WriteAllText((Join-Path $root 'files\lower.ini'), 'lower')

        $before = Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core')
        # Editing the variant this Linux host would never deploy still changes
        # the hash. Were only the resolved variant hashed, two hosts of
        # different build classes would disagree about the same desired state
        # and a host that crossed the bound would report drift no Apply could
        # clear.
        [IO.File]::WriteAllText((Join-Path $root 'files\upper.ini'), 'upper changed')
        $after = Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core')
        $after | Should -Not -Be $before
        [IO.File]::WriteAllText((Join-Path $root 'files\lower.ini'), 'lower changed')
        (Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core')) | Should -Not -Be $after
    }

    It 'accepts the repository manifest and keeps the 22H2 payload byte-identical' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $wsl = $manifest.ManagedFiles | Where-Object Id -eq 'wslConfig'
        (Resolve-WinEnvManagedFile -Definition $wsl -Build $Windows11_23H2).Source | Should -Be $Upper
        (Resolve-WinEnvManagedFile -Definition $wsl -Build $Windows11_22H2).Source | Should -Be $Upper
        (Resolve-WinEnvManagedFile -Definition $wsl -Build $Windows11_21H2).Source | Should -Be $Lower
        (Resolve-WinEnvManagedFile -Definition $wsl -Build $Windows10_22H2).Source | Should -Be $Lower
        (Resolve-WinEnvManagedFile -Definition $wsl -Build $null).Source | Should -Be $Lower

        # A host at or above the bound receives what it already had. Pinned as
        # a literal rather than against the old file, which no longer exists.
        $expected = "[wsl2]`nnetworkingMode=Mirrored`n`n[experimental]`nhostAddressLoopback=true`nautoMemoryReclaim=Gradual`nbestEffortDnsParsing=true`n"
        $actual = (Get-Content (Join-Path $desiredStateRoot $Upper) -Raw).Replace("`r`n", "`n")
        $actual | Should -Be $expected
    }

    It 'parses both payloads with the parser the entry declares' {
        # The merge gate must not accept a payload nobody parsed, and one of
        # these is never the local answer on any single host.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $wsl = $manifest.ManagedFiles | Where-Object Id -eq 'wslConfig'
        foreach ($variant in (Get-WinEnvManagedFileVariant -Definition $wsl)) {
            (Test-WinEnvSourceFile -Definition $variant -RepositoryRoot $desiredStateRoot) | Should -BeNullOrEmpty
        }
    }

    It 'refuses a variant list whose last entry is conditional' {
        # Negative fixture for the invariant the two-entry shape would have
        # needed and could not have enforced: on a host below every bound this
        # file would deploy nothing at all, silently.
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(New-ConditionalFile -Sources @(
                    @{ MinimumBuild = 22621; Source = 'files/upper.ini' },
                    @{ MinimumBuild = 19041; Source = 'files/lower.ini' }))
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
    }

    It 'refuses bounds that do not descend' {
        # An ascending list would let a 22631 host match the 19041 variant
        # first, so the highest bound a host meets would stop being the one it
        # resolves to.
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(New-ConditionalFile -Sources @(
                    @{ MinimumBuild = 19041; Source = 'files/lower.ini' },
                    @{ MinimumBuild = 22621; Source = 'files/upper.ini' },
                    @{ Source = 'files/base.ini' }))
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
    }

    It 'refuses an entry declaring both a scalar Source and alternatives' {
        $definition = New-ConditionalFile -Sources @(
            @{ MinimumBuild = 22621; Source = 'files/upper.ini' },
            @{ Source = 'files/lower.ini' })
        $definition.Source = 'files/plain.ini'
        $manifest = New-FeatureManifest -Override @{ ManagedFiles = @($definition) }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
    }

    It 'refuses an entry that declares no source at all' {
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(@{ Id = 'orphan'; Feature = 'core'; Target = 'target'; Compare = 'Text'; Parser = 'Ini' })
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
    }

    It 'refuses a single-variant list and a non-positive bound' {
        $single = New-FeatureManifest -Override @{
            ManagedFiles = @(New-ConditionalFile -Sources @(@{ Source = 'files/only.ini' }))
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $single }) | Should -Be $true

        $bogus = New-FeatureManifest -Override @{
            ManagedFiles = @(New-ConditionalFile -Sources @(
                    @{ MinimumBuild = 0; Source = 'files/upper.ini' },
                    @{ Source = 'files/lower.ini' }))
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $bogus }) | Should -Be $true
    }

    It 'accepts the shape the repository manifest uses' {
        # Positive fixture beside the four negative ones above.
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(New-ConditionalFile -Sources @(
                    @{ MinimumBuild = 22621; Source = 'files/upper.ini' },
                    @{ Source = 'files/lower.ini' }))
        }
        { Assert-WinEnvManagedFileModel -Manifest $manifest } | Should -Not -Throw
    }
}

Describe 'script syntax' {
    It 'parses all repository PowerShell files' {
        foreach ($file in Get-ChildItem $repositoryRoot -Filter '*.ps1' -File -Recurse) {
            $tokens = $null; $errors = $null
            [void][System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$errors)
            $errors.Count | Should -Be 0
        }
    }
}
