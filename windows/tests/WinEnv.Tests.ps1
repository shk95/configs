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
            SchemaVersion  = 2
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
}

Describe 'win-env manifest' {
    It 'loads schema 2 and the desired-state compatibility version' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $manifest.SchemaVersion | Should -Be 2
        $manifest.ProjectVersion | Should -Be '0.3.0'
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

    It 'manages the current Windows-side WSL configuration' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $wsl = $manifest.ManagedFiles | Where-Object Id -eq 'WslConfig'
        $wsl.Target | Should -Be '{USERPROFILE}\.wslconfig'
        $content = Get-Content (Join-Path $desiredStateRoot $wsl.Source) -Raw
        $content | Should -Match '(?m)^networkingMode=Mirrored$'
        $content | Should -Not -Match '(?m)^firewall\s*='
        $content | Should -Match '(?m)^hostAddressLoopback=true$'
        $content | Should -Match '(?m)^autoMemoryReclaim=Gradual$'
        $content | Should -Match '(?m)^bestEffortDnsParsing=true$'
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
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        foreach ($definition in $manifest.ManagedFiles) {
            { Test-WinEnvSourceFile -Definition $definition -RepositoryRoot $desiredStateRoot } |
                Should -Not -Throw
        }
    }

    It 'names the missing parser rather than reporting the source as valid' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        foreach ($definition in $manifest.ManagedFiles) {
            $reason = Test-WinEnvSourceFile -Definition $definition -RepositoryRoot $desiredStateRoot
            if ($null -ne $reason) {
                $reason | Should -BeOfType [string]
                $reason | Should -Not -BeNullOrEmpty
            }
        }
    }

    It 'does not contain excluded host and runtime files' {
        (Test-Path (Join-Path $desiredStateRoot 'files\powertoys\Workspaces\workspaces.json')) | Should -Be $false
        (Test-Path (Join-Path $desiredStateRoot 'files\powertoys\FancyZones\applied-layouts.json')) | Should -Be $false
        $all = Get-ChildItem (Join-Path $desiredStateRoot 'files\powertoys') -File -Recurse | ForEach-Object { Get-Content $_.FullName -Raw }
        ($all -join "`n") | Should -Not -Match 'C:\\\\Users\\\\user1'
    }

    It 'declares every deployable desired-state payload exactly once' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $declared = @($manifest.ManagedFiles.Source | ForEach-Object { $_.Replace('\', '/') } | Sort-Object)
        $filesRoot = Join-Path $desiredStateRoot 'files'
        $actual = @(Get-ChildItem $filesRoot -File -Recurse | Where-Object Extension -ne '.example' | ForEach-Object {
            'files/' + [IO.Path]::GetRelativePath($filesRoot, $_.FullName).Replace('\', '/')
        } | Sort-Object)
        ($declared -join "`n") | Should -Be ($actual -join "`n")
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

    It 'does not pull Windows Terminal into a WezTerm selection' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $selection = Get-WinEnvFeatureSelection -Manifest $manifest -Requested @('wezterm')
        ($selection.Selected -join ',') | Should -Be 'core,wezterm'
        $selection.Excluded | Should -Contain 'font'
        $selection.Excluded | Should -Contain 'terminal'
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
