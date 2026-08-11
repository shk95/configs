$repositoryRoot = Split-Path -Parent $PSScriptRoot
$monorepoRoot = Split-Path -Parent $repositoryRoot
$desiredStateRoot = Join-Path $repositoryRoot 'desired'
Import-Module (Join-Path $repositoryRoot 'src\WinEnv.psm1') -Force

function Test-Throws {
    param([scriptblock] $ScriptBlock)
    try { & $ScriptBlock; return $false } catch { return $true }
}

Describe 'win-env manifest' {
    It 'loads schema 1 and the desired-state compatibility version' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $manifest.SchemaVersion | Should Be 1
        $manifest.ProjectVersion | Should Be '0.2.0'
    }

    It 'pins the v3.5.0 D2Koding asset and hashes' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $manifest.Font.Version | Should Be '3.5.0'
        $manifest.Font.Name | Should Be 'D2KodingLigature Nerd Font Mono'
        $manifest.Font.Sha256 | Should Match '^[0-9a-f]{64}$'
        $manifest.Font.Files.Count | Should Be 2
    }

    It 'uses exact expected WinGet IDs' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        (($manifest.Packages.Id | Sort-Object) -join ',') | Should Be 'Microsoft.PowerShell,Microsoft.PowerToys,Microsoft.WindowsTerminal,wez.wezterm,Zellij.Zellij'
    }

    It 'connects the Terminal profile to the pinned font and GUIDs' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $terminal = Get-Content (Join-Path $desiredStateRoot 'files\terminal\settings.json') -Raw | ConvertFrom-Json
        $terminal.defaultProfile | Should Be $manifest.Terminal.DefaultProfileGuid
        $terminal.profiles.defaults.font.face | Should Be $manifest.Font.Name
        ($terminal.profiles.list | Where-Object name -eq 'Zellij Workspace').guid | Should Be $manifest.Terminal.ZellijProfileGuid
    }

    It 'manages the current Windows-side WSL configuration' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $wsl = $manifest.ManagedFiles | Where-Object Id -eq 'WslConfig'
        $wsl.Target | Should Be '{USERPROFILE}\.wslconfig'
        $content = Get-Content (Join-Path $desiredStateRoot $wsl.Source) -Raw
        $content | Should Match '(?m)^networkingMode=Mirrored$'
        $content | Should Not Match '(?m)^firewall\s*='
        $content | Should Match '(?m)^hostAddressLoopback=true$'
        $content | Should Match '(?m)^autoMemoryReclaim=Gradual$'
        $content | Should Match '(?m)^bestEffortDnsParsing=true$'
    }
}

Describe 'version gate' {
    It 'orders repository versions correctly' {
        (Compare-WinEnvVersion -RepositoryVersion '0.1.0' -AppliedVersion '0.0.0') | Should BeGreaterThan 0
        (Compare-WinEnvVersion -RepositoryVersion '0.1.0' -AppliedVersion '0.1.0') | Should Be 0
        (Compare-WinEnvVersion -RepositoryVersion '0.1.0' -AppliedVersion '0.2.0') | Should BeLessThan 0
    }

    It 'rejects an invalid semantic version' {
        (Test-Throws { Compare-WinEnvVersion -RepositoryVersion 'not-semver' -AppliedVersion '0.1.0' }) | Should Be $true
    }
}

Describe 'JSON ownership' {
    It 'allows runtime properties in subset mode' {
        $expected = '{"enabled":true,"nested":{"value":7}}' | ConvertFrom-Json
        $actual = '{"enabled":true,"nested":{"value":7,"runtime":"ignored"},"version":"dynamic"}' | ConvertFrom-Json
        (Test-WinEnvJsonSubset -Expected $expected -Actual $actual) | Should Be $true
    }

    It 'detects changed managed properties' {
        $expected = '{"enabled":true,"items":[1,2]}' | ConvertFrom-Json
        $actual = '{"enabled":false,"items":[1,2]}' | ConvertFrom-Json
        (Test-WinEnvJsonSubset -Expected $expected -Actual $actual) | Should Be $false
    }
}

