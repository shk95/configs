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
            SchemaVersion  = 4
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
    It 'loads schema 4 and the desired-state compatibility version' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $manifest.SchemaVersion | Should -Be 4
        $manifest.ProjectVersion | Should -Be '0.5.0'
    }

    It 'pins the v3.5.0 D2Koding asset and hashes' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $manifest.Font.Version | Should -Be '3.5.0'
        $manifest.Font.Name | Should -Be 'D2KodingLigature Nerd Font Mono'
        $manifest.Font.Sha256 | Should -Match '^[0-9a-f]{64}$'
        # Four files: the Mono set WezTerm's first font-list entry names plus
        # the non-Mono set its second entry names, all from the one pinned
        # D2Coding.zip archive above.
        $manifest.Font.Files.Count | Should -Be 4
        (($manifest.Font.Files.FileName | Sort-Object) -join ',') | Should -Be (
            'D2KodingLigatureNerdFont-Bold.ttf,D2KodingLigatureNerdFont-Regular.ttf,' +
            'D2KodingLigatureNerdFontMono-Bold.ttf,D2KodingLigatureNerdFontMono-Regular.ttf'
        )
        foreach ($fontFile in $manifest.Font.Files) {
            $fontFile.Sha256 | Should -Match '^[0-9a-f]{64}$'
        }
    }

    It 'installs a registered face for every family WezTerm''s font list names' {
        # #67: the font list on Windows equals the Unix-like list, which names
        # a Mono and a non-Mono D2Koding family. A fixture must fail if either
        # family has no registered face, or the two copies could drift again
        # without either domain's own checks noticing.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $fonts = Get-Content (Join-Path $desiredStateRoot 'files\wezterm\fonts.json') -Raw | ConvertFrom-Json
        $registeredFamilies = @($manifest.Font.Files | ForEach-Object { $_.FullName -replace ' Bold$', '' }) |
            Sort-Object -Unique
        foreach ($family in $fonts.families) {
            $registeredFamilies | Should -Contain $family
        }
    }

    It 'copies the Unix-like WezTerm font list without a Windows-only windowsChecks addendum' {
        $unixFontsPath = Join-Path $monorepoRoot 'assets\wezterm\fonts.json'
        $windowsFontsPath = Join-Path $desiredStateRoot 'files\wezterm\fonts.json'
        (Get-Content $unixFontsPath -Raw) | Should -Be (Get-Content $windowsFontsPath -Raw)
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

Describe 'Windows Terminal generated profiles' {
    BeforeAll {
        $TerminalPayload = Join-Path $desiredStateRoot 'files\terminal\settings.json'
        $TerminalTarget = Join-Path $TestDrive 'terminal-settings.json'

        # Expand-WinEnvTemplate reads LOCALAPPDATA for every managed file it
        # compares, and the hosts this suite is authored on do not set it. The
        # value is irrelevant here, because this payload carries no template,
        # but it has to exist for the managed-file path to run at all.
        $SavedLocalAppData = $env:LOCALAPPDATA
        if (-not $env:LOCALAPPDATA) { $env:LOCALAPPDATA = $TestDrive }

        # The profile the maintainer's host held on 2026-08-30 beside the two
        # the payload declares: a Git for Windows fragment profile, carrying
        # the source that records which extension produced it. Windows
        # Terminal wrote it back into the file seconds after Apply overwrote
        # that file, which under ExactJson made post-apply validation throw
        # and left the host deployed but unrecorded. The guid is not part of
        # that observation; any key the payload does not declare reaches the
        # same branch. Every invented guid in this Describe is written as a
        # short opaque key rather than as a UUID, because a UUID in tracked
        # desired state is what tool/version-control/hygiene exists to catch
        # and a fixture must not teach it to ignore one.
        $GeneratedGitBash = [pscustomobject]@{
            guid   = '{generated-git-bash}'
            hidden = $false
            name   = 'Git Bash'
            source = 'Git'
        }
    }

    AfterAll { $env:LOCALAPPDATA = $SavedLocalAppData }

    It 'converges on the three-profile file the maintainer''s host showed' {
        # The whole point of the change, exercised through the manifest entry
        # that declares the mode rather than through a synthetic definition.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $definition = $manifest.ManagedFiles | Where-Object Id -eq 'windowsTerminal'
        $definition.Target = $TerminalTarget

        $document = Get-Content -LiteralPath $TerminalPayload -Raw -Encoding utf8 | ConvertFrom-Json
        $document.profiles.list = @($document.profiles.list) + $GeneratedGitBash
        @($document.profiles.list).Count | Should -Be 3
        @($document.profiles.list | ForEach-Object { $_.name }) |
            Should -Be @('PowerShell 7', 'Zellij Workspace', 'Git Bash')
        [IO.File]::WriteAllText($TerminalTarget, ($document | ConvertTo-Json -Depth 100))

        (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot) | Should -Be $true
    }

    It 'leaves ExactJson reporting that same file as drift' {
        # The tolerance is one declared mode, not a loosening of ExactJson.
        # Every other managed file keeps the comparison it had.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $definition = $manifest.ManagedFiles | Where-Object Id -eq 'windowsTerminal'
        $definition.Target = $TerminalTarget
        $definition.Compare = 'ExactJson'

        $document = Get-Content -LiteralPath $TerminalPayload -Raw -Encoding utf8 | ConvertFrom-Json
        $document.profiles.list = @($document.profiles.list) + $GeneratedGitBash
        [IO.File]::WriteAllText($TerminalTarget, ($document | ConvertTo-Json -Depth 100))

        (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot) | Should -Be $false
    }

    It 'reports an undeclared profile without a source as drift' {
        # A sourceless profile was written by a person or by another tool.
        # Tolerating it would make the file unowned rather than co-owned.
        $expected = Get-Content -LiteralPath $TerminalPayload -Raw -Encoding utf8
        $document = $expected | ConvertFrom-Json
        $handWritten = [pscustomobject]@{
            commandline = 'cmd.exe'
            guid        = '{hand-written-command-prompt}'
            name        = 'Command Prompt'
        }
        $document.profiles.list = @($document.profiles.list) + $handWritten
        $actual = $document | ConvertTo-Json -Depth 100

        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual $actual) | Should -Be $false

        # Reported as drift through the manifest entry as well, so -Check and
        # post-apply validation see it and not only the comparison itself.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $definition = $manifest.ManagedFiles | Where-Object Id -eq 'windowsTerminal'
        $definition.Target = $TerminalTarget
        [IO.File]::WriteAllText($TerminalTarget, $actual)
        (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot) | Should -Be $false

        # An empty source is not a generator's answer either. The object is
        # already in the list, so this changes the entry in place.
        $handWritten | Add-Member -NotePropertyName 'source' -NotePropertyValue '  '
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual ($document | ConvertTo-Json -Depth 100)) |
            Should -Be $false
    }

    It 'reports a changed, missing or duplicated declared profile as drift' {
        $expected = Get-Content -LiteralPath $TerminalPayload -Raw -Encoding utf8

        $changed = $expected | ConvertFrom-Json
        $changed.profiles.list[1].commandline = 'zellij.exe attach --create other'
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual ($changed | ConvertTo-Json -Depth 100)) |
            Should -Be $false

        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $definition = $manifest.ManagedFiles | Where-Object Id -eq 'windowsTerminal'
        $definition.Target = $TerminalTarget
        [IO.File]::WriteAllText($TerminalTarget, ($changed | ConvertTo-Json -Depth 100))
        (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $desiredStateRoot) | Should -Be $false

        # A declared profile that acquired a source is still a changed
        # declared profile, not a generated one.
        $sourced = $expected | ConvertFrom-Json
        $sourced.profiles.list[1] | Add-Member -NotePropertyName 'source' -NotePropertyValue 'Git'
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual ($sourced | ConvertTo-Json -Depth 100)) |
            Should -Be $false

        $removed = $expected | ConvertFrom-Json
        $removed.profiles.list = @($removed.profiles.list[0], $GeneratedGitBash)
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual ($removed | ConvertTo-Json -Depth 100)) |
            Should -Be $false

        # Two entries carrying one declared guid are ambiguous rather than
        # generated, whatever the second one's source says.
        $duplicated = $expected | ConvertFrom-Json
        $twin = $duplicated.profiles.list[0] | ConvertTo-Json -Depth 100 | ConvertFrom-Json
        $twin.name = 'PowerShell 7 (again)'
        $duplicated.profiles.list = @($duplicated.profiles.list) + $twin
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual ($duplicated | ConvertTo-Json -Depth 100)) |
            Should -Be $false
    }

    It 'tolerates only an entry keyed and sourced the way a generator writes one' {
        # Every comparison in this mode is ordinal, so a capitalised Source is
        # not the property Windows Terminal writes; a non-string source is not
        # a generator's name; and an entry with no guid is not a shape this
        # rule could key on, so none of them earns the tolerance.
        $expected = '{"profiles":{"list":[{"guid":"{declared}","name":"PowerShell 7"}]}}'
        $refused = @(
            '{"guid":"{generated}","name":"Git Bash","Source":"Git"}',
            '{"name":"Git Bash","source":"Git"}',
            '{"guid":"   ","name":"Git Bash","source":"Git"}',
            '{"guid":"{generated}","name":"Git Bash","source":0}',
            '{"guid":"{generated}","name":"Git Bash","source":false}'
        )
        foreach ($extra in $refused) {
            $actual = '{"profiles":{"list":[{"guid":"{declared}","name":"PowerShell 7"},' + $extra + ']}}'
            (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual $actual) | Should -Be $false
        }

        # The one shape it does accept, beside the five it refuses.
        $accepted = '{"profiles":{"list":[{"guid":"{declared}","name":"PowerShell 7"},' +
        '{"guid":"{generated}","name":"Git Bash","source":"Git"}]}}'
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual $accepted) | Should -Be $true
    }

    It 'matches declared profiles by guid rather than by position' {
        # Windows Terminal decides where in the list it writes what it
        # generated, so a positional comparison would report drift for a file
        # that holds exactly the declared profiles.
        $expected = Get-Content -LiteralPath $TerminalPayload -Raw -Encoding utf8
        $document = $expected | ConvertFrom-Json
        $declared = @($document.profiles.list)
        $document.profiles.list = @($GeneratedGitBash, $declared[1], $declared[0])

        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual ($document | ConvertTo-Json -Depth 100)) |
            Should -Be $true
    }

    It 'reads a one-profile list as a list rather than as a single profile' {
        # PowerShell hands a one-element array back as its element unless the
        # value is protected on the way out, and a payload is allowed to
        # declare one profile.
        $expected = '{"profiles":{"list":[{"guid":"{declared}","name":"PowerShell 7"}]}}'
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual $expected) | Should -Be $true

        $generated = '{"profiles":{"list":[{"guid":"{declared}","name":"PowerShell 7"},' +
        '{"guid":"{generated}","name":"Git Bash","source":"Git"}]}}'
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual $generated) | Should -Be $true

        $sourceless = '{"profiles":{"list":[{"guid":"{declared}","name":"PowerShell 7"},' +
        '{"guid":"{generated}","name":"Git Bash"}]}}'
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual $sourceless) | Should -Be $false
    }

    It 'holds everything outside profiles.list to exact equality' {
        $expected = Get-Content -LiteralPath $TerminalPayload -Raw -Encoding utf8

        $theme = $expected | ConvertFrom-Json
        $theme.theme = 'dark'
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual ($theme | ConvertTo-Json -Depth 100)) |
            Should -Be $false

        # profiles.defaults is beside the list and is not tolerated: it is the
        # payload's own appearance, which nothing generates.
        $defaults = $expected | ConvertFrom-Json
        $defaults.profiles.defaults.colorScheme = 'Campbell'
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual ($defaults | ConvertTo-Json -Depth 100)) |
            Should -Be $false

        $added = $expected | ConvertFrom-Json
        $added | Add-Member -NotePropertyName 'launchMode' -NotePropertyValue 'maximized'
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual ($added | ConvertTo-Json -Depth 100)) |
            Should -Be $false

        # A file Windows Terminal has not touched at all still converges.
        (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual $expected) | Should -Be $true
    }

    It 'refuses a target that is not shaped like a settings file' {
        $expected = Get-Content -LiteralPath $TerminalPayload -Raw -Encoding utf8
        foreach ($actual in @('{}', '{"profiles":[]}', '{"profiles":{"list":{}}}')) {
            (Test-WinEnvJsonWithGeneratedProfiles -Expected $expected -Actual $actual) | Should -Be $false
        }
    }

    It 'refuses a payload this mode cannot match by guid' {
        # These are authoring errors in the repository's own payload, so they
        # are named rather than silently converging.
        $noList = '{"profiles":{"defaults":{}}}'
        (Test-Throws { Test-WinEnvJsonWithGeneratedProfiles -Expected $noList -Actual $noList }) | Should -Be $true

        $noGuid = '{"profiles":{"list":[{"name":"Unkeyed"}]}}'
        (Test-Throws { Test-WinEnvJsonWithGeneratedProfiles -Expected $noGuid -Actual $noGuid }) | Should -Be $true

        $repeated = '{"profiles":{"list":[{"guid":"{a}","name":"One"},{"guid":"{a}","name":"Two"}]}}'
        (Test-Throws { Test-WinEnvJsonWithGeneratedProfiles -Expected $repeated -Actual $repeated }) | Should -Be $true
    }

    It 'rejects the generated-profile mode on an entry whose parser is not Json' {
        # The mode reads both sides as JSON. Declared on a Lua or INI payload
        # it would load, read as meaningful, and throw on the first host that
        # compared the file.
        foreach ($parser in @('Text', 'Ini', 'Lua', 'PowerShell', 'Kdl')) {
            $manifest = New-FeatureManifest -Override @{
                ManagedFiles = @(@{
                        Id      = 'terminalSettings'
                        Feature = 'terminal'
                        Source  = 'files/settings.json'
                        Target  = 'settings'
                        Compare = 'ExactJsonWithGeneratedProfiles'
                        Parser  = $parser
                    })
            }
            (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
        }

        $missingParser = New-FeatureManifest -Override @{
            ManagedFiles = @(@{
                    Id      = 'terminalSettings'
                    Feature = 'terminal'
                    Source  = 'files/settings.json'
                    Target  = 'settings'
                    Compare = 'ExactJsonWithGeneratedProfiles'
                })
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $missingParser }) | Should -Be $true

        $json = New-FeatureManifest -Override @{
            ManagedFiles = @(@{
                    Id      = 'terminalSettings'
                    Feature = 'terminal'
                    Source  = 'files/settings.json'
                    Target  = 'settings'
                    Compare = 'ExactJsonWithGeneratedProfiles'
                    Parser  = 'Json'
                })
        }
        { Assert-WinEnvManagedFileModel -Manifest $json } | Should -Not -Throw
    }

    It 'rejects a comparison mode no entry can be compared with' {
        foreach ($compare in @('exactjsonwithgeneratedprofiles', 'JsonMerge', '')) {
            $manifest = New-FeatureManifest -Override @{
                ManagedFiles = @(@{
                        Id      = 'terminalSettings'
                        Feature = 'terminal'
                        Source  = 'files/settings.json'
                        Target  = 'settings'
                        Compare = $compare
                        Parser  = 'Json'
                    })
            }
            (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
        }

        $noCompare = New-FeatureManifest -Override @{
            ManagedFiles = @(@{ Id = 'terminalSettings'; Feature = 'terminal'; Source = 'files/settings.json'; Target = 'settings'; Parser = 'Json' })
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $noCompare }) | Should -Be $true
    }

    It 'gives the tolerance to the one file Windows Terminal co-owns' {
        # Apply still writes this payload whole. The tolerance is a read-side
        # statement about one application, so a second entry claiming it would
        # be a decision, not a detail.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $tolerant = @($manifest.ManagedFiles | Where-Object Compare -eq 'ExactJsonWithGeneratedProfiles')
        $tolerant.Count | Should -Be 1
        $tolerant[0].Id | Should -Be 'windowsTerminal'
        $tolerant[0].Parser | Should -Be 'Json'

        # And the payload it names really is keyed the way the mode matches.
        $document = Get-Content -LiteralPath $TerminalPayload -Raw -Encoding utf8 | ConvertFrom-Json
        foreach ($entry in $document.profiles.list) { $entry.guid | Should -Not -BeNullOrEmpty }
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
        # -Force for the same reason the declaration assertion below uses it:
        # the two scanners walk the same tree and must not disagree about what
        # they can see. A payload whose name begins with a dot would otherwise
        # be declared and never scanned for a leaked path.
        $all = Get-ChildItem (Join-Path $desiredStateRoot 'files') -File -Recurse -Force |
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
        # wezterm's fonts.json leads with D2KodingLigature Nerd Font Mono
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
        foreach ($command in 'Get-WinEnvAppxPresence', 'Test-WinEnvFeaturePrecondition',
            'Get-WinEnvPackageStatus', 'Get-WinEnvFontStatus') {
            foreach ($seam in 'Query', 'AppxQuery', 'RegistrationQuery',
                'FontDirectoryQuery', 'FontRegistryQuery', 'DirectWriteQuery') {
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

Describe 'font installation state' {
    BeforeAll {
        # The four faces of a font whose manifest entry has already grown once:
        # the two Mono faces a host may have installed before the entry listed
        # the other two.
        $FontFaces = @(
            @{ FileName = 'TestFontMono-Regular.ttf'; RegistryName = 'Test Font Mono (TrueType)' },
            @{ FileName = 'TestFontMono-Bold.ttf'; RegistryName = 'Test Font Mono Bold (TrueType)' },
            @{ FileName = 'TestFont-Regular.ttf'; RegistryName = 'Test Font (TrueType)' },
            @{ FileName = 'TestFont-Bold.ttf'; RegistryName = 'Test Font Bold (TrueType)' }
        )

        # A fixture is a directory standing in for the per-user font directory
        # and two hashtables standing in for the two registry keys. It never
        # reads or writes this machine's fonts or its registry: the states that
        # have to be covered include ones no host can be put into on request,
        # and the one that caused the regression is among them.
        function New-FontFixture {
            param(
                [Parameter(Mandatory)][string] $Root,
                [string[]] $Present = @(),
                [string[]] $Corrupt = @(),
                [string[]] $Registered = @(),
                [hashtable] $ForeignRegistration = @{},
                [string[]] $SystemFamilyValue = @(),
                [bool] $DirectWrite = $false
            )

            $case = Join-Path $Root ([guid]::NewGuid().ToString('N'))
            $pinnedDirectory = Join-Path $case 'pinned'
            $fontDirectory = Join-Path $case 'fonts'
            [void](New-Item -ItemType Directory -Path $pinnedDirectory -Force)
            [void](New-Item -ItemType Directory -Path $fontDirectory -Force)

            $files = @()
            $userRegistry = @{}
            foreach ($face in $FontFaces) {
                # The pinned bytes exist for every listed face, whether or not
                # this host has installed it, because the manifest pins a hash
                # for every face it lists.
                $pinned = Join-Path $pinnedDirectory $face.FileName
                Set-Content -LiteralPath $pinned -Value "pinned $($face.FileName)" -NoNewline
                $files += @{
                    FileName     = $face.FileName
                    RegistryName = $face.RegistryName
                    Sha256       = (Get-FileHash -LiteralPath $pinned -Algorithm SHA256).Hash.ToLowerInvariant()
                }

                $path = Join-Path $fontDirectory $face.FileName
                if ($Present -contains $face.FileName) { Copy-Item -LiteralPath $pinned -Destination $path }
                elseif ($Corrupt -contains $face.FileName) {
                    Set-Content -LiteralPath $path -Value 'a different font entirely' -NoNewline
                }
                if ($Registered -contains $face.FileName) { $userRegistry[$face.RegistryName] = $path }
                if ($ForeignRegistration.ContainsKey($face.FileName)) {
                    $userRegistry[$face.RegistryName] = $ForeignRegistration[$face.FileName]
                }
            }

            $systemRegistry = @{}
            foreach ($value in $SystemFamilyValue) { $systemRegistry[$value] = "C:\Windows\Fonts\$value" }

            # Get-ItemProperty returns the provider's own members beside the
            # key's values, so the stand-in carries them too: a family scan that
            # matched one of those would report a font nobody installed.
            foreach ($key in @($userRegistry, $systemRegistry)) {
                $key['PSPath'] = 'Microsoft.PowerShell.Core\Registry::HKEY_CURRENT_USER\Software'
                $key['PSChildName'] = 'Fonts'
                $key['PSProvider'] = 'Microsoft.PowerShell.Core\Registry'
            }
            $userKey = [pscustomobject]$userRegistry
            $systemKey = [pscustomobject]$systemRegistry
            return [pscustomobject]@{
                Font             = @{ Name = 'Test Font Mono'; Files = $files }
                FontDirectory    = $fontDirectory
                DirectoryQuery   = { $fontDirectory }.GetNewClosure()
                RegistryQuery    = {
                    param([string] $Path)
                    if ($Path -like 'HKCU:*') { return $userKey }
                    return $systemKey
                }.GetNewClosure()
                DirectWriteQuery = { param([string] $FamilyName) $DirectWrite }.GetNewClosure()
            }
        }

        function Get-FontFixtureStatus {
            param([Parameter(Mandatory)] $Fixture)

            return Get-WinEnvFontStatus -Font $Fixture.Font `
                -FontDirectoryQuery $Fixture.DirectoryQuery `
                -FontRegistryQuery $Fixture.RegistryQuery `
                -DirectWriteQuery $Fixture.DirectWriteQuery
        }

        $MonoFaces = @('TestFontMono-Regular.ttf', 'TestFontMono-Bold.ttf')
        $AllFaces = @(
            'TestFontMono-Regular.ttf', 'TestFontMono-Bold.ttf',
            'TestFont-Regular.ttf', 'TestFont-Bold.ttf')
    }

    It 'calls a valid registered subset of a grown manifest incomplete, not a conflict' {
        # The reported regression: raising the manifest from two faces to four
        # turned every host that already had the two into a refused Apply. The
        # two files here are the manifest's own, byte for byte, and registered
        # to their own paths. Nothing has to be overwritten to finish this.
        $fixture = New-FontFixture -Root $TestDrive -Present $MonoFaces -Registered $MonoFaces -DirectWrite $true
        $status = Get-FontFixtureStatus -Fixture $fixture

        $status.Incomplete | Should -Be $true
        $status.Conflict | Should -Be $false
        $status.Missing | Should -Be $false
        $status.RegistrationRepairable | Should -Be $false
        $status.Installed | Should -Be $false
        # The two counts the check's wording reads.
        $status.InstalledFaceCount | Should -Be 2
        $status.FaceCount | Should -Be 4
    }

    It 'calls a registration whose file is gone incomplete, because writing that file back finishes it' {
        $fixture = New-FontFixture -Root $TestDrive -Present $MonoFaces `
            -Registered ($MonoFaces + 'TestFont-Regular.ttf') -DirectWrite $true
        $status = Get-FontFixtureStatus -Fixture $fixture

        $status.Incomplete | Should -Be $true
        $status.Conflict | Should -Be $false
        $status.InstalledFaceCount | Should -Be 2
    }

    It 'still calls a file that is not the one the manifest pins a conflict' {
        $fixture = New-FontFixture -Root $TestDrive `
            -Present @('TestFontMono-Regular.ttf', 'TestFont-Regular.ttf', 'TestFont-Bold.ttf') `
            -Corrupt @('TestFontMono-Bold.ttf') -Registered $AllFaces -DirectWrite $true
        $status = Get-FontFixtureStatus -Fixture $fixture

        $status.Conflict | Should -Be $true
        $status.Incomplete | Should -Be $false
        $status.Installed | Should -Be $false
    }

    It 'still calls a registration naming another path a conflict' {
        $fixture = New-FontFixture -Root $TestDrive -Present $MonoFaces -Registered $MonoFaces `
            -ForeignRegistration @{ 'TestFont-Regular.ttf' = 'C:\ProgramData\Other Vendor\TestFont-Regular.ttf' } `
            -DirectWrite $true
        $status = Get-FontFixtureStatus -Fixture $fixture

        $status.Conflict | Should -Be $true
        $status.Incomplete | Should -Be $false
    }

    It 'still calls a system-wide install of the same family a conflict' {
        # A machine-wide registration of this family is not something a
        # per-user Apply may overwrite. DirectWrite is asked about the family
        # the machine-wide entry installs, so this fixture pins the half of the
        # case where it does not resolve: when it does, the registration
        # shortcut in $registered already reports the host as Installed and
        # nothing reaches a state this describes. That shortcut predates this
        # change and is not what it decides.
        $fixture = New-FontFixture -Root $TestDrive -Present $MonoFaces -Registered $MonoFaces `
            -SystemFamilyValue @('Test Font Mono (TrueType)') -DirectWrite $false
        $status = Get-FontFixtureStatus -Fixture $fixture

        $status.Conflict | Should -Be $true
        $status.Incomplete | Should -Be $false
        $status.Installed | Should -Be $false
    }

    It 'refuses a foreign registration even on a host holding every file' {
        # Every listed file is valid and only one registration is wrong, which
        # is the shape closest to a repair. Repairing it would overwrite a value
        # this repository did not write, so it is a conflict rather than the
        # narrower registration repair beside it.
        $fixture = New-FontFixture -Root $TestDrive -Present $AllFaces -Registered $AllFaces `
            -ForeignRegistration @{ 'TestFont-Bold.ttf' = 'C:\ProgramData\Other Vendor\TestFont-Bold.ttf' } `
            -DirectWrite $true
        $status = Get-FontFixtureStatus -Fixture $fixture

        $status.Conflict | Should -Be $true
        $status.RegistrationRepairable | Should -Be $false
        $status.Incomplete | Should -Be $false
        $status.Installed | Should -Be $false
    }

    It 'still calls a host holding every file with no registration registration-repairable' {
        $fixture = New-FontFixture -Root $TestDrive -Present $AllFaces -DirectWrite $false
        $status = Get-FontFixtureStatus -Fixture $fixture

        $status.RegistrationRepairable | Should -Be $true
        $status.Incomplete | Should -Be $false
        $status.Conflict | Should -Be $false
        $status.Missing | Should -Be $false
    }

    It 'still calls a host with no artifact at all missing' {
        $fixture = New-FontFixture -Root $TestDrive -DirectWrite $false
        $status = Get-FontFixtureStatus -Fixture $fixture

        $status.Missing | Should -Be $true
        $status.Incomplete | Should -Be $false
        $status.Conflict | Should -Be $false
        $status.InstalledFaceCount | Should -Be 0
    }

    It 'still calls a fully installed and resolvable font installed' {
        $fixture = New-FontFixture -Root $TestDrive -Present $AllFaces -Registered $AllFaces -DirectWrite $true
        $status = Get-FontFixtureStatus -Fixture $fixture

        $status.Installed | Should -Be $true
        $status.Incomplete | Should -Be $false
        $status.Conflict | Should -Be $false
        $status.Missing | Should -Be $false
        $status.InstalledFaceCount | Should -Be 4
    }

    It 'reports exactly one state for every fixture' {
        # The four states are a partition, which is what lets the check and
        # Apply branch on them in any order.
        $fixtures = @(
            (New-FontFixture -Root $TestDrive -Present $MonoFaces -Registered $MonoFaces -DirectWrite $true),
            (New-FontFixture -Root $TestDrive -Present $AllFaces -Registered $AllFaces -DirectWrite $true),
            (New-FontFixture -Root $TestDrive -Present $AllFaces -DirectWrite $false),
            (New-FontFixture -Root $TestDrive -Present $AllFaces -Registered $AllFaces `
                    -ForeignRegistration @{ 'TestFont-Bold.ttf' = 'C:\ProgramData\Other Vendor\TestFont-Bold.ttf' } `
                    -DirectWrite $true),
            (New-FontFixture -Root $TestDrive -DirectWrite $false),
            (New-FontFixture -Root $TestDrive -Present $MonoFaces -Registered $MonoFaces `
                    -SystemFamilyValue @('Test Font Mono (TrueType)') -DirectWrite $false)
        )
        foreach ($fixture in $fixtures) {
            $status = Get-FontFixtureStatus -Fixture $fixture
            @($status.Installed, $status.Incomplete, $status.RegistrationRepairable,
                $status.Conflict, $status.Missing | Where-Object { $_ }).Count | Should -Be 1
        }
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

    It 'refuses a variant declaring any key but Source and MinimumBuild' {
        # A per-variant Compare, Parser, Feature or Target would load, read as
        # meaningful, and do nothing: New-ResolvedManagedFile copies those from
        # the entry alone. Silently dropping it is the exact class of error the
        # loader exists to catch.
        foreach ($key in @('Compare', 'Parser', 'Feature', 'Target', 'MinimumBuidl')) {
            $upper = @{ MinimumBuild = 22621; Source = 'files/upper.ini' }
            $upper[$key] = 'value'
            $manifest = New-FeatureManifest -Override @{
                ManagedFiles = @(New-ConditionalFile -Sources @($upper, @{ Source = 'files/lower.ini' }))
            }
            (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
        }

        # The unconditional last variant is held to the same rule.
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(New-ConditionalFile -Sources @(
                    @{ MinimumBuild = 22621; Source = 'files/upper.ini' },
                    @{ Source = 'files/lower.ini'; Compare = 'Binary' }))
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
    }

    It 'refuses a variant whose Source is empty or blank' {
        # Caught at load, naming the entry, rather than later from
        # check-desired-state.ps1 as a missing path that is really the
        # desired-state root.
        foreach ($empty in @('', '   ')) {
            $manifest = New-FeatureManifest -Override @{
                ManagedFiles = @(New-ConditionalFile -Sources @(
                        @{ MinimumBuild = 22621; Source = $empty },
                        @{ Source = 'files/lower.ini' }))
            }
            (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
        }

        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(New-ConditionalFile -Sources @(
                    @{ MinimumBuild = 22621; Source = 'files/upper.ini' },
                    @{ Source = '' }))
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
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

Describe 'capture' {
    BeforeAll {
        # A host no machine running this suite has to be. Every value is
        # assembled from separate literals for the reason the payload scan
        # earlier in this file gives: written contiguously, an absolute account
        # path in this committed source is itself what
        # tool/version-control/hygiene refuses, and a fixture must not teach
        # either scanner to ignore one.
        $Account = 'alice'
        $CaptureUserProfile = 'C' + ':' + '\' + 'Users' + '\' + $Account
        $CaptureLocalAppData = $CaptureUserProfile + '\' + 'AppData' + '\' + 'Local'
        $CaptureAppData = $CaptureUserProfile + '\' + 'AppData' + '\' + 'Roaming'
        $CaptureHost = @{
            UserProfile  = $CaptureUserProfile
            LocalAppData = $CaptureLocalAppData
            AppData      = $CaptureAppData
            UserName     = $Account
        }
        # The spelling a JSON payload carries: one separator written as two.
        $JsonLocalAppData = $CaptureLocalAppData.Replace('\', '\\')
        $JsonAppData = $CaptureAppData.Replace('\', '\\')
        $JsonUserProfile = $CaptureUserProfile.Replace('\', '\\')

        # A throwaway desired-state root. Capture writes payloads, so no
        # fixture here may point it at windows/desired.
        $CaptureRoot = Join-Path $TestDrive 'capture-desired'
        $CaptureFiles = Join-Path $CaptureRoot 'files'
        $CaptureTargets = Join-Path $TestDrive 'capture-host'
        [void](New-Item -ItemType Directory -Path $CaptureFiles -Force)
        [void](New-Item -ItemType Directory -Path $CaptureTargets -Force)

        function New-CapturePayload {
            param([string] $Name, [string] $Content)
            [IO.File]::WriteAllText((Join-Path $CaptureFiles $Name), $Content)
            return "files/$Name"
        }

        function New-CaptureTarget {
            param([string] $Name, [string] $Content)
            $path = Join-Path $CaptureTargets $Name
            [IO.File]::WriteAllText($path, $Content)
            return $path
        }

        function New-CaptureDefinition {
            param(
                [string] $Id = 'sample',
                [string] $Feature = 'core',
                [string] $Compare = 'ExactJson',
                [string] $Parser = 'Json',
                [string] $Source,
                [string] $Target
            )
            return @{
                Id      = $Id
                Feature = $Feature
                Compare = $Compare
                Parser  = $Parser
                Source  = $Source
                Target  = $Target
            }
        }
    }

    It 'restores the one placeholder the deploy direction expands' {
        $content = '{"template":"' + $JsonLocalAppData + '\\NewPlus"}'
        $result = ConvertFrom-WinEnvTemplate -Content $content -HostPath $CaptureHost

        $result.Content | Should -Be '{"template":"__LOCALAPPDATA_JSON__\\NewPlus"}'
        # Nothing is reported as unrepresentable, and that is the longest-first
        # rule under test rather than a detail: USERPROFILE is a prefix of
        # LOCALAPPDATA, so a shortest-first pass would have matched the head of
        # this occurrence and reported a leak that is not there.
        @($result.Unrepresented).Count | Should -Be 0
        # The round trip is exact: Apply expands what capture restored.
        (Expand-WinEnvTemplate -Content $result.Content -HostPath $CaptureHost) | Should -Be $content
    }

    It 'reports a spelling it cannot represent instead of inventing a placeholder' {
        # Apply expands one token, to the JSON-escaped spelling of
        # LOCALAPPDATA. Writing `{USERPROFILE}` into a payload would deploy that
        # text literally to the host, so every other spelling is reported and
        # refused rather than rewritten.
        $raw = 'Set-Location "' + $CaptureLocalAppData + '"'
        $rawResult = ConvertFrom-WinEnvTemplate -Content $raw -HostPath $CaptureHost
        $rawResult.Content | Should -Be $raw
        @($rawResult.Unrepresented) | Should -Contain 'LOCALAPPDATA (raw)'

        $roaming = '{"config":"' + $JsonAppData + '\\Zellij"}'
        $roamingResult = ConvertFrom-WinEnvTemplate -Content $roaming -HostPath $CaptureHost
        $roamingResult.Content | Should -Be $roaming
        @($roamingResult.Unrepresented) | Should -Contain 'APPDATA (JSON-escaped)'

        $profileText = '{"home":"' + $JsonUserProfile + '"}'
        $profileResult = ConvertFrom-WinEnvTemplate -Content $profileText -HostPath $CaptureHost
        @($profileResult.Unrepresented) | Should -Contain 'USERPROFILE (JSON-escaped)'
    }

    It 'captures an ExactJson payload and converges the check that reported the drift' {
        $source = New-CapturePayload 'exact.json' "{`n  `"template`": `"__LOCALAPPDATA_JSON__\\Old`"`n}`n"
        $target = New-CaptureTarget 'exact.json' ('{"template":"' + $JsonLocalAppData + '\\New"}')
        $definition = New-CaptureDefinition -Id 'exact' -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Captured'
        $plan.Content | Should -Be '{"template":"__LOCALAPPDATA_JSON__\\New"}'
        $plan.Content | Should -Not -Match 'Users'

        [void](Save-WinEnvCapturedPayload -Plan $plan -RepositoryRoot $CaptureRoot)
        # The point of the whole tool: the file the check called drift now
        # matches the payload, through the same comparison the check uses.
        (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $CaptureRoot -HostPath $CaptureHost) |
            Should -Be $true
    }

    It 'drops a generated Windows Terminal profile and keeps the declared ones' {
        $payloadText = Get-Content -LiteralPath (Join-Path $desiredStateRoot 'files/terminal/settings.json') `
            -Raw -Encoding utf8
        $source = New-CapturePayload 'terminal.json' $payloadText

        # The maintainer's host: the two declared profiles, a change made in
        # the application's own settings UI, and the Git for Windows fragment
        # profile Windows Terminal materialises into the file it co-owns. The
        # guid is a short opaque key rather than a UUID, because a UUID in
        # tracked desired state is what hygiene exists to catch.
        #
        # The changed key is derived from the payload rather than written as a
        # literal. Capturing this very key on a host is the tool's headline
        # use case, and a fixture asserting the value the payload happens to
        # hold today would stop being drift the moment someone captures it,
        # turning a legitimate capture into a failing suite.
        $document = $payloadText | ConvertFrom-Json
        $flipped = -not $document.copyOnSelect
        $document.copyOnSelect = $flipped
        $document.profiles.list = @($document.profiles.list) + [pscustomobject]@{
            guid   = '{generated-git-bash}'
            hidden = $false
            name   = 'Git Bash'
            source = 'Git'
        }
        $target = New-CaptureTarget 'terminal.json' ($document | ConvertTo-Json -Depth 100)

        $definition = New-CaptureDefinition -Id 'windowsTerminal' -Feature 'terminal' `
            -Compare 'ExactJsonWithGeneratedProfiles' -Source $source -Target $target
        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost

        $plan.Status | Should -Be 'Captured'
        $captured = $plan.Content | ConvertFrom-Json
        @($captured.profiles.list).Count | Should -Be 2
        @($captured.profiles.list | Where-Object { $_.PSObject.Properties['source'] -and $_.source -eq 'Git' }) |
            Should -BeNullOrEmpty
        # A declared profile that carries a source of its own stays: the rule
        # keys on the guid the payload declares, not on the member's presence.
        @($captured.profiles.list | ForEach-Object { $_.name }) | Should -Be @('PowerShell 7', 'Zellij Workspace')
        $captured.copyOnSelect | Should -Be $flipped

        [void](Save-WinEnvCapturedPayload -Plan $plan -RepositoryRoot $CaptureRoot)
        (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $CaptureRoot -HostPath $CaptureHost) |
            Should -Be $true
    }

    It 'refuses a file the suite already names as runtime state' {
        # Both spellings the deny list is matched against: the payload this
        # repository would hold, and the target on the host. Neither file has
        # to exist, because the refusal is decided before either is read, and
        # the target below is deliberately in a directory PowerToys would not
        # use: the name is what these two guards and hygiene all decide on.
        $bySource = New-CaptureDefinition -Id 'workspaces' -Feature 'powertoys' `
            -Source 'files/powertoys/Workspaces/workspaces.json' `
            -Target (Join-Path $CaptureTargets 'unrelated.json')
        $plan = Get-WinEnvCapturePlan -Definition $bySource -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'runtime state'

        $byTarget = New-CaptureDefinition -Id 'appliedLayouts' -Feature 'powertoys' `
            -Source 'files/exact.json' `
            -Target (Join-Path (Join-Path $CaptureTargets 'FancyZones') 'applied-layouts.json')
        $targetPlan = Get-WinEnvCapturePlan -Definition $byTarget -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $targetPlan.Status | Should -Be 'Refused'
        $targetPlan.Reason | Should -Match 'runtime state'
    }

    It 'refuses a JsonSubset payload, which cannot be derived from the host file' {
        $source = New-CapturePayload 'subset.json' '{"declared":true}'
        $target = New-CaptureTarget 'subset.json' '{"declared":false,"untracked":1}'
        $definition = New-CaptureDefinition -Id 'subset' -Compare 'JsonSubset' -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'subset'
    }

    It 'refuses a target this host does not have' {
        $source = New-CapturePayload 'absent.json' '{"a":1}'
        $definition = New-CaptureDefinition -Id 'absent' -Source $source `
            -Target (Join-Path $CaptureTargets 'never-written.json')

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'does not exist'
    }

    It 'refuses a build-conditional entry on a host whose build is undetermined' {
        $upper = New-CapturePayload 'upper.wslconfig' "[wsl2]`nnetworkingMode=Mirrored`n"
        $lower = New-CapturePayload 'lower.wslconfig' "[wsl2]`nmemory=4GB`n"
        $target = New-CaptureTarget 'undetermined.wslconfig' "[wsl2]`nmemory=8GB`n"
        $definition = @{
            Id      = 'wslConfig'
            Feature = 'wsl'
            Compare = 'Text'
            Parser  = 'Ini'
            Target  = $target
            Sources = @(@{ MinimumBuild = 22621; Source = $upper }, @{ Source = $lower })
        }

        # Apply reads a null build as the variant every supported build
        # honours, which is safe because it deploys the lower payload. Capture
        # is stricter in the other direction: writing host content into a
        # payload no host selected would put one machine's state into a file
        # another machine deploys.
        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build $null -HostPath $CaptureHost
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'build'
    }

    It 'captures into the payload variant the host build selects' {
        $upper = New-CapturePayload 'selected-upper.wslconfig' "[wsl2]`nnetworkingMode=Mirrored`n"
        $lower = New-CapturePayload 'selected-lower.wslconfig' "[wsl2]`nmemory=4GB`n"
        $target = New-CaptureTarget 'selected.wslconfig' "[wsl2]`nmemory=8GB`n"
        $definition = @{
            Id      = 'wslConfig'
            Feature = 'wsl'
            Compare = 'Text'
            Parser  = 'Ini'
            Target  = $target
            Sources = @(@{ MinimumBuild = 22621; Source = $upper }, @{ Source = $lower })
        }

        (Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
                -Build 22631 -HostPath $CaptureHost).Source | Should -Be $upper
        $below = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 19045 -HostPath $CaptureHost
        $below.Source | Should -Be $lower
        $below.Status | Should -Be 'Captured'
        $below.Content | Should -Be "[wsl2]`nmemory=8GB`n"
    }

    It 'refuses content that still holds an absolute account path' {
        # Another account's path: no host value of this run rewrites it, and
        # every payload assertion in this suite would reject it.
        $other = 'C' + ':' + '\' + 'Users' + '\' + 'bob' + '\' + 'Desktop'
        $source = New-CapturePayload 'leaky.json' '{"path":""}'
        $target = New-CaptureTarget 'leaky.json' ('{"path":"' + $other.Replace('\', '\\') + '"}')
        $definition = New-CaptureDefinition -Id 'leaky' -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'absolute account path'
    }

    It 'refuses content that names this host account outside a path' {
        $source = New-CapturePayload 'named.json' '{"greeting":""}'
        $target = New-CaptureTarget 'named.json' ('{"greeting":"hello ' + $Account + '"}')
        $definition = New-CaptureDefinition -Id 'named' -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'account'

        # Bounded by the characters a name is spelled with, so a short account
        # name inside an unrelated word is not a leak.
        $innocent = New-CaptureTarget 'innocent.json' ('{"greeting":"hello ' + $Account + 'bury"}')
        $innocentDefinition = New-CaptureDefinition -Id 'innocent' `
            -Source (New-CapturePayload 'innocent.json' '{"greeting":""}') -Target $innocent
        (Get-WinEnvCapturePlan -Definition $innocentDefinition -RepositoryRoot $CaptureRoot `
                -Build 22631 -HostPath $CaptureHost).Status | Should -Be 'Captured'
    }

    It 'refuses a .wslconfig firewall key, which AGENTS.md adds only on direction' {
        $source = New-CapturePayload 'guarded.wslconfig' "[wsl2]`nmemory=4GB`n"
        $target = New-CaptureTarget 'guarded.wslconfig' "[wsl2]`nmemory=8GB`nfirewall=true`n"
        $definition = New-CaptureDefinition -Id 'wslConfig' -Feature 'wsl' -Compare 'Text' -Parser 'Ini' `
            -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'firewall'
    }

    It 'leaves a file that matches its payload untouched' {
        $text = "{`n  `"a`": 1`n}`n"
        $source = New-CapturePayload 'unchanged.json' $text
        $target = New-CaptureTarget 'unchanged.json' '{"a":1}'
        $definition = New-CaptureDefinition -Id 'unchanged' -Source $source -Target $target
        $payloadPath = Join-Path $CaptureRoot $source
        $before = (Get-FileHash -LiteralPath $payloadPath -Algorithm SHA256).Hash

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Unchanged'
        $plan.Content | Should -BeNullOrEmpty
        { Save-WinEnvCapturedPayload -Plan $plan -RepositoryRoot $CaptureRoot } | Should -Throw
        (Get-FileHash -LiteralPath $payloadPath -Algorithm SHA256).Hash | Should -Be $before
    }

    It 'writes nothing under -WhatIf' {
        $source = New-CapturePayload 'whatif.json' "{`n  `"a`": 1`n}`n"
        $target = New-CaptureTarget 'whatif.json' '{"a":2}'
        $definition = New-CaptureDefinition -Id 'whatif' -Source $source -Target $target
        $payloadPath = Join-Path $CaptureRoot $source
        $before = (Get-FileHash -LiteralPath $payloadPath -Algorithm SHA256).Hash

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Captured'
        (Save-WinEnvCapturedPayload -Plan $plan -RepositoryRoot $CaptureRoot -WhatIf) | Should -Be $payloadPath
        (Get-FileHash -LiteralPath $payloadPath -Algorithm SHA256).Hash | Should -Be $before

        [void](Save-WinEnvCapturedPayload -Plan $plan -RepositoryRoot $CaptureRoot)
        (Get-FileHash -LiteralPath $payloadPath -Algorithm SHA256).Hash | Should -Not -Be $before
    }

    It 'keeps the line-ending and final-newline convention the payload already uses' {
        # A host file and its payload may disagree about line endings without
        # disagreeing about anything a comparison mode reads, so writing the
        # host's convention would turn a one-key change into a whole-file diff.
        $crlfPath = Join-Path $CaptureFiles 'endings-crlf.ini'
        [IO.File]::WriteAllText($crlfPath, "[wsl2]`r`nmemory=4GB`r`n")
        (ConvertTo-WinEnvPayloadText -Content "[wsl2]`nmemory=8GB`n" -PayloadPath $crlfPath) |
            Should -Be "[wsl2]`r`nmemory=8GB`r`n"

        $lfPath = Join-Path $CaptureFiles 'endings-lf.ini'
        [IO.File]::WriteAllText($lfPath, "[wsl2]`nmemory=4GB")
        # No final newline in the payload, and none added.
        (ConvertTo-WinEnvPayloadText -Content "[wsl2]`r`nmemory=8GB`r`n" -PayloadPath $lfPath) |
            Should -Be "[wsl2]`nmemory=8GB"
    }

    It 'pretty-prints a Json payload to two-space indentation and leaves every other parser as host bytes' {
        # Compact, the shape most host applications actually write, and not
        # already two-space, so a passing assertion cannot be an accident of
        # ConvertTo-Json's own current default.
        $compact = '{"a":1,"nested":{"b":[1,2],"empty":{},"list":[]},"str":"a{b}[c]\"d\\e"}'
        $jsonPath = Join-Path $CaptureFiles 'pretty-direct.json'
        [IO.File]::WriteAllText($jsonPath, "{`n}`n")

        $pretty = ConvertTo-WinEnvPayloadText -Content $compact -PayloadPath $jsonPath -Parser 'Json'
        $expected = "{`n" +
        "  `"a`": 1,`n" +
        "  `"nested`": {`n" +
        "    `"b`": [`n" +
        "      1,`n" +
        "      2`n" +
        "    ],`n" +
        "    `"empty`": {},`n" +
        "    `"list`": []`n" +
        "  },`n" +
        "  `"str`": `"a{b}[c]\`"d\\e`"`n" +
        '}' + "`n"
        $pretty | Should -Be $expected

        # The point of ConvertTo-WinEnvCanonicalJson: reformatting is pure
        # whitespace, so the pretty text and the compact host text it came
        # from parse to the identical value.
        (ConvertTo-WinEnvCanonicalJson $pretty) | Should -Be (ConvertTo-WinEnvCanonicalJson $compact)

        # No Parser given at all -- every non-Json call site -- keeps today's
        # behaviour: host bytes, untouched.
        $iniPath = Join-Path $CaptureFiles 'pretty-direct.ini'
        [IO.File]::WriteAllText($iniPath, "memory=4GB`n")
        (ConvertTo-WinEnvPayloadText -Content 'memory=8GB' -PayloadPath $iniPath -Parser 'Ini') |
            Should -Be "memory=8GB`n"
        (ConvertTo-WinEnvPayloadText -Content 'memory=8GB' -PayloadPath $iniPath) |
            Should -Be "memory=8GB`n"
    }

    It 'writes a captured Json payload pretty-printed and reports the next run unchanged' {
        # The regression this issue exists for: a host application's own
        # compact writer must not become the payload's diff.
        $source = New-CapturePayload 'pretty.json' "{`n  `"a`": 1`n}`n"
        $target = New-CaptureTarget 'pretty.json' '{"a":2,"b":{"c":[1,2,3]},"d":[]}'
        $definition = New-CaptureDefinition -Id 'pretty' -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Captured'
        # Get-WinEnvCapturePlan's own Content stays the raw host text: only the
        # write side pretty-prints, so a caller inspecting the plan still sees
        # exactly what the host held.
        $plan.Content | Should -Be '{"a":2,"b":{"c":[1,2,3]},"d":[]}'

        [void](Save-WinEnvCapturedPayload -Plan $plan -RepositoryRoot $CaptureRoot)
        $payloadPath = Join-Path $CaptureRoot $source
        $written = Get-Content -LiteralPath $payloadPath -Raw -Encoding utf8
        $written | Should -Be (
            "{`n  `"a`": 2,`n  `"b`": {`n    `"c`": [`n      1,`n      2,`n      3`n    ]`n  },`n  `"d`": []`n}`n"
        )

        # Byte-stable across two runs: capturing again from the same,
        # unchanged host reports nothing left to do, through the same
        # canonical comparison -Check uses.
        $second = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $second.Status | Should -Be 'Unchanged'
    }

    It 'restores a host directory the file spells in another case' {
        # Windows accepts more than one spelling of the same directory while
        # every comparison here is ordinal, so the restore matches
        # case-insensitively and normalises the occurrence to the spelling
        # Apply writes back.
        $shouted = $JsonLocalAppData.ToUpperInvariant()
        # -BeExactly, because Should -Be is itself case-insensitive and would
        # call the two spellings equal.
        $shouted | Should -Not -BeExactly $JsonLocalAppData

        $result = ConvertFrom-WinEnvTemplate -Content ('{"template":"' + $shouted + '\\NewPlus"}') `
            -HostPath $CaptureHost
        $result.Content | Should -Be '{"template":"__LOCALAPPDATA_JSON__\\NewPlus"}'
        @($result.Unrepresented).Count | Should -Be 0
    }

    It 'keeps an undeclared profile no generator claims and drops one with no guid' {
        # Three undeclared shapes beside the declared profile. The read side
        # tolerates only the one carrying a source, so the other two are drift
        # under its own rule -- but they are not the same kind of drift. An
        # entry with a guid can become a declared profile, while an entry
        # without one cannot: writing it into the payload makes every later
        # comparison throw "A declared Windows Terminal profile has no guid"
        # instead of reporting drift, which is the regression this fixture
        # exists for.
        $declared = @{ profiles = @{ list = @(@{ guid = '{declared-profile}'; name = 'Declared' }) } } |
            ConvertTo-Json -Depth 100
        $source = New-CapturePayload 'profile-shapes.json' $declared

        $hostText = @{
            profiles = @{
                list = @(
                    @{ guid = '{declared-profile}'; name = 'Declared' },
                    @{ guid = '{hand-written}'; name = 'Hand written' },
                    @{ name = 'No guid at all' },
                    @{ guid = '{generated}'; name = 'Generated'; source = 'Git' }
                )
            }
        } | ConvertTo-Json -Depth 100
        $target = New-CaptureTarget 'profile-shapes.json' $hostText

        $definition = New-CaptureDefinition -Id 'profileShapes' -Feature 'terminal' `
            -Compare 'ExactJsonWithGeneratedProfiles' -Source $source -Target $target
        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost

        $plan.Status | Should -Be 'Captured'
        $result = $plan.Content | ConvertFrom-Json
        @($result.profiles.list | ForEach-Object { $_.name }) | Should -Be @('Declared', 'Hand written')

        [void](Save-WinEnvCapturedPayload -Plan $plan -RepositoryRoot $CaptureRoot)
        # Still drift, because the host holds a profile no payload can own.
        # Drift is the honest answer; a thrown exception is not, and before the
        # guidless entry was dropped this is where the suite blew up.
        { Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $CaptureRoot -HostPath $CaptureHost } |
            Should -Not -Throw
    }

    It 'refuses a host file that uses one profile guid twice' {
        # The read side reports a repeated declared guid as drift, so capture
        # is reached; writing both copies would make the payload itself throw
        # on every later comparison. Which copy the operator meant is not this
        # tool's question, so the run refuses and names the guid.
        $declared = @{ profiles = @{ list = @(@{ guid = '{twice}'; name = 'Declared' }) } } |
            ConvertTo-Json -Depth 100
        $source = New-CapturePayload 'duplicate-guid.json' $declared

        $hostText = @{
            profiles = @{
                list = @(
                    @{ guid = '{twice}'; name = 'Declared' },
                    @{ guid = '{twice}'; name = 'Declared again' }
                )
            }
        } | ConvertTo-Json -Depth 100
        $target = New-CaptureTarget 'duplicate-guid.json' $hostText

        $definition = New-CaptureDefinition -Id 'duplicateGuid' -Feature 'terminal' `
            -Compare 'ExactJsonWithGeneratedProfiles' -Source $source -Target $target
        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost

        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'more than once'
        $plan.Reason | Should -Match 'twice'
    }

    It 'refuses every spelling of an absolute account path, not only the backslash one' {
        # The three axes tool/version-control/hygiene enforces repository-wide.
        # Each is assembled from separate literals, for the reason the payload
        # scan earlier in this file gives, and each is written into the host
        # file as a JSON string, which is how a Windows Terminal
        # startingDirectory or a PowerToys path setting would carry it.
        $forwardSlashDrive = 'C' + ':' + '/' + 'Users' + '/' + 'bob'
        $posix = '/' + 'home' + '/' + 'bob'
        $unc = '\' + '\' + 'wsl.localhost' + '\' + 'Ubuntu' + '\' + 'home' + '\' + 'bob'

        $index = 0
        foreach ($leak in @($forwardSlashDrive, $posix, $unc)) {
            $index++
            $name = "spelling-$index.json"
            $definition = New-CaptureDefinition -Id "spelling$index" `
                -Source (New-CapturePayload $name '{"path":""}') `
                -Target (New-CaptureTarget $name ('{"path":"' + $leak.Replace('\', '\\') + '"}'))

            $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
                -Build 22631 -HostPath $CaptureHost
            $plan.Status | Should -Be 'Refused' -Because $leak
            $plan.Reason | Should -Match 'absolute account path'
        }
    }

    It 'offers the documented selection and no unattended mode' {
        # The script is the part of capture that needs a terminal and a Git
        # repository, so this suite holds it to its interface rather than
        # running it end to end. Its selection and payload rules are fixtured
        # above through the functions it calls, and so is its branch rule now
        # (Describe 'capture branch', below) -- both against a throwaway
        # repository, never this one. What remains genuinely host-only is
        # whether the commit's pre-commit hook actually ran, which is what
        # docs/status.md records as an open question.
        $capturePath = Join-Path $repositoryRoot 'tools\capture.ps1'
        (Test-Path -LiteralPath $capturePath -PathType Leaf) | Should -Be $true

        $tokens = $null; $errors = $null
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($capturePath, [ref]$tokens, [ref]$errors)
        $errors.Count | Should -Be 0

        $parameters = @($ast.ParamBlock.Parameters | ForEach-Object { $_.Name.VariablePath.UserPath })
        $parameters | Should -Contain 'Feature'
        $parameters | Should -Contain 'Id'
        $parameters | Should -Contain 'Branch'
        # -WhatIf comes from SupportsShouldProcess rather than from a parameter
        # of its own, and there is deliberately no -Yes, -Force or override.
        ($ast.ParamBlock.Attributes | ForEach-Object { $_.Extent.Text }) -join ' ' |
            Should -Match 'SupportsShouldProcess'
        $parameters | Should -Not -Contain 'Force'
        $parameters | Should -Not -Contain 'Yes'
    }
}

Describe 'capture branch' {
    <#
        The branch rule tool/version-control/commit applies (#72), copied into
        Get-WinEnvCaptureBranchPlan and New-WinEnvCaptureBranch (#77) because
        capture.ps1 restates that helper's shape rather than calling it. Every
        fixture below runs against a throwaway working copy and a throwaway
        bare remote under $TestDrive, the way tool/version-control/test builds
        one for the same rule in #72 -- never this repository's own dev.
    #>
    BeforeAll {
        function New-BranchFixture {
            # A repository with one commit on dev, pushed to a bare remote and
            # fetched back, plus a master branch: exactly the shape
            # Get-WinEnvCaptureBranchPlan and New-WinEnvCaptureBranch read.
            $token = [guid]::NewGuid().ToString('N')
            $remote = Join-Path $TestDrive "branch-remote-$token.git"
            $repo = Join-Path $TestDrive "branch-repo-$token"
            [void](New-Item -ItemType Directory -Path $repo -Force)

            & git init -q --bare -b dev $remote | Out-Null
            & git -C $repo init -q -b dev | Out-Null
            & git -C $repo config user.name Fixture | Out-Null
            & git -C $repo config user.email fixture@example.invalid | Out-Null
            & git -C $repo remote add origin $remote | Out-Null
            [IO.File]::WriteAllText((Join-Path $repo 'seed.txt'), 'seed')
            & git -C $repo add -- seed.txt | Out-Null
            & git -C $repo commit -q -m 'seed' | Out-Null
            & git -C $repo push -q --set-upstream origin dev | Out-Null
            & git -C $repo branch -q master | Out-Null

            return [pscustomobject]@{ Repo = $repo; Remote = $remote }
        }

        function Get-FixtureBranches {
            param([Parameter(Mandatory)][string] $Repo)
            return @(& git -C $Repo for-each-ref --format='%(refname)' refs/heads)
        }

        function Get-FixtureCurrentBranch {
            param([Parameter(Mandatory)][string] $Repo)
            return (& git -C $Repo branch --show-current).Trim()
        }
    }

    It 'refuses on master without reading the remote at all' {
        $fixture = New-BranchFixture
        & git -C $fixture.Repo switch -q master | Out-Null
        # No origin/dev ref at all would make a remote-reading refusal true by
        # accident; deleting it proves master is decided first.
        & git -C $fixture.Repo update-ref -d refs/remotes/origin/dev | Out-Null

        $plan = Get-WinEnvCaptureBranchPlan -RepositoryRoot $fixture.Repo -BranchName 'feature/windows-capture-font'
        $plan.Status | Should -Be 'Refused'
        $plan.Branch | Should -BeNullOrEmpty
        $plan.Message | Should -Match 'master'
    }

    It 'commits where it is on a branch that is not dev or master' {
        $fixture = New-BranchFixture
        & git -C $fixture.Repo switch -q -c feature/windows-existing | Out-Null

        $plan = Get-WinEnvCaptureBranchPlan -RepositoryRoot $fixture.Repo -BranchName 'feature/windows-capture-font'
        $plan.Status | Should -Be 'Current'
        $plan.Branch | Should -Be 'feature/windows-existing'
    }

    It 'refuses when origin/dev has never been fetched' {
        $fixture = New-BranchFixture
        & git -C $fixture.Repo update-ref -d refs/remotes/origin/dev | Out-Null

        $plan = Get-WinEnvCaptureBranchPlan -RepositoryRoot $fixture.Repo -BranchName 'feature/windows-capture-font'
        $plan.Status | Should -Be 'Refused'
        $plan.Message | Should -Match 'origin/dev is unavailable'
    }

    It 'refuses when local dev has moved past a stale origin/dev' {
        $fixture = New-BranchFixture
        [IO.File]::WriteAllText((Join-Path $fixture.Repo 'seed.txt'), 'changed locally')
        & git -C $fixture.Repo commit -q -a -m 'advance dev locally' | Out-Null

        $plan = Get-WinEnvCaptureBranchPlan -RepositoryRoot $fixture.Repo -BranchName 'feature/windows-capture-font'
        $plan.Status | Should -Be 'Refused'
        $plan.Message | Should -Match 'dev is not at origin/dev'
    }

    It 'refuses a branch name that already exists' {
        $fixture = New-BranchFixture
        & git -C $fixture.Repo branch -q feature/windows-capture-font | Out-Null

        $plan = Get-WinEnvCaptureBranchPlan -RepositoryRoot $fixture.Repo -BranchName 'feature/windows-capture-font'
        $plan.Status | Should -Be 'Refused'
        $plan.Message | Should -Match 'already exists'
    }

    It 'creates the named branch from origin/dev and leaves dev untouched' {
        $fixture = New-BranchFixture
        $plan = Get-WinEnvCaptureBranchPlan -RepositoryRoot $fixture.Repo -BranchName 'feature/windows-capture-font'
        $plan.Status | Should -Be 'Create'

        $devBefore = (& git -C $fixture.Repo rev-parse dev).Trim()
        $originDev = (& git -C $fixture.Repo rev-parse refs/remotes/origin/dev).Trim()

        $result = New-WinEnvCaptureBranch -RepositoryRoot $fixture.Repo -Branch $plan.Branch
        $result.Status | Should -Be 'Created'
        (Get-FixtureCurrentBranch -Repo $fixture.Repo) | Should -Be 'feature/windows-capture-font'
        (& git -C $fixture.Repo rev-parse HEAD).Trim() | Should -Be $originDev
        # dev itself never moved: this run's branch is a sibling of dev, not a
        # fast-forward of it.
        (& git -C $fixture.Repo rev-parse dev).Trim() | Should -Be $devBefore
    }

    It 'creates nothing when the fetch fails' {
        $fixture = New-BranchFixture
        & git -C $fixture.Repo remote set-url origin (Join-Path $TestDrive 'no-such-remote.git') | Out-Null
        $before = Get-FixtureBranches -Repo $fixture.Repo

        $result = New-WinEnvCaptureBranch -RepositoryRoot $fixture.Repo -Branch 'feature/windows-capture-font'
        $result.Status | Should -Be 'Refused'
        $result.Message | Should -Match 'fetch'
        (Get-FixtureBranches -Repo $fixture.Repo) | Should -Be $before
        (Get-FixtureCurrentBranch -Repo $fixture.Repo) | Should -Be 'dev'
    }

    It 'refuses and creates nothing when origin/dev moves while waiting for an answer' {
        $fixture = New-BranchFixture
        # A second clone pushes past the origin/dev this repo already fetched,
        # standing in for another change landing while the operator reads the
        # diff between the plan and the confirmation.
        $other = Join-Path $TestDrive ('branch-race-' + [guid]::NewGuid().ToString('N'))
        & git clone -q $fixture.Remote $other | Out-Null
        & git -C $other config user.name Fixture | Out-Null
        & git -C $other config user.email fixture@example.invalid | Out-Null
        [IO.File]::WriteAllText((Join-Path $other 'seed.txt'), 'raced')
        & git -C $other commit -q -a -m 'a change that landed during the wait' | Out-Null
        & git -C $other push -q origin dev | Out-Null

        $before = Get-FixtureBranches -Repo $fixture.Repo
        $result = New-WinEnvCaptureBranch -RepositoryRoot $fixture.Repo -Branch 'feature/windows-capture-font'
        $result.Status | Should -Be 'Refused'
        $result.Message | Should -Match 'moved'
        (Get-FixtureBranches -Repo $fixture.Repo) | Should -Be $before
        (Get-FixtureCurrentBranch -Repo $fixture.Repo) | Should -Be 'dev'
    }

    It 'writes nothing under -WhatIf' {
        $fixture = New-BranchFixture
        $before = Get-FixtureBranches -Repo $fixture.Repo

        [void](New-WinEnvCaptureBranch -RepositoryRoot $fixture.Repo -Branch 'feature/windows-capture-font' -WhatIf)
        (Get-FixtureBranches -Repo $fixture.Repo) | Should -Be $before
        (Get-FixtureCurrentBranch -Repo $fixture.Repo) | Should -Be 'dev'
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