Describe 'PowerShell profile marker' {
    It 'adds one block and preserves existing external blocks' {
        $profile = Join-Path $TestDrive 'profile.ps1'
        [IO.File]::WriteAllText($profile, "#region sysmon-banner`r`n'SysMon'`r`n#endregion sysmon-banner`r`n")
        Set-WinEnvProfileHook -ProfilePath $profile
        Set-WinEnvProfileHook -ProfilePath $profile
        $content = Get-Content -LiteralPath $profile -Raw
        ([regex]::Matches($content, '(?m)^#region win-env$')).Count | Should Be 1
        $content | Should Match '#region sysmon-banner'
        (Test-WinEnvProfileHook -ProfilePath $profile) | Should Be $true
    }

    It 'refuses unmatched markers' {
        $profile = Join-Path $TestDrive 'broken-profile.ps1'
        [IO.File]::WriteAllText($profile, "#region win-env`r`n")
        (Test-Throws { Set-WinEnvProfileHook -ProfilePath $profile }) | Should Be $true
    }
}

Describe 'state safety' {
    It 'resolves the repository commit without trusting Windows Git safe-directory state' {
        (Get-WinEnvGitCommit -RepositoryRoot $monorepoRoot) | Should Match '^(unborn|[0-9a-f]{40})$'
    }

    It 'treats a missing state as uninitialized' {
        (Get-WinEnvState -Path (Join-Path $TestDrive 'missing.json')) | Should Be $null
    }

    It 'rejects corrupt state instead of applying' {
        $path = Join-Path $TestDrive 'state.json'
        [IO.File]::WriteAllText($path, '{broken')
        (Test-Throws { Get-WinEnvState -Path $path }) | Should Be $true
    }

    It 'atomically writes valid state' {
        $path = Join-Path $TestDrive 'state\state.json'
        $fontRegisteredAtUtc = '2026-08-10T07:42:46.5260930+00:00'
        $desiredStateHash = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
        Write-WinEnvState -Path $path -ProjectVersion '0.1.0' -GitCommit '0123456789abcdef' -DesiredStateHash $desiredStateHash -FontRegisteredAtUtc $fontRegisteredAtUtc
        $state = Get-WinEnvState -Path $path
        $state.projectVersion | Should Be '0.1.0'
        $state.gitCommit | Should Be '0123456789abcdef'
        $state.bundleHash | Should Be $desiredStateHash
        ([DateTimeOffset]$state.fontRegisteredAtUtc).UtcTicks | Should Be ([DateTimeOffset]$fontRegisteredAtUtc).UtcTicks
    }

    It 'changes the desired-state hash when content changes' {
        $root = Join-Path $TestDrive 'desired'
        [void](New-Item -ItemType Directory -Path $root)
        [IO.File]::WriteAllText((Join-Path $root 'manifest.json'), '{}')
        $before = Get-WinEnvDesiredStateHash -Root $root
        [IO.File]::WriteAllText((Join-Path $root 'manifest.json'), '{"changed":true}')
        $after = Get-WinEnvDesiredStateHash -Root $root
        $before | Should Match '^[0-9a-f]{64}$'
        $after | Should Match '^[0-9a-f]{64}$'
        $after | Should Not Be $before
    }
}

Describe 'managed sources' {
    It 'parses every source that needs no external parser' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        foreach ($definition in $manifest.ManagedFiles) {
            if ($definition.Parser -ne 'Kdl') {
                { Test-WinEnvSourceFile -Definition $definition -RepositoryRoot $desiredStateRoot } | Should Not Throw
            }
        }
    }

    It 'does not contain excluded host and runtime files' {
        (Test-Path (Join-Path $desiredStateRoot 'files\powertoys\Workspaces\workspaces.json')) | Should Be $false
        (Test-Path (Join-Path $desiredStateRoot 'files\powertoys\FancyZones\applied-layouts.json')) | Should Be $false
        $all = Get-ChildItem (Join-Path $desiredStateRoot 'files\powertoys') -File -Recurse | ForEach-Object { Get-Content $_.FullName -Raw }
        ($all -join "`n") | Should Not Match 'C:\\\\Users\\\\user1'
    }

    It 'declares every deployable desired-state payload exactly once' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $declared = @($manifest.ManagedFiles.Source | ForEach-Object { $_.Replace('\', '/') } | Sort-Object)
        $filesRoot = Join-Path $desiredStateRoot 'files'
        $actual = @(Get-ChildItem $filesRoot -File -Recurse | Where-Object Extension -ne '.example' | ForEach-Object {
            'files/' + [IO.Path]::GetRelativePath($filesRoot, $_.FullName).Replace('\', '/')
        } | Sort-Object)
        ($declared -join "`n") | Should Be ($actual -join "`n")
    }
}

Describe 'script syntax' {
    It 'parses all repository PowerShell files' {
        foreach ($file in Get-ChildItem $repositoryRoot -Filter '*.ps1' -File -Recurse) {
            $tokens = $null; $errors = $null
            [void][System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$errors)
            $errors.Count | Should Be 0
        }
    }
}
