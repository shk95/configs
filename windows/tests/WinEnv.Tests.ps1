BeforeAll {
    $testsRoot = Split-Path -Parent $PSCommandPath
    $repositoryRoot = Split-Path -Parent $testsRoot
    # INV windows/no-unix-host-required — the suite reads the Windows tree
    # only. The one path it takes above it is the repository's own git
    # metadata, for the applied-commit case, which is repository state
    # rather than another domain's tree; the 'Windows tree isolation' cases
    # below scan every script here for a read into a Unix-like tree.
    $desiredStateRoot = Join-Path $repositoryRoot 'desired'
    Import-Module (Join-Path $repositoryRoot 'src\WinEnv.psm1') -Force
    # Invoke-Pester can be called without test.ps1; the suite defends itself.
    . (Join-Path $repositoryRoot 'tools\isolate-git.ps1')

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
    It 'INV windows/schema-version-refused: loads schema 4 and the desired-state compatibility version' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $manifest.SchemaVersion | Should -Be 4
        $manifest.ProjectVersion | Should -Be '0.6.0'
    }

    It 'INV windows/schema-version-refused: refuses a manifest schema this module does not read' {
        $path = Join-Path $TestDrive 'manifest-schema5.json'
        [IO.File]::WriteAllText($path, '{"SchemaVersion":5,"ProjectVersion":"1.0.0"}')
        $message = $null
        try { Get-WinEnvManifest -Path $path | Out-Null } catch { $message = $_.Exception.Message }
        $message | Should -Match 'INV windows/schema-version-refused'
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
        # #67: the Windows font list names a Mono and a non-Mono D2Koding
        # family. A fixture must fail if either family has no registered
        # face; the list is this domain's own copy and is held to this
        # domain's manifest, not to the Unix-like copy it was taken from
        # (INV windows/no-unix-host-required took the byte comparison out,
        # and with it the guard against a `windowsChecks` addendum, a key
        # nothing on Windows consumes).
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $fonts = Get-Content (Join-Path $desiredStateRoot 'files\wezterm\fonts.json') -Raw | ConvertFrom-Json
        $registeredFamilies = @($manifest.Font.Files | ForEach-Object { $_.FullName -replace ' Bold$', '' }) |
            Sort-Object -Unique
        foreach ($family in $fonts.families) {
            $registeredFamilies | Should -Contain $family
        }
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
        # gate table in
        # docs/decisions/wslconfig-selected-by-windows-build.md.
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

Describe 'JSON ownership' {
    It 'INV windows/subset-owns-declared-keys: allows runtime properties in subset mode' {
        $expected = '{"enabled":true,"nested":{"value":7}}' | ConvertFrom-Json
        $actual = '{"enabled":true,"nested":{"value":7,"runtime":"ignored"},"version":"dynamic"}' | ConvertFrom-Json
        (Test-WinEnvJsonSubset -Expected $expected -Actual $actual) | Should -Be $true
    }

    It 'INV windows/subset-owns-declared-keys: detects changed managed properties' {
        $expected = '{"enabled":true,"items":[1,2]}' | ConvertFrom-Json
        $actual = '{"enabled":false,"items":[1,2]}' | ConvertFrom-Json
        (Test-WinEnvJsonSubset -Expected $expected -Actual $actual) | Should -Be $false
    }
}

Describe 'JsonSubset projection' {
    BeforeAll {
        # The projection returns text, and every assertion below is about the
        # document rather than about how ConvertTo-Json spaced it.
        function Get-Projection {
            param([string] $Declared, [string] $Actual)
            $projected = ConvertTo-WinEnvJsonSubsetProjection -DeclaredContent $Declared -HostContent $Actual
            return ($projected | ConvertFrom-Json -Depth 100)
        }

        function Get-ProjectionText {
            param([string] $Declared, [string] $Actual)
            $projected = ConvertTo-WinEnvJsonSubsetProjection -DeclaredContent $Declared -HostContent $Actual
            return ((ConvertFrom-Json -InputObject $projected -NoEnumerate) | ConvertTo-Json -Depth 100 -Compress)
        }

        function Get-ProjectionError {
            param([string] $Declared, [string] $Actual)
            try {
                [void](ConvertTo-WinEnvJsonSubsetProjection -DeclaredContent $Declared -HostContent $Actual)
                return ''
            }
            catch { return [string]$_.Exception.Message }
        }
    }

    It 'takes the host value of every key the payload declares' {
        $projected = Get-Projection '{"a":1,"b":{"c":2}}' '{"a":9,"b":{"c":8}}'
        $projected.a | Should -Be 9
        $projected.b.c | Should -Be 8
    }

    It 'never captures a key the payload does not declare' {
        # The whole mechanism in one case: the host file mixes the two settings
        # the payload manages with the version stamp, the timestamp and the
        # telemetry flag the application keeps beside them. None of the three
        # is declared, so none of the three can reach desired state -- not
        # because they are named anywhere, but because the payload does not
        # declare them.
        $declared = '{"properties":{"mode":0},"name":"Sample"}'
        $actual = '{"properties":{"mode":2,"expirationDateTime":"2026-01-01T00:00:00Z"},' +
        '"name":"Sample","version":"3.1.4","telemetry":{"optedIn":true}}'
        $text = Get-ProjectionText $declared $actual

        $text | Should -Be '{"properties":{"mode":2},"name":"Sample"}'
        $text | Should -Not -Match 'version'
        $text | Should -Not -Match 'expirationDateTime'
        $text | Should -Not -Match 'telemetry'
    }

    It 'converges the comparison that reported the drift' {
        # The invariant the whole mechanism rests on, asserted through
        # Test-WinEnvJsonSubset itself rather than restated: there is no host
        # this can project from and leave drifted.
        $declared = '{"a":1,"list":[{"x":1}],"nested":{"deep":{"k":"old"}}}'
        $actual = '{"a":2,"list":[{"x":5,"extra":true},{"y":6}],"nested":{"deep":{"k":"new","runtime":1}},"stamp":7}'
        (Test-WinEnvJsonSubset -Expected ($declared | ConvertFrom-Json) -Actual ($actual | ConvertFrom-Json)) |
            Should -Be $false

        $projected = Get-Projection $declared $actual
        (Test-WinEnvJsonSubset -Expected $projected -Actual ($actual | ConvertFrom-Json)) | Should -Be $true
    }

    It 'projects a list element onto the declared element and takes the rest as the host holds them' {
        # The read side compares a list by position and requires equal length,
        # so a payload cannot declare a member subset that outlives a length
        # change. Element 0 has a declared shape and loses the member the
        # payload never declared; element 1 has none and arrives whole.
        $text = Get-ProjectionText '{"l":[{"a":1}]}' '{"l":[{"a":5,"extra":9},{"b":2,"c":3}]}'
        $text | Should -Be '{"l":[{"a":5},{"b":2,"c":3}]}'
    }

    It 'shortens a declared list to the length the host holds' {
        $text = Get-ProjectionText '{"l":[{"a":1},{"a":2}]}' '{"l":[{"a":7}]}'
        $text | Should -Be '{"l":[{"a":7}]}'
    }

    It 'keeps a list nested inside a list from collapsing into its parent' {
        # A projected element that is itself a list would be flattened by an
        # array subexpression, which would silently rewrite the document's
        # shape rather than fail.
        $text = Get-ProjectionText '{"l":[[1,2]]}' '{"l":[[3,4]]}'
        $text | Should -Be '{"l":[[3,4]]}'
    }

    It 'reads a document whose root is a one-element array as a list' {
        # ConvertFrom-Json writes a top-level array's elements to the pipeline
        # one at a time, so without -NoEnumerate this document would reach the
        # projection as its single element and be refused as a shape change.
        $text = Get-ProjectionText '[{"a":1}]' '[{"a":2,"x":3},{"z":4}]'
        $text | Should -Be '[{"a":2},{"z":4}]'
    }

    It 'INV windows/declared-list-has-content: declares nothing by declaring an empty object, and everything by declaring an empty list' {
        # Not a quirk of this direction but the read side's own asymmetry,
        # carried across unchanged: a declared object is a member subset, so an
        # empty one owns no member and can never drift; a declared list is
        # positional and length-exact, so an empty one owns the whole list.
        (Get-ProjectionText '{"m":{}}' '{"m":{"k":1}}') | Should -Be '{"m":{}}'
        (Get-ProjectionText '{"l":[]}' '{"l":[1,2]}') | Should -Be '{"l":[1,2]}'
    }

    It 'writes the host value under the name the payload declares' {
        # The member lookup is the comparison's own, which is case-insensitive.
        # A host that respells a declared key is a key the read side already
        # found, and the payload keeps its own spelling across captures.
        (Get-ProjectionText '{"Alpha":1}' '{"alpha":42}') | Should -Be '{"Alpha":42}'
    }

    It 'moves a declared value between a scalar and null in both directions' {
        # The read side treats a declared null as a leaf, so a settings key
        # that moves between a path and null is an ordinary value change.
        (Get-ProjectionText '{"p":null}' '{"p":"set"}') | Should -Be '{"p":"set"}'
        (Get-ProjectionText '{"p":"set"}' '{"p":null}') | Should -Be '{"p":null}'
    }

    It 'refuses a declared key the host file no longer holds, and names it' {
        $message = Get-ProjectionError '{"properties":{"kept":1,"gone":2}}' '{"properties":{"kept":1}}'
        $message | Should -Match 'no longer holds'
        # The path, not just the leaf name: a refusal an operator cannot act on
        # is worse than no capture at all.
        $message | Should -Match ([regex]::Escape("'properties.gone'"))
    }

    It 'refuses a host value whose shape is not the declared one, in either direction' {
        $scalarForObject = Get-ProjectionError '{"a":{"b":1}}' '{"a":5}'
        $scalarForObject | Should -Match 'holds a scalar'
        $scalarForObject | Should -Match 'declares an object'
        $scalarForObject | Should -Match ([regex]::Escape("at 'a'"))

        $objectForList = Get-ProjectionError '{"a":[1]}' '{"a":{"b":1}}'
        $objectForList | Should -Match 'holds an object'
        $objectForList | Should -Match 'declares a list'

        $rootMismatch = Get-ProjectionError '{"a":1}' '[{"a":1}]'
        $rootMismatch | Should -Match 'at the document root'
    }

    It 'is idempotent on every JsonSubset payload this repository commits' {
        # Each committed payload must already be a shape the projection can
        # express, or the first real capture from a clean host would refuse.
        # Projecting a payload onto itself proves that for the whole inventory
        # without a Windows host, and fails the moment a new payload declares
        # something the mechanism cannot carry.
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $subsets = @($manifest.ManagedFiles | Where-Object { [string]$_.Compare -ceq 'JsonSubset' })
        $subsets.Count | Should -BeGreaterThan 0

        foreach ($definition in $subsets) {
            $payload = Get-Content -LiteralPath (Join-Path $desiredStateRoot ([string]$definition.Source)) `
                -Raw -Encoding utf8
            $projected = ConvertTo-WinEnvJsonSubsetProjection -DeclaredContent $payload -HostContent $payload
            # Canonical rather than textual: the payload is pretty-printed and
            # the projection is not, and only the document is under test.
            (ConvertTo-WinEnvCanonicalJson $projected) |
                Should -Be (ConvertTo-WinEnvCanonicalJson $payload) -Because "$($definition.Id) must project onto itself"
        }
    }
}

Describe 'PowerToys payload audit' {
    # Three keys the #93 audit of PowerToys' own settings models found and
    # decided about. Each is asserted individually rather than through a list
    # of forbidden names: a name list would be the second declaration of what a
    # payload owns that the projection exists to avoid, and each of these has
    # its own reason that a shared list would flatten away.
    BeforeAll {
        function Get-PowerToysPayload {
            param([string] $Relative)
            return (Get-Content -LiteralPath (Join-Path $desiredStateRoot "files/powertoys/$Relative") `
                    -Raw -Encoding utf8 | ConvertFrom-Json -Depth 100)
        }
    }

    It 'INV windows/declared-list-has-content: declares no empty list anywhere in a JsonSubset payload' {
        # The one shape in which a payload can silently absorb host state, and
        # the finding that review caught (#100). A declared list is exact --
        # the read side matches it by position and requires equal length -- so
        # an empty declared list is not "owns nothing", it is "owns whatever
        # the host holds". The PowerToys inventory declared twenty-eight of
        # them, and capture would have absorbed CmdPal's monitor topology and
        # its installed-extension ranking through two of them.
        #
        # The rule is uniform, so this needs no allowlist: a list is declared
        # only when there is content to declare. A key left undeclared owns
        # nothing, which is what an empty list cannot express. Assert it over
        # the manifest rather than over a fixed file list, so a payload added
        # later is covered the day it is declared.
        function Get-EmptyListPath {
            param($Node, [string] $Path)
            if ($Node -is [System.Collections.IList]) {
                if (@($Node).Count -eq 0) { return $Path }
                $found = @()
                for ($i = 0; $i -lt @($Node).Count; $i++) {
                    $found += @(Get-EmptyListPath -Node @($Node)[$i] -Path "$Path[$i]")
                }
                return $found
            }
            if ($null -eq $Node -or $Node -is [string] -or $Node -is [ValueType]) { return @() }
            $found = @()
            foreach ($property in $Node.PSObject.Properties) {
                $child = if ([string]::IsNullOrEmpty($Path)) { $property.Name } else { "$Path.$($property.Name)" }
                $found += @(Get-EmptyListPath -Node $property.Value -Path $child)
            }
            return $found
        }

        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $subsets = @($manifest.ManagedFiles | Where-Object { [string]$_.Compare -ceq 'JsonSubset' })
        $subsets.Count | Should -BeGreaterThan 0

        foreach ($definition in $subsets) {
            $document = Get-Content -LiteralPath (Join-Path $desiredStateRoot ([string]$definition.Source)) `
                -Raw -Encoding utf8 | ConvertFrom-Json -Depth 100
            $empty = @(Get-EmptyListPath -Node $document -Path '')
            $empty -join ', ' | Should -Be '' `
                -Because "$($definition.Id) must declare a list only where it has content to declare"
        }
    }

    It 'declares no AI provider list for Advanced Paste' {
        # A declared list is captured as the host holds it, so declaring
        # `providers` would let one capture copy an API key or endpoint out of
        # the maintainer's host and into a committed payload. Desired state
        # says AI paste is off with no active provider, which needs neither.
        $advancedPaste = Get-PowerToysPayload 'AdvancedPaste/settings.json'
        $configuration = $advancedPaste.properties.'paste-ai-configuration'
        $configuration.PSObject.Properties['active-provider-id'] | Should -Not -BeNullOrEmpty
        $configuration.PSObject.Properties['providers'] | Should -BeNullOrEmpty
        $advancedPaste.properties.IsAIEnabled.value | Should -Be $false
        # custom-actions carries the same hazard in the same file: a user's
        # free-text AI prompts, captured verbatim through an empty declared
        # list. AI paste is off in desired state, so a custom action is inert.
        $advancedPaste.properties.PSObject.Properties['custom-actions'] | Should -BeNullOrEmpty
    }

    It 'declares no Awake expiry timestamp' {
        # PowerToys initialises expirationDateTime to the moment the file is
        # created and rewrites it whenever the module's state changes. It is a
        # timestamp, not a setting, and AGENTS.md keeps runtime state out of
        # every domain.
        $awake = Get-PowerToysPayload 'Awake/settings.json'
        $awake.properties.PSObject.Properties['expirationDateTime'] | Should -BeNullOrEmpty
        # The four values that do describe intent are still declared, so this
        # is an exclusion rather than an unmanaged file.
        foreach ($name in @('keepDisplayOn', 'mode', 'intervalHours', 'intervalMinutes')) {
            $awake.properties.PSObject.Properties[$name] | Should -Not -BeNullOrEmpty -Because "Awake declares $name"
        }
    }

    It 'declares none of the root settings PowerToys computes at runtime' {
        # The runner rewrites each of these from the live host -- the product
        # version, the elevation checks, the detected OS theme, and a one-shot
        # IPC field -- so a captured payload holding one would be a snapshot of
        # one machine's session. PowerToys' own backup manifest ignores
        # powertoys_version for the same reason.
        $root = Get-PowerToysPayload 'settings.json'
        foreach ($name in @('powertoys_version', 'is_elevated', 'is_admin', 'system_theme', 'action_name')) {
            $root.PSObject.Properties[$name] | Should -BeNullOrEmpty -Because "the root payload must not declare $name"
        }
        # run_elevated and startup are the genuine settings beside them and
        # stay declared. PowerToys does reconcile startup against the live
        # scheduled task, so review asked whether it belongs above (#100). It
        # does not: the test is not "does the application write it back" --
        # PowerToys writes all of these back -- but "does it change without the
        # maintainer changing anything". powertoys_version moves on every
        # upgrade, is_elevated on how the process launched, system_theme with
        # the OS. startup moves only when someone chooses it, which is what a
        # declared setting is.
        $root.PSObject.Properties['run_elevated'] | Should -Not -BeNullOrEmpty
        $root.PSObject.Properties['startup'] | Should -Not -BeNullOrEmpty
    }

    It 'declares no computed default-shortcut member' {
        # PowerToys serialises a get-only DefaultActivationShortcut /
        # DefaultEditorShortcut into these three files. It is a constant the
        # application recomputes, not a setting, and it is version-specific, so
        # declaring it would make desired state carry a value no maintainer
        # chose. The real shortcut beside it stays declared.
        $peek = Get-PowerToysPayload 'Peek/settings.json'
        $peek.properties.PSObject.Properties['DefaultActivationShortcut'] | Should -BeNullOrEmpty
        $peek.properties.PSObject.Properties['ActivationShortcut'] | Should -Not -BeNullOrEmpty

        $findMyMouse = Get-PowerToysPayload 'FindMyMouse/settings.json'
        $findMyMouse.properties.PSObject.Properties['DefaultActivationShortcut'] | Should -BeNullOrEmpty
        $findMyMouse.properties.PSObject.Properties['activation_shortcut'] | Should -Not -BeNullOrEmpty

        $keyboardManager = Get-PowerToysPayload 'Keyboard Manager/settings.json'
        $keyboardManager.properties.PSObject.Properties['DefaultEditorShortcut'] | Should -BeNullOrEmpty
        $keyboardManager.properties.PSObject.Properties['EditorShortcut'] | Should -Not -BeNullOrEmpty
    }

    It 'keeps the module version each file migrates on' {
        # Peek migrates when version is absent or "0.0.1", and that migration
        # also forces EnableSpaceToActivate off; FindMyMouse migrates from
        # "1.0". Declaring the post-migration literal is what stops Apply from
        # re-triggering either one on every reconcile.
        (Get-PowerToysPayload 'Peek/settings.json').version | Should -Be '0.0.2'
        (Get-PowerToysPayload 'FindMyMouse/settings.json').version | Should -Be '1.1'
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

    It 'INV windows/compare-mode-declared: rejects the generated-profile mode on an entry whose parser is not Json' {
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

    It 'INV windows/compare-mode-declared: rejects a comparison mode no entry can be compared with' {
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

    It 'INV windows/compare-mode-declared: gives the tolerance to the one file Windows Terminal co-owns' {
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
    It 'INV windows/external-profile-blocks-preserved: adds one block and preserves existing external blocks' {
        $profile = Join-Path $TestDrive 'profile.ps1'
        [IO.File]::WriteAllText($profile, "#region sysmon-banner`r`n'SysMon'`r`n#endregion sysmon-banner`r`n")
        Set-WinEnvProfileHook -ProfilePath $profile
        Set-WinEnvProfileHook -ProfilePath $profile
        $content = Get-Content -LiteralPath $profile -Raw
        ([regex]::Matches($content, '(?m)^#region win-env\r?$')).Count | Should -Be 1
        $content | Should -Match '#region sysmon-banner'
        (Test-WinEnvProfileHook -ProfilePath $profile) | Should -Be $true
    }

    It 'INV windows/external-profile-blocks-preserved: refuses unmatched markers' {
        $profile = Join-Path $TestDrive 'broken-profile.ps1'
        [IO.File]::WriteAllText($profile, "#region win-env`r`n")
        (Test-Throws { Set-WinEnvProfileHook -ProfilePath $profile }) | Should -Be $true
    }

    # A regression guard on the committed payload, not a rule: a profile that
    # prints in a non-interactive process breaks any program that starts
    # pwsh and reads its output. It names no invariant.
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
        # The repository root, the way setup.ps1 resolves it for
        # Get-WinEnvGitCommit: git metadata is repository state, not a
        # Unix-like tree (INV windows/no-unix-host-required).
        (Get-WinEnvGitCommit -RepositoryRoot (Split-Path -Parent $repositoryRoot)) | Should -Match '^(unborn|[0-9a-f]{40})$'
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

    It 'INV windows/schema-version-refused: refuses a state schema this module does not read' {
        $path = Join-Path $TestDrive 'schema3.json'
        [IO.File]::WriteAllText($path, '{"schemaVersion":3,"projectVersion":"0.1.0","appliedAtUtc":"2026-01-01T00:00:00+00:00","gitCommit":"0123456789abcdef","features":["core"]}')
        $message = $null
        try { Get-WinEnvState -Path $path | Out-Null } catch { $message = $_.Exception.Message }
        $message | Should -Match 'INV windows/schema-version-refused'
    }

    It 'INV windows/hash-covers-selection: changes the desired-state hash when content changes' {
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

    It 'INV windows/hash-covers-selection: ignores a payload the selection excludes' {
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

    It 'INV windows/hash-covers-selection: covers the manifest itself' {
        $manifest = New-FeatureManifest
        $root = Join-Path $TestDrive 'desired-manifest'
        [void](New-Item -ItemType Directory -Path (Join-Path $root 'files') -Force)
        [IO.File]::WriteAllText((Join-Path $root 'files\profile.ps1'), 'core')
        [IO.File]::WriteAllText((Join-Path $root 'manifest.json'), '{}')
        $before = Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core')
        [IO.File]::WriteAllText((Join-Path $root 'manifest.json'), '{"changed":true}')
        $after = Get-WinEnvDesiredStateHash -Root $root -Manifest $manifest -Feature @('core')
        $after | Should -Not -Be $before
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

    It 'INV windows/feature-owns-every-item: declares every deployable desired-state payload exactly once' {
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
    It 'INV windows/feature-owns-every-item: owns every deployable item with a declared feature' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        $declared = Get-WinEnvFeatureId -Manifest $manifest
        foreach ($package in $manifest.Packages) { $declared | Should -Contain $package.Feature }
        foreach ($definition in $manifest.ManagedFiles) { $declared | Should -Contain $definition.Feature }
        $declared | Should -Contain $manifest.Font.Feature
        $declared | Should -Contain $manifest.Terminal.Feature
    }

    It 'INV windows/feature-owns-every-item: rejects a deployable item that names no feature' {
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(@{ Id = 'orphan'; Source = 'files/orphan.txt'; Target = 'orphan'; Compare = 'Text'; Parser = 'Text' })
        }
        (Test-Throws { Assert-WinEnvFeatureModel -Manifest $manifest }) | Should -Be $true
    }

    It 'INV windows/feature-owns-every-item: rejects an item that names an undeclared feature' {
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

Describe 'identifier uniqueness' {
    BeforeAll {
        function Get-FeatureModelRefusal {
            param([hashtable] $Manifest)
            $message = $null
            try { Assert-WinEnvFeatureModel -Manifest $Manifest } catch { $message = $_.Exception.Message }
            return $message
        }
    }

    It 'INV windows/unique-ids: refuses a feature id declared twice' {
        $manifest = New-FeatureManifest -Override @{
            Features = @(
                @{ Id = 'core'; Name = 'Core'; Required = $true },
                @{ Id = 'font'; Name = 'Font' },
                @{ Id = 'font'; Name = 'Font again' },
                @{ Id = 'zellij'; Name = 'Zellij' },
                @{ Id = 'terminal'; Name = 'Terminal'; Requires = @('font', 'zellij') }
            )
        }
        (Get-FeatureModelRefusal -Manifest $manifest) | Should -Match 'INV windows/unique-ids'
    }

    It 'INV windows/unique-ids: refuses a package id declared twice' {
        $manifest = New-FeatureManifest -Override @{
            Packages = @(
                @{ Id = 'Vendor.Shell'; Feature = 'core'; Bootstrap = $true; Detection = 'Command'; Command = 'pwsh.exe' },
                @{ Id = 'Vendor.Shell'; Feature = 'font'; Detection = 'WinGet' }
            )
        }
        (Get-FeatureModelRefusal -Manifest $manifest) | Should -Match "INV windows/unique-ids: The package 'Vendor.Shell' is declared more than once"
    }

    It 'INV windows/unique-ids: refuses a managed-file id declared twice' {
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(
                @{ Id = 'profile'; Feature = 'core'; Source = 'files/profile.ps1'; Target = 'profile'; Compare = 'Text'; Parser = 'PowerShell' },
                @{ Id = 'profile'; Feature = 'terminal'; Source = 'files/other.ps1'; Target = 'other'; Compare = 'Text'; Parser = 'PowerShell' }
            )
        }
        (Get-FeatureModelRefusal -Manifest $manifest) | Should -Match "INV windows/unique-ids: The managed file 'profile' is declared more than once"
    }

    It 'INV windows/unique-ids: refuses a package or managed file declared without an Id' {
        $package = New-FeatureManifest -Override @{
            Packages = @(@{ Feature = 'core'; Detection = 'WinGet' })
        }
        (Get-FeatureModelRefusal -Manifest $package) | Should -Match 'INV windows/unique-ids: A package is declared without an Id'

        $file = New-FeatureManifest -Override @{
            ManagedFiles = @(@{ Id = ''; Feature = 'core'; Source = 'files/profile.ps1'; Target = 'profile'; Compare = 'Text'; Parser = 'PowerShell' })
        }
        (Get-FeatureModelRefusal -Manifest $file) | Should -Match 'INV windows/unique-ids: A managed file is declared without an Id'
    }

    It 'INV windows/unique-ids: keeps packages and managed files as separate namespaces' {
        # A plan names a package or a managed file, never "an item", so one
        # spelling in both lists is unambiguous; the same spelling twice in
        # one list is what the rule refuses.
        $manifest = New-FeatureManifest -Override @{
            Packages     = @(@{ Id = 'profile'; Feature = 'core'; Bootstrap = $true; Detection = 'Command'; Command = 'pwsh.exe' })
            ManagedFiles = @(@{ Id = 'profile'; Feature = 'core'; Source = 'files/profile.ps1'; Target = 'profile'; Compare = 'Text'; Parser = 'PowerShell' })
        }
        (Get-FeatureModelRefusal -Manifest $manifest) | Should -BeNullOrEmpty
    }

    It 'INV windows/unique-ids: loads the repository manifest, whose ids are distinct' {
        $manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
        foreach ($list in @($manifest.Packages, $manifest.ManagedFiles)) {
            $ids = @($list | ForEach-Object { [string]$_.Id })
            @($ids | Sort-Object -Unique).Count | Should -Be $ids.Count
        }
    }
}

Describe 'parser declaration' {
    BeforeAll {
        function New-ParserManifest {
            param([hashtable] $Entry)
            $definition = @{ Id = 'payload'; Feature = 'core'; Source = 'files/payload'; Target = 'payload'; Compare = 'Text' }
            foreach ($key in $Entry.Keys) { $definition[$key] = $Entry[$key] }
            return New-FeatureManifest -Override @{ ManagedFiles = @($definition) }
        }

        function Get-ManagedFileRefusal {
            param([hashtable] $Manifest)
            $message = $null
            try { Assert-WinEnvManagedFileModel -Manifest $Manifest } catch { $message = $_.Exception.Message }
            return $message
        }
    }

    It 'INV windows/parser-declared: refuses a parser the domain has no validator for when the manifest loads' {
        # A misspelling and a case slip are the two ways a name that is
        # almost right would have fallen through the validator as parsed.
        foreach ($parser in @('Yaml', 'json', 'Powershell')) {
            (Get-ManagedFileRefusal -Manifest (New-ParserManifest -Entry @{ Parser = $parser })) |
                Should -Match "INV windows/parser-declared: The managed file 'payload' declares unknown parser '$parser'"
        }
    }

    It 'INV windows/parser-declared: refuses a managed file that declares no parser' {
        (Get-ManagedFileRefusal -Manifest (New-ParserManifest -Entry @{})) |
            Should -Match "INV windows/parser-declared: The managed file 'payload' declares unknown parser ''"
        (Get-ManagedFileRefusal -Manifest (New-ParserManifest -Entry @{ Parser = '' })) |
            Should -Match 'INV windows/parser-declared'
    }

    It 'INV windows/parser-declared: accepts every parser the validator has a case for' {
        # Listed here rather than read from the module on purpose: the case
        # is an independent oracle for the declared list, so a name dropped
        # from the module fails here instead of disappearing from both.
        foreach ($parser in @('Json', 'Ini', 'PowerShell', 'Kdl', 'Lua', 'Text')) {
            (Get-ManagedFileRefusal -Manifest (New-ParserManifest -Entry @{ Parser = $parser })) | Should -BeNullOrEmpty
        }
    }

    It 'INV windows/parser-declared: the validator refuses an unknown or missing parser instead of counting the source as parsed' {
        # Reaches the validator without the loader, the way a definition
        # built in code would. Before the default arm this returned $null,
        # which every caller reads as "parsed".
        $root = Join-Path $TestDrive 'parser-declared'
        [void](New-Item -ItemType Directory -Path $root -Force)
        [IO.File]::WriteAllText((Join-Path $root 'payload.yaml'), "key: value`n")
        foreach ($definition in @(
                @{ Id = 'payload'; Source = 'payload.yaml'; Parser = 'Yaml' },
                @{ Id = 'payload'; Source = 'payload.yaml' }
            )) {
            $message = $null
            try { Test-WinEnvSourceFile -Definition $definition -RepositoryRoot $root | Out-Null } catch { $message = $_.Exception.Message }
            $message | Should -Match "INV windows/parser-declared: No validator exists for parser '(Yaml|)' declared on 'payload.yaml'"
        }
    }
}

Describe 'feature selection' {
    It 'reduces a bare selection to the required features' {
        $selection = Get-WinEnvFeatureSelection -Manifest (New-FeatureManifest)
        ($selection.Selected -join ',') | Should -Be 'core'
        $selection.Excluded | Should -Contain 'terminal'
    }

    It 'INV windows/selection-closed-and-explicit: closes over declared dependencies and reports what it added' {
        $selection = Get-WinEnvFeatureSelection -Manifest (New-FeatureManifest) -Requested @('terminal')
        ($selection.Selected -join ',') | Should -Be 'core,font,zellij,terminal'
        (($selection.Implied | Sort-Object) -join ',') | Should -Be 'font,zellij'
        $selection.Excluded.Count | Should -Be 0
    }

    It 'INV windows/selection-closed-and-explicit: keeps a dependency selectable on its own' {
        $selection = Get-WinEnvFeatureSelection -Manifest (New-FeatureManifest) -Requested @('zellij')
        ($selection.Selected -join ',') | Should -Be 'core,zellij'
        $selection.Excluded | Should -Contain 'terminal'
    }

    It 'INV windows/selection-closed-and-explicit: rejects an unknown feature instead of silently ignoring it' {
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

    It 'INV windows/check-exit-contract: ranks drift above an undecidable item in the check exit contract' {
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

    It 'INV windows/check-exit-contract: turns an undecidable item into a failure when native evidence is required' {
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

    It 'INV windows/font-state-total: calls a valid registered subset of a grown manifest incomplete, not a conflict' {
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

    It 'INV windows/font-state-total: still calls a file that is not the one the manifest pins a conflict' {
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

    It 'INV windows/font-state-total: refuses a foreign registration even on a host holding every file' {
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

    It 'INV windows/font-state-total: reports exactly one state for every fixture' {
        # The five states are a partition, which is what lets the check and
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

    It 'INV windows/hash-covers-selection: hashes every declared variant so the desired state cannot depend on the host' {
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

    It 'INV windows/sources-total-function: refuses a variant list whose last entry is conditional' {
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

    It 'INV windows/sources-total-function: refuses bounds that do not descend' {
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

    It 'INV windows/sources-total-function: refuses an entry declaring both a scalar Source and alternatives' {
        $definition = New-ConditionalFile -Sources @(
            @{ MinimumBuild = 22621; Source = 'files/upper.ini' },
            @{ Source = 'files/lower.ini' })
        $definition.Source = 'files/plain.ini'
        $manifest = New-FeatureManifest -Override @{ ManagedFiles = @($definition) }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
    }

    It 'INV windows/sources-total-function: refuses an entry that declares no source at all' {
        $manifest = New-FeatureManifest -Override @{
            ManagedFiles = @(@{ Id = 'orphan'; Feature = 'core'; Target = 'target'; Compare = 'Text'; Parser = 'Ini' })
        }
        (Test-Throws { Assert-WinEnvManagedFileModel -Manifest $manifest }) | Should -Be $true
    }

    It 'INV windows/sources-total-function: refuses a single-variant list and a non-positive bound' {
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

    It 'INV windows/sources-total-function: refuses a variant declaring any key but Source and MinimumBuild' {
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

    It 'INV windows/sources-total-function: refuses a variant whose Source is empty or blank' {
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

    It 'INV windows/sources-total-function: accepts the shape the repository manifest uses' {
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

    It 'INV windows/one-placeholder: restores the one placeholder the deploy direction expands' {
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

    It 'INV windows/one-placeholder: reports a spelling it cannot represent instead of inventing a placeholder' {
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

    It 'captures a JsonSubset payload onto the keys it declares and converges the check' {
        # The headline case the mode used to refuse: the maintainer changed a
        # setting in the application's UI, and the same file also carries the
        # version stamp and the window geometry the application rewrites while
        # it runs.
        $source = New-CapturePayload 'subset.json' "{`n  `"declared`": true`n}`n"
        $target = New-CaptureTarget 'subset.json' `
            '{"declared":false,"version":"1.9.2","window":{"top":11,"left":907}}'
        $definition = New-CaptureDefinition -Id 'subset' -Compare 'JsonSubset' -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Captured'

        $captured = $plan.Content | ConvertFrom-Json
        $captured.declared | Should -Be $false
        # Neither undeclared key reaches desired state, and the payload gained
        # no member at all.
        @($captured.PSObject.Properties | ForEach-Object { $_.Name }) | Should -Be @('declared')
        $plan.Content | Should -Not -Match 'version'
        $plan.Content | Should -Not -Match 'window'

        [void](Save-WinEnvCapturedPayload -Plan $plan -RepositoryRoot $CaptureRoot)
        # The point of the whole change: a JsonSubset file the check called
        # drift is clean afterwards, through the comparison the check uses.
        (Test-WinEnvManagedFile -Definition $definition -RepositoryRoot $CaptureRoot -HostPath $CaptureHost) |
            Should -Be $true
    }

    It 'drops an account path the payload never declared instead of refusing the capture' {
        # The projection runs before the content scans, so a leak the payload
        # does not own is gone by the time they read the content. This is the
        # ordering under test: reversed, every capture from a real PowerToys
        # host would be refused for a path in a key desired state never
        # manages.
        $source = New-CapturePayload 'subset-leak.json' "{`n  `"declared`": 1`n}`n"
        $target = New-CaptureTarget 'subset-leak.json' `
            ('{"declared":2,"recentFile":"' + $JsonUserProfile + '\\notes.txt"}')
        $definition = New-CaptureDefinition -Id 'subsetLeak' -Compare 'JsonSubset' -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Captured'
        (ConvertTo-WinEnvCanonicalJson $plan.Content) | Should -Be '{"declared":2}'
        $plan.Content | Should -Not -Match 'Users'
    }

    It 'still refuses this host''s account name inside a key the payload does declare' {
        # The other half of the rule above. Dropping undeclared keys must not
        # be mistaken for a licence to write a leak the payload owns: every
        # content refusal still reads the projected document.
        $source = New-CapturePayload 'subset-owned-leak.json' "{`n  `"owner`": `"someone`"`n}`n"
        $target = New-CaptureTarget 'subset-owned-leak.json' ('{"owner":"' + $Account + '","other":1}')
        $definition = New-CaptureDefinition -Id 'subsetOwnedLeak' -Compare 'JsonSubset' `
            -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'account'
    }

    It 'refuses a JsonSubset file the payload''s declared shape cannot express' {
        # Both genuinely non-derivable shapes, reported as a refusal with the
        # key path rather than as a crash that would end the run.
        $missingSource = New-CapturePayload 'subset-missing.json' "{`n  `"kept`": 1,`n  `"gone`": 2`n}`n"
        $missingTarget = New-CaptureTarget 'subset-missing.json' '{"kept":9}'
        $missing = Get-WinEnvCapturePlan -RepositoryRoot $CaptureRoot -Build 22631 -HostPath $CaptureHost `
            -Definition (New-CaptureDefinition -Id 'subsetMissing' -Compare 'JsonSubset' `
                -Source $missingSource -Target $missingTarget)
        $missing.Status | Should -Be 'Refused'
        $missing.Reason | Should -Match 'no longer holds'
        $missing.Reason | Should -Match 'gone'

        $shapeSource = New-CapturePayload 'subset-shape.json' "{`n  `"properties`": {`n    `"mode`": 0`n  }`n}`n"
        $shapeTarget = New-CaptureTarget 'subset-shape.json' '{"properties":3}'
        $shape = Get-WinEnvCapturePlan -RepositoryRoot $CaptureRoot -Build 22631 -HostPath $CaptureHost `
            -Definition (New-CaptureDefinition -Id 'subsetShape' -Compare 'JsonSubset' `
                -Source $shapeSource -Target $shapeTarget)
        $shape.Status | Should -Be 'Refused'
        $shape.Reason | Should -Match 'declares an object'
        $shape.Reason | Should -Match 'properties'
    }

    It 'names every declared key a host file no longer holds, not only the first' {
        # #110: the projection itself still throws on the first missing key,
        # which is right for the document it would have returned, but a
        # refusal built from that one throw let three PowerToys payloads each
        # surface a second missing key only after the first was already fixed
        # and captured again. One run has to name all of them.
        $source = New-CapturePayload 'subset-missing-many.json' `
            "{`n  `"properties`": {`n    `"kept`": 1,`n    `"first-gone`": 2`n  },`n  `"second-gone`": 3`n}`n"
        $target = New-CaptureTarget 'subset-missing-many.json' '{"properties":{"kept":9}}'
        $plan = Get-WinEnvCapturePlan -RepositoryRoot $CaptureRoot -Build 22631 -HostPath $CaptureHost `
            -Definition (New-CaptureDefinition -Id 'subsetMissingMany' -Compare 'JsonSubset' `
                -Source $source -Target $target)

        $plan.Status | Should -Be 'Refused'
        $plan.Reason | Should -Match 'no longer holds'
        $plan.Reason | Should -Match ([regex]::Escape("'properties.first-gone'"))
        $plan.Reason | Should -Match ([regex]::Escape("'second-gone'"))
        # Stable and readable: the nested path names before the top-level one
        # that follows it in the declared document, not an arbitrary order.
        $plan.Reason.IndexOf('properties.first-gone') | Should -BeLessThan $plan.Reason.IndexOf('second-gone')
        # Plural wording once there is more than one, so the message still
        # reads as a sentence rather than a list grammar disagrees with.
        $plan.Reason | Should -Match 'keys'
        $plan.Reason | Should -Match 'restore them'
    }

    It 'leaves a JsonSubset file that matches its payload untouched' {
        # Unchanged is still decided before the projection, so a host holding
        # any number of undeclared keys is not reported as a capture.
        $source = New-CapturePayload 'subset-clean.json' "{`n  `"declared`": true`n}`n"
        $target = New-CaptureTarget 'subset-clean.json' '{"declared":true,"version":"9.9.9"}'
        $definition = New-CaptureDefinition -Id 'subsetClean' -Compare 'JsonSubset' -Source $source -Target $target

        $plan = Get-WinEnvCapturePlan -Definition $definition -RepositoryRoot $CaptureRoot `
            -Build 22631 -HostPath $CaptureHost
        $plan.Status | Should -Be 'Unchanged'
        $plan.Content | Should -BeNullOrEmpty
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
        # whether the commit's pre-commit hook actually ran, which #77 has
        # since shown happens under Git for Windows
        # (docs/decisions/hooks-run-under-git-for-windows.md).
        $capturePath = Join-Path $repositoryRoot 'tools\capture.ps1'
        (Test-Path -LiteralPath $capturePath -PathType Leaf) | Should -Be $true

        $tokens = $null; $errors = $null
        $ast = [System.Management.Automation.Language.Parser]::ParseFile($capturePath, [ref]$tokens, [ref]$errors)
        $errors.Count | Should -Be 0

        $parameters = @($ast.ParamBlock.Parameters | ForEach-Object { $_.Name.VariablePath.UserPath })
        $parameters | Should -Contain 'Feature'
        $parameters | Should -Contain 'Id'
        $parameters | Should -Contain 'Branch'
        $parameters | Should -Contain 'Publish'
        # -WhatIf comes from SupportsShouldProcess rather than from a parameter
        # of its own, and there is deliberately no -Yes, -Force or override.
        ($ast.ParamBlock.Attributes | ForEach-Object { $_.Extent.Text }) -join ' ' |
            Should -Match 'SupportsShouldProcess'
        $parameters | Should -Not -Contain 'Force'
        $parameters | Should -Not -Contain 'Yes'
    }

    It 'guards every host read behind Test-WinEnvWindowsHost' {
        # The predicate is one line over the automatic variable and has no
        # fixture of its own. What this suite asserts on any platform without
        # running the script is that the call happens exactly once, ahead of
        # the first host read, and that finding it false is what stops the run.
        $capturePath = Join-Path $repositoryRoot 'tools\capture.ps1'
        $tokens = $null; $errors = $null
        $tree = [System.Management.Automation.Language.Parser]::ParseFile($capturePath, [ref]$tokens, [ref]$errors)
        $errors.Count | Should -Be 0

        $guardCalls = @($tree.FindAll(
                { $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true) |
                Where-Object { $_.GetCommandName() -eq 'Test-WinEnvWindowsHost' })
        $guardCalls.Count | Should -Be 1

        $firstManifestRead = @($tree.FindAll(
                { $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true) |
                Where-Object { $_.GetCommandName() -eq 'Get-WinEnvManifest' }) | Select-Object -First 1
        $firstManifestRead | Should -Not -BeNullOrEmpty
        $guardCalls[0].Extent.StartOffset | Should -BeLessThan $firstManifestRead.Extent.StartOffset

        $guardIf = @($tree.FindAll(
                { $args[0] -is [System.Management.Automation.Language.IfStatementAst] }, $true) |
                Where-Object { $_.Clauses[0].Item1.Extent.Text -match 'Test-WinEnvWindowsHost' }) |
            Select-Object -First 1
        $guardIf | Should -Not -BeNullOrEmpty
        $guardIf.Clauses[0].Item1.Extent.Text | Should -Match '-not'

        $guardBody = @($guardIf.Clauses[0].Item2.FindAll(
                { $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true) |
                ForEach-Object { $_.GetCommandName() })
        $guardBody | Should -Contain 'Stop-Capture'
    }

    It 'refuses to run at all on a non-Windows host' {
        # Genuinely end-to-end, unlike the rest of this Describe block: the
        # guard is the one thing in capture.ps1 that is safe to run for real,
        # anywhere, because it is the only code that runs before any host
        # read or write. On native Windows the real answer is the positive
        # branch instead, where the guard passes and the script would go on
        # to read the host; running the full script here would need a fixture
        # repository this block does not build, and must never be this one.
        if ([Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT) {
            Set-ItResult -Skipped -Because 'this host is Windows, where capture.ps1 does not refuse'
            return
        }

        $capturePath = Join-Path $repositoryRoot 'tools\capture.ps1'
        $pwsh = (Get-Process -Id $PID).Path
        $output = @(& $pwsh -NoLogo -NoProfile -NonInteractive -File $capturePath 2>&1)
        $LASTEXITCODE | Should -Be 1
        ($output -join [Environment]::NewLine) | Should -Match 'only runs on Windows'
        ($output -join [Environment]::NewLine) | Should -Match ([regex]::Escape('tool/version-control/commit --publish'))
    }

    It 'asks the documented question once, and only that question' {
        # The prompt's wording is asserted here rather than in the end-to-end
        # transcript. Windows PowerShell's console host writes a Read-Host
        # prompt to the console device instead of to stdout, so a captured
        # child process never carries it and a transcript assertion would only
        # ever be testing which console the suite ran on. The source is the
        # same on every platform, and one Read-Host is itself the invariant:
        # a second question would be a second confirmation.
        $capturePath = Join-Path $repositoryRoot 'tools\capture.ps1'
        $tokens = $null; $errors = $null
        $tree = [System.Management.Automation.Language.Parser]::ParseFile($capturePath, [ref]$tokens, [ref]$errors)

        $prompts = @($tree.FindAll(
                { $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true) |
                Where-Object { $_.GetCommandName() -eq 'Read-Host' })
        $prompts.Count | Should -Be 1

        $literals = @($tree.FindAll(
                { $args[0] -is [System.Management.Automation.Language.StringConstantExpressionAst] }, $true) |
                ForEach-Object { $_.Value })
        $literals | Should -Contain 'Write these payloads, commit and publish? [y/N]'
        $literals | Should -Contain 'Write these payloads and commit? [y/N]'
    }

    It 'never spells a hook bypass or an administrative merge' {
        # -Publish adds a push and a merge to this tool's reach, and each has a
        # flag that would turn a gate off. Neither may appear in the source at
        # all: an operator may decide to skip a gate, but a tool that took that
        # decision silently would be writing policy rather than implementing it.
        # Read from the commands the parser found rather than from the raw
        # text, so the prose that explains why these flags are absent does not
        # itself trip the guard.
        $sources = @(
            (Join-Path $repositoryRoot 'tools\capture.ps1'),
            (Join-Path $repositoryRoot 'src\WinEnv.psm1'))
        foreach ($source in $sources) {
            $tokens = $null; $errors = $null
            $tree = [System.Management.Automation.Language.Parser]::ParseFile($source, [ref]$tokens, [ref]$errors)
            $commands = @($tree.FindAll(
                    { $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true) |
                    ForEach-Object { $_.Extent.Text })
            $invoked = $commands -join ' '
            $invoked | Should -Not -Match '--no-verify' -Because $source
            $invoked | Should -Not -Match '--force' -Because $source
            $invoked | Should -Not -Match '--admin' -Because $source

            # The same two gates have one-letter spellings: `git push -f` and
            # `git commit -n` bypass exactly what the long flags do, and a
            # guard that only knows the long ones invites the short ones.
            # Scoped to git invocations, because -f and -n mean other things
            # elsewhere in PowerShell.
            $gitCommands = @($commands | Where-Object { $_ -cmatch '(^|\s)git(\s|$)' })
            foreach ($command in $gitCommands) {
                $command | Should -Not -Match '(^|\s)-[fn](\s|$)' -Because "$source : $command"
            }
        }
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

    It 'INV windows/capture-publishes-through-dev: refuses on master without reading the remote at all' {
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

    It 'refuses a -Branch override that fails this repository''s naming policy' {
        # The exact regression a review caught live: README's own example was
        # -Branch fix/font, which tool/version-control/audit rejects for
        # missing the windows- scope prefix. This must refuse before any read
        # of the remote at all, the same as the master refusal does.
        $fixture = New-BranchFixture
        & git -C $fixture.Repo update-ref -d refs/remotes/origin/dev | Out-Null

        $plan = Get-WinEnvCaptureBranchPlan -RepositoryRoot $fixture.Repo -BranchName 'fix/font'
        $plan.Status | Should -Be 'Refused'
        $plan.Branch | Should -BeNullOrEmpty
        $plan.Message | Should -Match 'naming policy'
        # Naming the pattern, not just the symptom, is the point: the operator
        # can fix the name without having to go read tool/version-control/audit.
        $plan.Detail | Should -Match ([regex]::Escape('(feature|fix)/(unixlike|windows|common|repository)-[a-z0-9][a-z0-9-]*'))
    }

    It 'accepts a -Branch override that follows the naming policy' {
        $fixture = New-BranchFixture
        $plan = Get-WinEnvCaptureBranchPlan -RepositoryRoot $fixture.Repo -BranchName 'fix/windows-font'
        $plan.Status | Should -Be 'Create'
        $plan.Branch | Should -Be 'fix/windows-font'

        $originDev = (& git -C $fixture.Repo rev-parse refs/remotes/origin/dev).Trim()
        $result = New-WinEnvCaptureBranch -RepositoryRoot $fixture.Repo -Branch $plan.Branch
        $result.Status | Should -Be 'Created'
        (Get-FixtureCurrentBranch -Repo $fixture.Repo) | Should -Be 'fix/windows-font'
        (& git -C $fixture.Repo rev-parse HEAD).Trim() | Should -Be $originDev
    }

    It 'INV windows/capture-publishes-through-dev: creates the named branch from origin/dev and leaves dev untouched' {
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

Describe 'capture branch pruning' {
    <#
        Remove-WinEnvMergedLocalBranch (#103): GitHub auto-deletes a merged
        pull request's remote branch, but the same branch lingers in this
        clone until something clears it. Every fixture below runs against a
        throwaway working copy and a throwaway bare remote under $TestDrive,
        the same shape Describe 'capture branch' builds -- never this
        repository's own dev.
    #>
    BeforeAll {
        function New-PruneFixture {
            # A repository with one commit on dev, pushed to a bare remote and
            # fetched back, plus a master branch: exactly the shape
            # Remove-WinEnvMergedLocalBranch reads.
            $token = [guid]::NewGuid().ToString('N')
            $remote = Join-Path $TestDrive "prune-remote-$token.git"
            $repo = Join-Path $TestDrive "prune-repo-$token"
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
            return @(& git -C $Repo for-each-ref --format='%(refname:short)' refs/heads)
        }
    }

    It 'INV windows/capture-publishes-through-dev: deletes a local branch already merged into origin/dev' {
        $fixture = New-PruneFixture
        & git -C $fixture.Repo branch -q feature/windows-old-capture | Out-Null

        $result = @(Remove-WinEnvMergedLocalBranch -RepositoryRoot $fixture.Repo)
        $result.Count | Should -Be 1
        $result[0].Branch | Should -Be 'feature/windows-old-capture'
        $result[0].Status | Should -Be 'Deleted'
        (Get-FixtureBranches -Repo $fixture.Repo) | Should -Not -Contain 'feature/windows-old-capture'
    }

    It 'keeps a branch that carries a commit origin/dev does not have' {
        $fixture = New-PruneFixture
        & git -C $fixture.Repo switch -q -c feature/windows-unique | Out-Null
        [IO.File]::WriteAllText((Join-Path $fixture.Repo 'unique.txt'), 'unique')
        & git -C $fixture.Repo add -- unique.txt | Out-Null
        & git -C $fixture.Repo commit -q -m 'a commit origin/dev does not have' | Out-Null
        & git -C $fixture.Repo switch -q dev | Out-Null

        $result = @(Remove-WinEnvMergedLocalBranch -RepositoryRoot $fixture.Repo)
        $result | Should -BeNullOrEmpty
        (Get-FixtureBranches -Repo $fixture.Repo) | Should -Contain 'feature/windows-unique'
    }

    It 'INV windows/capture-publishes-through-dev: never deletes the current branch, dev or master even when each is an ancestor of origin/dev' {
        $fixture = New-PruneFixture
        # Cut from dev's own tip, so this branch, dev and master are all,
        # trivially, ancestors of origin/dev; only the name-based exclusion
        # can be what keeps them.
        & git -C $fixture.Repo switch -q -c feature/windows-current | Out-Null

        $result = @(Remove-WinEnvMergedLocalBranch -RepositoryRoot $fixture.Repo)
        $result | Should -BeNullOrEmpty
        $branches = Get-FixtureBranches -Repo $fixture.Repo
        $branches | Should -Contain 'dev'
        $branches | Should -Contain 'master'
        $branches | Should -Contain 'feature/windows-current'
    }

    It 'reports a deletion failure on its own branch without stopping the rest of the run' {
        $fixture = New-PruneFixture
        & git -C $fixture.Repo branch -q feature/windows-merged-one | Out-Null
        & git -C $fixture.Repo branch -q feature/windows-merged-two | Out-Null

        # A branch checked out in another worktree is the ordinary way git
        # itself refuses `branch -D`, standing in for whatever else could make
        # one deletion fail without weakening the ancestor proof under test.
        $worktree = Join-Path $TestDrive ('prune-worktree-' + [guid]::NewGuid().ToString('N'))
        & git -C $fixture.Repo worktree add -q $worktree feature/windows-merged-two | Out-Null

        try {
            $result = @(Remove-WinEnvMergedLocalBranch -RepositoryRoot $fixture.Repo)
            ($result | Where-Object Branch -eq 'feature/windows-merged-one').Status | Should -Be 'Deleted'
            $failed = $result | Where-Object Branch -eq 'feature/windows-merged-two'
            $failed.Status | Should -Be 'Failed'
            $failed.Detail | Should -Not -BeNullOrEmpty
            (Get-FixtureBranches -Repo $fixture.Repo) | Should -Contain 'feature/windows-merged-two'
        }
        finally {
            & git -C $fixture.Repo worktree remove --force $worktree 2>$null | Out-Null
        }
    }

    It 'prunes nothing when origin/dev has never been fetched' {
        $fixture = New-PruneFixture
        & git -C $fixture.Repo branch -q feature/windows-old-capture | Out-Null
        & git -C $fixture.Repo update-ref -d refs/remotes/origin/dev | Out-Null

        $result = @(Remove-WinEnvMergedLocalBranch -RepositoryRoot $fixture.Repo)
        $result | Should -BeNullOrEmpty
        (Get-FixtureBranches -Repo $fixture.Repo) | Should -Contain 'feature/windows-old-capture'
    }

    It 'writes nothing under -WhatIf' {
        $fixture = New-PruneFixture
        & git -C $fixture.Repo branch -q feature/windows-old-capture | Out-Null
        $before = Get-FixtureBranches -Repo $fixture.Repo

        [void](Remove-WinEnvMergedLocalBranch -RepositoryRoot $fixture.Repo -WhatIf)
        (Get-FixtureBranches -Repo $fixture.Repo) | Should -Be $before
    }
}

Describe 'capture publish' {
    <#
        The publish half of capture (#80), a copy of what --publish added to
        tool/version-control/commit (#72) rather than a caller of it. Every
        fixture below runs against a throwaway working copy, a throwaway bare
        remote and a stub `gh` under $TestDrive -- never this repository, never
        this machine's real remote, and never a real `gh` call. Nothing here is
        Windows evidence: what is owed from the maintainer's host is one real
        -Publish run.
    #>
    BeforeAll {
        $PwshPath = (Get-Process -Id $PID).Path

        # The end-to-end cases in the last Context each launch a child
        # PowerShell that imports this module and spawns a dozen git
        # processes, and together they cost more than the rest of this suite.
        # `.githooks/pre-push` runs the whole suite natively on every push
        # that touches windows/**, so leaving them always-on taxes every
        # Windows-lane push -- including the one -Publish itself makes. They
        # are therefore opt-in, the way `.githooks/evidence` already makes the
        # local gate advisory and CI the merge gate: the windows job in
        # .github/workflows/ci.yml sets WIN_ENV_E2E, so the merge gate loses
        # nothing, and a local run says out loud what it skipped. Every
        # module-level fixture above runs unconditionally.
        $EndToEnd = [Environment]::GetEnvironmentVariable('WIN_ENV_E2E') -eq '1'

        function Skip-WithoutEndToEnd {
            param([Parameter(Mandatory)][string] $Label)

            if ($EndToEnd) { return }
            Write-Host ("· skipped: publish end to end, $Label " +
                '(set WIN_ENV_E2E=1 to run it; the CI windows job does)')
            Set-ItResult -Skipped -Because 'WIN_ENV_E2E is not set'
        }

        function New-StubGh {
            <#
                A gh that answers from environment variables and records every
                call, written as gh.ps1 because PowerShell resolves a bare
                command name against .ps1 as well as the platform's executable
                extensions -- on Windows and on the Unix-like hosts this suite
                also runs on. One implementation therefore serves both, where a
                .cmd and a shell script would be two that could disagree about
                the very refusals under test, and a shim that spawned a second
                PowerShell would cost more than every other fixture here
                together.
            #>
            param([Parameter(Mandatory)][string] $Directory)

            [void](New-Item -ItemType Directory -Path $Directory -Force)
            # Its own writes go through .NET rather than through Add-Content
            # and Copy-Item: a script run in process inherits the caller's
            # $WhatIfPreference, and a -WhatIf run of capture would otherwise
            # make the stub record nothing -- which reads as "gh was never
            # called" and is exactly the claim the -WhatIf fixture is checking.
            # A real gh.exe is a separate process and has no such inheritance.
            [IO.File]::WriteAllText((Join-Path $Directory 'gh.ps1'), @'
$call = @($args)
if ($env:STUB_GH_LOG) { [IO.File]::AppendAllText($env:STUB_GH_LOG, ($call -join ' ') + [Environment]::NewLine) }
function Get-StubStatus {
    param([string] $Name)
    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) { return 0 }
    return [int]$value
}
function Get-StubValue {
    param([string] $Name, [string] $Default)
    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) { return $Default }
    return $value
}
switch ((@($call | Select-Object -First 2) -join ' ')) {
    'auth status' { exit (Get-StubStatus 'STUB_GH_AUTH_STATUS') }
    'api repos/{owner}/{repo}' { Write-Output (Get-StubValue 'STUB_GH_ALLOW_AUTO_MERGE' 'true'); exit 0 }
    'pr list' { Write-Output (Get-StubValue 'STUB_GH_PR_LIST' '[]'); exit 0 }
    'pr create' {
        $index = [array]::IndexOf($call, '--body-file')
        if ($index -ge 0 -and $env:STUB_GH_BODY_COPY) {
            [IO.File]::Copy($call[$index + 1], $env:STUB_GH_BODY_COPY, $true)
        }
        $status = Get-StubStatus 'STUB_GH_CREATE_STATUS'
        if ($status -ne 0) { Write-Output 'stub: pr create refused'; exit $status }
        Write-Output (Get-StubValue 'STUB_GH_PR_URL' 'https://github.com/example/repo/pull/1')
        exit 0
    }
    'pr merge' { exit (Get-StubStatus 'STUB_GH_MERGE_STATUS') }
}
Write-Output 'stub: unknown gh invocation'
exit 1
'@)
            return $Directory
        }

        function New-PublishRepository {
            # dev, pushed to a bare remote and fetched back, plus master: the
            # shape every function under test reads. -Populate lays whatever
            # the run under test needs into the seed commit.
            param([scriptblock] $Populate)

            $token = [guid]::NewGuid().ToString('N')
            $base = Join-Path $TestDrive "publish-$token"
            $repo = Join-Path $base 'repo'
            $remote = Join-Path $base 'remote.git'
            [void](New-Item -ItemType Directory -Path $repo -Force)

            & git init -q --bare -b dev $remote | Out-Null
            & git -C $repo init -q -b dev | Out-Null
            & git -C $repo config user.name Fixture | Out-Null
            & git -C $repo config user.email fixture@example.invalid | Out-Null
            & git -C $repo remote add origin $remote | Out-Null
            if ($Populate) { & $Populate $repo } else { [IO.File]::WriteAllText((Join-Path $repo 'seed.txt'), 'seed') }
            & git -C $repo add -A | Out-Null
            & git -C $repo commit -q -m 'seed' | Out-Null
            & git -C $repo push -q --set-upstream origin dev | Out-Null
            & git -C $repo branch -q master | Out-Null

            return [pscustomobject]@{
                Base   = $base
                Repo   = $repo
                Remote = $remote
                Bin    = (New-StubGh -Directory (Join-Path $base 'bin'))
                Log    = (Join-Path $base 'gh.log')
                Body   = (Join-Path $base 'pull-request-body.md')
            }
        }

        function New-PublishWorkspace {
            <#
                A throwaway monorepo holding this repository's own capture
                script and module over a manifest no host has to match, plus
                the host files it captures from. The script is copied rather
                than run in place, because a run of it commits, branches and
                pushes: this suite must never point it at this repository.
            #>
            $features = @(
                @{ Id = 'core'; Name = 'Core'; Required = $true },
                @{ Id = 'extra'; Name = 'Extra' })
            $managed = @(
                @{ Id = 'sample'; Feature = 'core'; Source = 'files/sample.json'
                    Target = '{LOCALAPPDATA}/sample.json'; Compare = 'ExactJson'; Parser = 'Json'
                },
                @{ Id = 'other'; Feature = 'extra'; Source = 'files/other.json'
                    Target = '{LOCALAPPDATA}/other.json'; Compare = 'ExactJson'; Parser = 'Json'
                })
            $manifest = @{
                SchemaVersion  = 4
                ProjectVersion = '1.0.0'
                Features       = $features
                Packages       = @()
                ManagedFiles   = $managed
                Font           = @{ Feature = 'core'; Name = 'Test Font' }
                Terminal       = @{ Feature = 'core' }
            }

            $fixture = New-PublishRepository -Populate {
                param([string] $repo)
                foreach ($relative in @('windows/src', 'windows/tools', 'windows/desired/files')) {
                    [void](New-Item -ItemType Directory -Path (Join-Path $repo $relative) -Force)
                }
                Copy-Item -LiteralPath (Join-Path $repositoryRoot 'src\WinEnv.psm1') `
                    -Destination (Join-Path $repo 'windows/src/WinEnv.psm1')
                Copy-Item -LiteralPath (Join-Path $repositoryRoot 'tools\capture.ps1') `
                    -Destination (Join-Path $repo 'windows/tools/capture.ps1')
                [IO.File]::WriteAllText((Join-Path $repo 'windows/desired/manifest.json'),
                    ($manifest | ConvertTo-Json -Depth 10))
                [IO.File]::WriteAllText((Join-Path $repo 'windows/desired/files/sample.json'),
                    "{`n  `"theme`": `"light`"`n}`n")
                [IO.File]::WriteAllText((Join-Path $repo 'windows/desired/files/other.json'),
                    "{`n  `"size`": 10`n}`n")
            }

            # The host this capture reads. It drifted from both payloads.
            $hostDirectory = Join-Path $fixture.Base 'host'
            [void](New-Item -ItemType Directory -Path $hostDirectory -Force)
            [IO.File]::WriteAllText((Join-Path $hostDirectory 'sample.json'), '{"theme":"dark"}')
            [IO.File]::WriteAllText((Join-Path $hostDirectory 'other.json'), '{"size":14}')

            return $fixture | Add-Member -NotePropertyName HostDirectory -NotePropertyValue $hostDirectory -PassThru |
                Add-Member -NotePropertyName Capture `
                    -NotePropertyValue (Join-Path $fixture.Repo 'windows/tools/capture.ps1') -PassThru
        }

        function Invoke-Capture {
            <#
                One run of the copied script, answering its single prompt from
                stdin. It runs in a child process because the script exits, and
                because a run must inherit a PATH whose gh is the stub.
            #>
            param(
                [Parameter(Mandatory)][object] $Fixture,
                [Parameter(Mandatory)][string[]] $Argument,
                [string] $Answer = 'y',
                [hashtable] $Environment = @{}
            )

            $variables = $Environment.Clone()
            $variables['LOCALAPPDATA'] = $Fixture.HostDirectory
            $variables['APPDATA'] = $Fixture.HostDirectory
            $variables['USERPROFILE'] = $Fixture.Base

            # Every value the child run needs, copied into this scope first:
            # GetNewClosure captures the local scope and nothing above it.
            $shell = $PwshPath
            $script = $Fixture.Capture
            $reply = $Answer
            $callArgument = $Argument
            return Invoke-WithStubGh -Fixture $Fixture -Environment $variables -ScriptBlock {
                $output = $reply | & $shell -NoProfile -File $script @callArgument 2>&1
                [pscustomobject]@{
                    ExitCode = $LASTEXITCODE
                    Output   = @($output | ForEach-Object { [string]$_ })
                }
            }.GetNewClosure()
        }

        function Get-GhLog {
            param([Parameter(Mandatory)][object] $Fixture)
            if (-not (Test-Path -LiteralPath $Fixture.Log)) { return @() }
            return @(Get-Content -LiteralPath $Fixture.Log)
        }

        function Invoke-WithStubGh {
            # The stub is prepended to PATH rather than substituted for it,
            # because git is still needed; it wins because PATH resolves in
            # order.
            param(
                [Parameter(Mandatory)][object] $Fixture,
                [Parameter(Mandatory)][scriptblock] $ScriptBlock,
                [hashtable] $Environment = @{}
            )

            $variables = @{
                PATH              = ($Fixture.Bin + [IO.Path]::PathSeparator + $env:PATH)
                STUB_GH_LOG       = $Fixture.Log
                STUB_GH_BODY_COPY = $Fixture.Body
            }
            foreach ($key in $Environment.Keys) { $variables[$key] = $Environment[$key] }

            $saved = @{}
            foreach ($key in $variables.Keys) {
                $saved[$key] = [Environment]::GetEnvironmentVariable($key)
                [Environment]::SetEnvironmentVariable($key, $variables[$key])
            }
            try { & $ScriptBlock }
            finally {
                foreach ($key in $saved.Keys) { [Environment]::SetEnvironmentVariable($key, $saved[$key]) }
            }
        }
    }

    Context 'the pull request a run would open' {
        It 'titles a one-feature run with that commit''s own subject' {
            Get-WinEnvPullRequestTitle -Commit @('feat(windows): capture font settings from the host') |
                Should -Be 'feat(windows): capture font settings from the host'
        }

        It 'titles a multi-feature run generally, since no commit subject covers it' {
            Get-WinEnvPullRequestTitle -Commit @(
                'feat(windows): capture font settings from the host',
                'feat(windows): capture terminal settings from the host') |
                Should -Be 'feat(windows): capture settings from the host'
        }

        It 'carries the scope, the selection, the build, the files, the commits and the evidence' {
            $body = New-WinEnvPullRequestBody -Branch 'feature/windows-capture-font' `
                -Feature @('font') -ManagedFile @('fontPayload (windows/desired/files/font.json)') `
                -Commit @('feat(windows): capture font settings from the host') `
                -Command 'windows/tools/capture.ps1 -Feature font -Publish' -Build '22631' `
                -Evidence @(([char]27 + '[31m') + '→ hygiene' + ([char]27 + '[0m')) `
                -PushEvidence @('→ Windows tests', 'Tests Passed: 164, Failed: 0')

            $body | Should -Match 'Scope: windows'
            $body | Should -Match ([regex]::Escape('Branch: feature/windows-capture-font'))
            $body | Should -Match 'Feature selection: font'
            $body | Should -Match 'Windows build: 22631'
            $body | Should -Match ([regex]::Escape('Command: windows/tools/capture.ps1 -Feature font -Publish'))
            $body | Should -Match ([regex]::Escape('- fontPayload (windows/desired/files/font.json)'))
            $body | Should -Match ([regex]::Escape('- feat(windows): capture font settings from the host'))
            $body | Should -Match '→ hygiene'
            # The native gate's own output. It is produced by the pre-push
            # hook, which is the only hook that selects this domain's checks,
            # so a body without this block carries no Windows evidence at all.
            $body | Should -Match 'Local push evidence:'
            $body | Should -Match ([regex]::Escape('Tests Passed: 164, Failed: 0'))
            # A pull request renders the escape bytes rather than the colour.
            $body | Should -Not -Match ([char]27)
        }

        It 'says the build is undetermined rather than leaving the line blank' {
            $body = New-WinEnvPullRequestBody -Branch 'feature/windows-capture-font' -Feature @('font') `
                -ManagedFile @('fontPayload (windows/desired/files/font.json)') `
                -Commit @('feat(windows): capture font settings from the host') `
                -Command 'windows/tools/capture.ps1 -Publish' -Build ''
            $body | Should -Match 'Windows build: undetermined'
        }

        It 'promises both outputs where a plan has neither yet' {
            $body = New-WinEnvPullRequestBody -Branch 'feature/windows-capture-font' -Feature @('font') `
                -ManagedFile @('fontPayload (windows/desired/files/font.json)') `
                -Commit @('feat(windows): capture font settings from the host') `
                -Command 'windows/tools/capture.ps1 -Publish' -Build '22631'
            $body | Should -Match ([regex]::Escape('(the commit output, once the commit runs)'))
            $body | Should -Match ([regex]::Escape("(the pre-push hook's output, once the push runs)"))
        }

        It 'names what the branch already carried, which the same merge takes to dev' {
            $body = New-WinEnvPullRequestBody -Branch 'feature/windows-capture-font' -Feature @('font') `
                -ManagedFile @('fontPayload (windows/desired/files/font.json)') `
                -Commit @('feat(windows): capture font settings from the host') `
                -Command 'windows/tools/capture.ps1 -Publish' -Build '22631' `
                -Carried @('1234abc an earlier commit on this branch')
            $body | Should -Match ([regex]::Escape('- 1234abc an earlier commit on this branch'))
        }
    }

    Context 'evidence a published capture writes, readable' {
        <#
            #85: PR #84's body (the first real -Publish) reached GitHub with
            the hook's UTF-8 glyphs mislabelled as mojibake and a stray
            control character in the transcript, and its push-evidence block
            was this suite's own multi-minute Pester transcript, including
            lines a rejected-push fixture prints on purpose ("- the Windows
            checks failed", a throwaway `Temp\...\remote.git`). These fixtures
            cover the fix: correct decoding regardless of the console's own
            codepage, control characters stripped from the body only, and the
            push block condensed to what a reviewer needs.
        #>
        It 'recovers a hook''s UTF-8 glyphs a non-UTF-8 console codepage would mislabel' {
            # The exact failure mode: PowerShell's own `2>&1 | ForEach-Object`
            # decodes a captured native command's output with
            # [Console]::OutputEncoding, not the encoding the command wrote
            # in. Reproduced by hand while designing this fix: under codepage
            # 437, this same "-> <check> <dot>" line survives as "ΓåÆ Γ£ô
            # ┬╖" through that pipe. Invoke-WinEnvTeeCommand must not care --
            # it declares its own pipe's encoding as UTF-8 instead of trusting
            # the console's.
            $stubPath = Join-Path $TestDrive 'utf8-glyphs.ps1'
            [IO.File]::WriteAllText($stubPath, @'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Output '→ ✓ ·'
[Console]::Error.WriteLine('→-err')
exit 7
'@)

            $saved = [Console]::OutputEncoding
            try {
                [Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding(437)
                $result = Invoke-WinEnvTeeCommand -FilePath $PwshPath -ArgumentList @('-NoProfile', '-File', $stubPath)
            }
            finally {
                [Console]::OutputEncoding = $saved
            }

            $result.ExitCode | Should -Be 7
            $result.Evidence | Should -Contain '→ ✓ ·'
            $result.Evidence | Should -Contain '→-err'
        }

        It 'recovers the same glyphs when the console is already UTF-8, the common case' {
            # "Already UTF-8" is a condition this test establishes, never one
            # it inherits from whoever ran it. #109: on the maintainer's
            # Korean host the suite's own console was CP949, the child pwsh
            # inherited that codepage, and the line was already encoded as
            # CP949 before it reached the pipe -- so this test was red there
            # and green on CI while asserting nothing about
            # Invoke-WinEnvTeeCommand. Both sides are pinned here: the
            # console this process owns, which a Windows child inherits, and
            # the child's own output encoding, because a Unix child inherits
            # no console codepage at all.
            $stubPath = Join-Path $TestDrive 'utf8-glyphs-default.ps1'
            [IO.File]::WriteAllText($stubPath, @'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Output '→ ✓ ·'
exit 0
'@)

            $saved = [Console]::OutputEncoding
            try {
                [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
                $result = Invoke-WinEnvTeeCommand -FilePath $PwshPath -ArgumentList @('-NoProfile', '-File', $stubPath)
            }
            finally {
                [Console]::OutputEncoding = $saved
            }

            $result.ExitCode | Should -Be 0
            $result.Evidence | Should -Contain '→ ✓ ·'
        }

        It 'reports what a CP949 console loses instead of inventing glyphs' {
            # The regression #109 asked for, and the decision it asked for,
            # recorded where it is exercised. Reproduced by hand on Linux
            # pwsh with the same managed CP949 encoder .NET uses on Windows:
            # the loss happens in the *child's* write, not in this
            # repository's decode. A child encodes its own stdout with its
            # own [Console]::OutputEncoding, so "→" and "·" (both mappable
            # in CP949) leave as CP949 byte pairs and "✓" (not mappable at
            # all) leaves as a literal "?". The glyphs are gone from the pipe
            # before Invoke-WinEnvTeeCommand reads a byte.
            #
            # Decision: this is accepted display degradation, not a defect in
            # that function's pinning.
            #  - It owns only the read side and already pins it to UTF-8. No
            #    read-side decoding recovers a glyph the writer never emitted,
            #    and Windows offers no way to set a child's console codepage
            #    from ProcessStartInfo; a child that wants its glyphs kept
            #    declares its own encoding, as the CP437 fixture above does.
            #  - Nothing that carries meaning is lost from real evidence. git,
            #    the command actually teed for a push, writes its bytes
            #    directly, and every marker ConvertTo-WinEnvCondensedPushEvidence
            #    keys on ("→ <check>", "· ...") is printed by .githooks/evidence
            #    through /bin/sh printf, which emits that file's own UTF-8
            #    bytes whatever the console codepage is.
            #  - ASCII survives byte for byte, asserted below: the tally, the
            #    "[-]" markers and the failure detail a reviewer actually
            #    reads are untouched.
            # The contract is therefore that a line from a non-UTF-8 console
            # arrives degraded but framed, ordered and ASCII-intact -- never
            # silently replaced by plausible-but-wrong text.
            $stubPath = Join-Path $TestDrive 'cp949-glyphs.ps1'
            [IO.File]::WriteAllText($stubPath, @'
[System.Text.Encoding]::RegisterProvider([System.Text.CodePagesEncodingProvider]::Instance)
[Console]::OutputEncoding = [System.Text.Encoding]::GetEncoding(949)
Write-Output '→ ✓ · Tests Passed: 1, Failed: 0'
exit 0
'@)

            $saved = [Console]::OutputEncoding
            try {
                $result = Invoke-WinEnvTeeCommand -FilePath $PwshPath -ArgumentList @('-NoProfile', '-File', $stubPath)
            }
            finally {
                # A console is shared by every process attached to it, so the
                # child's own switch to CP949 outlives the child on Windows.
                # Re-assigning the saved encoding puts the operator's console
                # back where it was.
                [Console]::OutputEncoding = $saved
            }

            $result.ExitCode | Should -Be 0
            @($result.Evidence).Count | Should -Be 1
            $line = @($result.Evidence)[0]
            $line | Should -BeLike '*Tests Passed: 1, Failed: 0'
            $line | Should -Not -Match ([regex]::Escape('→'))
            $line | Should -Not -Match ([regex]::Escape('✓'))
            $line | Should -Not -Match ([regex]::Escape('·'))
            # Whatever replaced them is visibly lossy: U+FFFD where the bytes
            # were not UTF-8, "?" where CP949 had no mapping to begin with.
            @($line.ToCharArray() | Where-Object { [int]$_ -ge 0x80 -and [int]$_ -ne 0xFFFD }) |
                Should -BeNullOrEmpty
        }

        It 'strips a stray control character from the body but keeps a tab' {
            $body = New-WinEnvPullRequestBody -Branch 'feature/windows-capture-font' -Feature @('font') `
                -ManagedFile @('fontPayload (windows/desired/files/font.json)') `
                -Commit @('feat(windows): capture font settings from the host') `
                -Command 'windows/tools/capture.ps1 -Publish' -Build '22631' `
                -Evidence @("a line with a stray$([char]0x1A) control byte") `
                -PushEvidence @("· a$([char]9)tabbed dot line", "Tests Passed: 1, Failed: 0")

            $body | Should -Not -Match ([char]0x1A)
            $body | Should -Match ([regex]::Escape('a line with a stray control byte'))
            $body | Should -Match ([regex]::Escape("a$([char]9)tabbed dot line"))
        }

        It 'condenses a passing Pester transcript, keeping the summary and naming the count' {
            $line = @(
                '→ selected checks',
                'windows:desired-state',
                'windows:tests',
                '→ Windows desired-state check',
                'Windows desired state is valid.',
                '→ Windows tests',
                '',
                'Starting discovery in 1 files.',
                'Discovery found 165 tests in 620ms.',
                'Running tests.',
                '→ pushing feature/windows-capture-font',
                'To C:\Users\…\Temp\publish-abc123\remote.git',
                "branch 'feature/windows-capture-font' set up to track 'origin/feature/windows-capture-font'.",
                '- the Windows checks failed',
                "error: failed to push some refs to 'C:\Users\…\Temp\publish-abc123\remote.git'",
                '· skipped: publish end to end, the happy path (set WIN_ENV_E2E=1 to run it; the CI windows job does)',
                'Tests Passed: 154, Failed: 0, Skipped: 10, Inconclusive: 0, NotRun: 0'
            )

            $condensed = ConvertTo-WinEnvCondensedPushEvidence -Line $line

            $condensed | Should -Contain '→ selected checks'
            $condensed | Should -Contain '→ Windows desired-state check'
            $condensed | Should -Contain 'Windows desired state is valid.'
            $condensed | Should -Contain '→ Windows tests'
            $condensed | Should -Contain ('· skipped: publish end to end, the happy path ' +
                '(set WIN_ENV_E2E=1 to run it; the CI windows job does)')
            $condensed | Should -Contain 'Tests Passed: 154, Failed: 0, Skipped: 10, Inconclusive: 0, NotRun: 0'
            # The fixture's own push narration is inside the Windows tests
            # span and matches none of the kept shapes, so it is elided along
            # with Pester's own scaffolding -- this is the residual the note
            # above the block exists for, not a promise this function makes.
            $condensed | Should -Not -Contain '→ pushing feature/windows-capture-font'
            $condensed | Should -Not -Contain 'Starting discovery in 1 files.'
            # One elision marker naming a count, not one marker per line.
            @($condensed | Where-Object { $_ -match '^… \d+ passing .* elided …$' }).Count | Should -Be 1
        }

        It 'keeps every line of a failed test, condensing only what passed around it' {
            $esc = [char]27
            $line = @(
                '→ Windows tests',
                'Discovery found 1 tests in 10ms.',
                "$esc[91m[-] a test that failed$esc[0m$esc[90m 5ms (4ms|1ms)$esc[0m",
                "$esc[91m Expected 1, but got 2.",
                "$esc[91m at Should -Be 2, WinEnv.Tests.ps1:1$esc[0m",
                '',
                'Tests Passed: 0, Failed: 1, Skipped: 0, Inconclusive: 0, NotRun: 0'
            )

            $condensed = ConvertTo-WinEnvCondensedPushEvidence -Line $line

            $condensed | Should -Contain "$esc[91m[-] a test that failed$esc[0m$esc[90m 5ms (4ms|1ms)$esc[0m"
            $condensed | Should -Contain "$esc[91m Expected 1, but got 2."
            $condensed | Should -Contain "$esc[91m at Should -Be 2, WinEnv.Tests.ps1:1$esc[0m"
            $condensed | Should -Contain 'Tests Passed: 0, Failed: 1, Skipped: 0, Inconclusive: 0, NotRun: 0'
            $condensed | Should -Not -Contain 'Discovery found 1 tests in 10ms.'
        }

        It 'leaves everything outside the Windows tests span untouched' {
            # No "→ Windows tests" header at all: nothing here is a Pester
            # transcript, so nothing is elided, regardless of shape.
            $line = @('→ common check', 'a line that is neither a header nor a dot', 'common check passed')

            ConvertTo-WinEnvCondensedPushEvidence -Line $line | Should -Be $line
        }

        It 'condenses the push-evidence block inside the pull-request body and keeps the note above it' {
            $line = @(
                '→ Windows tests',
                'Discovery found 200 tests in 600ms.',
                '→ pushing feature/windows-capture-font',
                'To C:\Users\…\Temp\publish-abc123\remote.git',
                'Tests Passed: 199, Failed: 0, Skipped: 1, Inconclusive: 0, NotRun: 0'
            )

            $body = New-WinEnvPullRequestBody -Branch 'feature/windows-capture-font' -Feature @('font') `
                -ManagedFile @('fontPayload (windows/desired/files/font.json)') `
                -Commit @('feat(windows): capture font settings from the host') `
                -Command 'windows/tools/capture.ps1 -Publish' -Build '22631' -PushEvidence $line

            $body | Should -Match ([regex]::Escape('Fixture output inside this suite may mention throwaway ' +
                    '`Temp\…\remote.git` remotes'))
            $body | Should -Match ([regex]::Escape('Tests Passed: 199, Failed: 0, Skipped: 1'))
            $body | Should -Not -Match ([regex]::Escape('Discovery found 200 tests in 600ms.'))
            $body | Should -Match '… \d+ passing .* elided …'
        }
    }

    Context 'what the branch already carries' {
        It 'is empty on a branch that is origin/dev' {
            $fixture = New-PublishRepository
            @(Get-WinEnvPublishCarriedCommit -RepositoryRoot $fixture.Repo).Count | Should -Be 0
        }

        It 'lists every commit a push would take to dev with the capture' {
            $fixture = New-PublishRepository
            & git -C $fixture.Repo switch -q -c feature/windows-existing | Out-Null
            [IO.File]::WriteAllText((Join-Path $fixture.Repo 'seed.txt'), 'an unrelated local change')
            & git -C $fixture.Repo commit -q -a -m 'an unrelated commit already on this branch' | Out-Null

            $carried = @(Get-WinEnvPublishCarriedCommit -RepositoryRoot $fixture.Repo)
            $carried.Count | Should -Be 1
            $carried[0] | Should -Match 'an unrelated commit already on this branch'
        }
    }

    Context 'the preflight, which reads and never writes' {
        It 'refuses when gh is unavailable, before it asks git anything' {
            $fixture = New-PublishRepository
            $empty = Join-Path $fixture.Base 'no-tools'
            [void](New-Item -ItemType Directory -Path $empty -Force)

            $result = Invoke-WithStubGh -Fixture $fixture -Environment @{ PATH = $empty } -ScriptBlock {
                Get-WinEnvPublishPreflight -RepositoryRoot $fixture.Repo `
                    -Branch 'feature/windows-capture-font' -BranchIsNew
            }
            $result.Status | Should -Be 'Refused'
            $result.Message | Should -Match 'gh is unavailable'
            # The message has to name the way this platform installs it.
            $result.Detail | Should -Match ([regex]::Escape('winget install GitHub.cli'))
            (Get-GhLog $fixture).Count | Should -Be 0
        }

        It 'refuses an unauthenticated gh before reading any repository setting' {
            $fixture = New-PublishRepository
            $result = Invoke-WithStubGh -Fixture $fixture -Environment @{ STUB_GH_AUTH_STATUS = '1' } -ScriptBlock {
                Get-WinEnvPublishPreflight -RepositoryRoot $fixture.Repo `
                    -Branch 'feature/windows-capture-font' -BranchIsNew
            }
            $result.Status | Should -Be 'Refused'
            $result.Message | Should -Match 'not authenticated'
            @(Get-GhLog $fixture) | Should -Be @('auth status --hostname github.com')
        }

        It 'refuses when the repository does not allow auto-merge, before any pull request is listed' {
            $fixture = New-PublishRepository
            $result = Invoke-WithStubGh -Fixture $fixture -Environment @{ STUB_GH_ALLOW_AUTO_MERGE = 'false' } -ScriptBlock {
                Get-WinEnvPublishPreflight -RepositoryRoot $fixture.Repo `
                    -Branch 'feature/windows-capture-font' -BranchIsNew
            }
            $result.Status | Should -Be 'Refused'
            $result.Message | Should -Match 'does not allow auto-merge'
            # The field gh repo view has no column for; read through the API.
            @(Get-GhLog $fixture)[1] | Should -Be 'api repos/{owner}/{repo} --jq .allow_auto_merge'
            @(Get-GhLog $fixture).Count | Should -Be 2
        }

        It 'INV windows/capture-publishes-through-dev: refuses an open pull request from this head against a base other than dev' {
            $fixture = New-PublishRepository
            $listing = '[{"baseRefName":"master","isCrossRepository":false,' +
            '"url":"https://github.com/example/repo/pull/9"}]'
            $result = Invoke-WithStubGh -Fixture $fixture -Environment @{ STUB_GH_PR_LIST = $listing } -ScriptBlock {
                Get-WinEnvPublishPreflight -RepositoryRoot $fixture.Repo `
                    -Branch 'feature/windows-capture-font' -BranchIsNew
            }
            $result.Status | Should -Be 'Refused'
            $result.Message | Should -Match 'different base'
            $result.Detail | Should -Match ([regex]::Escape('https://github.com/example/repo/pull/9'))
        }

        It 'INV windows/capture-publishes-through-dev: reuses an open pull request from this head against dev instead of opening a second' {
            $fixture = New-PublishRepository
            $listing = '[{"baseRefName":"dev","isCrossRepository":false,' +
            '"url":"https://github.com/example/repo/pull/7"}]'
            $result = Invoke-WithStubGh -Fixture $fixture -Environment @{ STUB_GH_PR_LIST = $listing } -ScriptBlock {
                Get-WinEnvPublishPreflight -RepositoryRoot $fixture.Repo `
                    -Branch 'feature/windows-capture-font' -BranchIsNew
            }
            $result.Status | Should -Be 'Ready'
            $result.PullRequest | Should -Be 'https://github.com/example/repo/pull/7'
        }

        It 'ignores a fork''s branch of the same name, which gh pr list --head cannot exclude' {
            # gh filters --head by branch name alone and does not accept
            # "<owner>:<branch>", so a cross-repository row arrives here. It is
            # neither this branch nor this tool's to reuse or refuse over.
            $fixture = New-PublishRepository
            $listing = '[{"baseRefName":"master","isCrossRepository":true,' +
            '"url":"https://github.com/fork/repo/pull/9"},' +
            '{"baseRefName":"dev","isCrossRepository":true,' +
            '"url":"https://github.com/fork/repo/pull/10"}]'
            $result = Invoke-WithStubGh -Fixture $fixture -Environment @{ STUB_GH_PR_LIST = $listing } -ScriptBlock {
                Get-WinEnvPublishPreflight -RepositoryRoot $fixture.Repo `
                    -Branch 'feature/windows-capture-font' -BranchIsNew
            }
            $result.Status | Should -Be 'Ready'
            $result.PullRequest | Should -BeNullOrEmpty
        }

        It 'refuses to create a branch the remote already has' {
            $fixture = New-PublishRepository
            & git -C $fixture.Repo push -q origin dev:feature/windows-capture-font | Out-Null

            $result = Invoke-WithStubGh -Fixture $fixture -ScriptBlock {
                Get-WinEnvPublishPreflight -RepositoryRoot $fixture.Repo `
                    -Branch 'feature/windows-capture-font' -BranchIsNew
            }
            $result.Status | Should -Be 'Refused'
            $result.Message | Should -Match ([regex]::Escape('origin already has feature/windows-capture-font'))
        }

        It 'does not ask about a remote branch when the commit stays on the current one' {
            # -BranchIsNew is absent, so the branch is already this one and the
            # remote having it is exactly the normal case.
            $fixture = New-PublishRepository
            & git -C $fixture.Repo push -q origin dev:feature/windows-existing | Out-Null

            $result = Invoke-WithStubGh -Fixture $fixture -ScriptBlock {
                Get-WinEnvPublishPreflight -RepositoryRoot $fixture.Repo -Branch 'feature/windows-existing'
            }
            $result.Status | Should -Be 'Ready'
        }
    }

    Context 'the writing half' {
        BeforeAll {
            # The half of the body that is known before the push. The other
            # half -- what the pre-push hook said -- only exists afterwards,
            # which is why the body is built inside Publish-WinEnvCapture.
            $BodyParameter = @{
                Branch      = 'feature/windows-capture-font'
                Feature     = @('font')
                ManagedFile = @('fontPayload (windows/desired/files/font.json)')
                Commit      = @('feat(windows): capture font settings from the host')
                Command     = 'windows/tools/capture.ps1 -Feature font -Publish'
                Build       = '22631'
            }
        }

        It 'INV windows/capture-publishes-through-dev: pushes, opens one pull request and arms auto-merge exactly once' {
            $fixture = New-PublishRepository
            & git -C $fixture.Repo switch -q -c feature/windows-capture-font | Out-Null

            $result = Invoke-WithStubGh -Fixture $fixture -ScriptBlock {
                Publish-WinEnvCapture -RepositoryRoot $fixture.Repo -Branch 'feature/windows-capture-font' `
                    -Title 'feat(windows): capture font settings from the host' `
                    -BodyParameter $BodyParameter -PullRequest $null
            }
            $result.Status | Should -Be 'Published'
            $result.Url | Should -Be 'https://github.com/example/repo/pull/1'

            $log = @(Get-GhLog $fixture)
            @($log | Where-Object { $_ -like 'pr create *' }).Count | Should -Be 1
            @($log | Where-Object { $_ -like 'pr merge *' }).Count | Should -Be 1
            $log[-1] | Should -Be 'pr merge --auto --merge https://github.com/example/repo/pull/1'
            # --merge, never --admin: the wait for Required checks is the gate.
            @($log | Where-Object { $_ -match '--admin' }).Count | Should -Be 0
            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) |
                Should -Contain 'refs/heads/feature/windows-capture-font'

            $body = Get-Content -LiteralPath $fixture.Body -Raw
            $body | Should -Match ([regex]::Escape('- feat(windows): capture font settings from the host'))
            # git's own push report stands in for the hook's here, since this
            # fixture's remote runs no checks: what matters is that whatever
            # the push printed reached the body rather than the floor.
            $body | Should -Match 'Local push evidence:'
            $body | Should -Match ([regex]::Escape('feature/windows-capture-font'))
            $body | Should -Not -Match ([regex]::Escape("(the pre-push hook's output, once the push runs)"))
        }

        It 'INV windows/capture-publishes-through-dev: arms the pull request already open against dev and opens no second one' {
            $fixture = New-PublishRepository
            & git -C $fixture.Repo switch -q -c feature/windows-capture-font | Out-Null

            $result = Invoke-WithStubGh -Fixture $fixture -ScriptBlock {
                Publish-WinEnvCapture -RepositoryRoot $fixture.Repo -Branch 'feature/windows-capture-font' `
                    -Title 'feat(windows): capture font settings from the host' `
                    -BodyParameter $BodyParameter -PullRequest 'https://github.com/example/repo/pull/7'
            }
            $result.Status | Should -Be 'Published'
            $result.Url | Should -Be 'https://github.com/example/repo/pull/7'

            $log = @(Get-GhLog $fixture)
            @($log | Where-Object { $_ -like 'pr create *' }).Count | Should -Be 0
            @($log) | Should -Be @('pr merge --auto --merge https://github.com/example/repo/pull/7')
            (Test-Path -LiteralPath $fixture.Body) | Should -Be $false
        }

        It 'INV windows/capture-publishes-through-dev: stops at a rejected push with the commits local and nothing published' {
            $fixture = New-PublishRepository
            & git -C $fixture.Repo switch -q -c feature/windows-capture-font | Out-Null
            [IO.File]::WriteAllText((Join-Path $fixture.Repo 'seed.txt'), 'a captured payload')
            & git -C $fixture.Repo commit -q -a -m 'feat(windows): capture font settings from the host' | Out-Null
            $hooks = Join-Path $fixture.Repo '.githooks'
            [void](New-Item -ItemType Directory -Path $hooks -Force)
            $hook = Join-Path $hooks 'pre-push'
            # On its error stream: git discards a pre-push hook's stdout when
            # the push is not to a terminal, and the point of this fixture is
            # that the operator reads what the hook said.
            [IO.File]::WriteAllText($hook, "#!/bin/sh`necho '- the Windows checks failed' >&2`nexit 1`n")
            if (-not $IsWindows) { & chmod +x $hook }
            & git -C $fixture.Repo config core.hooksPath .githooks | Out-Null

            $result = Invoke-WithStubGh -Fixture $fixture -ScriptBlock {
                Publish-WinEnvCapture -RepositoryRoot $fixture.Repo -Branch 'feature/windows-capture-font' `
                    -Title 'feat(windows): capture font settings from the host' `
                    -BodyParameter $BodyParameter -PullRequest $null
            }
            $result.Status | Should -Be 'Refused'
            $result.Message | Should -Match 'push was rejected'
            $result.Detail | Should -Match ([regex]::Escape('feature/windows-capture-font'))
            $result.Detail | Should -Match 'nothing here retries with a bypass'
            (Get-GhLog $fixture).Count | Should -Be 0
            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) |
                Should -Not -Contain 'refs/heads/feature/windows-capture-font'
            # The commit is still here to push again once the hook passes.
            (& git -C $fixture.Repo log --oneline -1).Trim() | Should -Match 'capture font settings'
        }

        It 'reports an unarmed auto-merge with the pull request it left open' {
            $fixture = New-PublishRepository
            & git -C $fixture.Repo switch -q -c feature/windows-capture-font | Out-Null

            $result = Invoke-WithStubGh -Fixture $fixture -Environment @{ STUB_GH_MERGE_STATUS = '1' } -ScriptBlock {
                Publish-WinEnvCapture -RepositoryRoot $fixture.Repo -Branch 'feature/windows-capture-font' `
                    -Title 'feat(windows): capture font settings from the host' `
                    -BodyParameter $BodyParameter -PullRequest $null
            }
            $result.Status | Should -Be 'Refused'
            $result.Message | Should -Match 'Auto-merge could not be armed'
            $result.Detail | Should -Match ([regex]::Escape('https://github.com/example/repo/pull/1'))
        }

        It 'reports a pull request that could not be opened, with the branch already pushed' {
            $fixture = New-PublishRepository
            & git -C $fixture.Repo switch -q -c feature/windows-capture-font | Out-Null

            $result = Invoke-WithStubGh -Fixture $fixture -Environment @{ STUB_GH_CREATE_STATUS = '1' } -ScriptBlock {
                Publish-WinEnvCapture -RepositoryRoot $fixture.Repo -Branch 'feature/windows-capture-font' `
                    -Title 'feat(windows): capture font settings from the host' `
                    -BodyParameter $BodyParameter -PullRequest $null
            }
            $result.Status | Should -Be 'Refused'
            $result.Message | Should -Match 'could not be opened'
            @(Get-GhLog $fixture | Where-Object { $_ -like 'pr merge *' }).Count | Should -Be 0
        }

        It 'writes nothing under -WhatIf' {
            $fixture = New-PublishRepository
            & git -C $fixture.Repo switch -q -c feature/windows-capture-font | Out-Null
            $before = @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads)

            $result = Invoke-WithStubGh -Fixture $fixture -ScriptBlock {
                Publish-WinEnvCapture -RepositoryRoot $fixture.Repo -Branch 'feature/windows-capture-font' `
                    -Title 'feat(windows): capture font settings from the host' `
                    -BodyParameter $BodyParameter -PullRequest $null -WhatIf
            }
            $result.Status | Should -Be 'Skipped'
            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) | Should -Be $before
            (Get-GhLog $fixture).Count | Should -Be 0
        }
    }

    Context 'the whole run, from a drifted host file to a pull request' {
        It 'branches, commits, pushes, opens one pull request and arms auto-merge after one y' {
            Skip-WithoutEndToEnd 'the happy path'

            $fixture = New-PublishWorkspace
            $run = Invoke-Capture -Fixture $fixture -Argument @('-Feature', 'core', '-Publish') -Answer 'y'

            $run.ExitCode | Should -Be 0
            # What the confirmation asked is asserted against the script's
            # source below ('asks the documented question…'), not against this
            # transcript. Windows PowerShell's console host writes a
            # Read-Host prompt to the console device rather than to stdout, so
            # a child process whose output is captured never carries it, while
            # Unix-like pwsh happens to put it in the pipe. That difference is
            # the console's, not the tool's; what this fixture is for is the
            # behaviour the answer produced, which is everything below.
            #
            # The last line is the pull-request URL and nothing after it: this
            # run never waits on CI and never merges.
            $run.Output[-1] | Should -Be 'https://github.com/example/repo/pull/1'
            # The run really did stop for the question and act on the answer:
            # the plan was printed, and the payload was written only after it.
            $run.Output | Should -Contain '  publish: one pull request against dev, auto-merge armed'

            $log = @(Get-GhLog $fixture)
            @($log | Where-Object { $_ -like 'pr create *' }).Count | Should -Be 1
            @($log | Where-Object { $_ -like 'pr merge *' }).Count | Should -Be 1
            $log[-1] | Should -Be 'pr merge --auto --merge https://github.com/example/repo/pull/1'
            @($log | Where-Object { $_ -like 'pr create *' })[0] |
                Should -Match ([regex]::Escape('pr create --base dev --head feature/windows-capture-core'))

            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) |
                Should -Contain 'refs/heads/feature/windows-capture-core'
            (& git -C $fixture.Repo branch --show-current).Trim() | Should -Be 'feature/windows-capture-core'
            # dev never carried the commit.
            (& git -C $fixture.Repo rev-parse dev).Trim() |
                Should -Be (& git -C $fixture.Repo rev-parse refs/remotes/origin/dev).Trim()

            $body = Get-Content -LiteralPath $fixture.Body -Raw
            $body | Should -Match 'Scope: windows'
            $body | Should -Match 'Feature selection: core'
            $body | Should -Match 'Windows build:'
            $body | Should -Match ([regex]::Escape('- sample (windows/desired/files/sample.json)'))
            $body | Should -Match ([regex]::Escape('- feat(windows): capture core settings from the host'))
            $body | Should -Match ([regex]::Escape('Command: windows/tools/capture.ps1 -Feature core -Publish'))
            # The commit's own output, copied rather than intercepted.
            $body | Should -Match '1 file changed'
            # And the push's, which on a Windows host is where the domain's
            # own checks run. This fixture's remote runs none, so what lands
            # here is git's push report -- the point is that it lands.
            $body | Should -Match 'Local push evidence:'
            $body | Should -Match ([regex]::Escape('feature/windows-capture-core -> feature/windows-capture-core'))
            $body | Should -Not -Match ([regex]::Escape("(the pre-push hook's output, once the push runs)"))
            # Ordering: what the push said reaches the terminal too, between
            # the push line and the pull request being opened. Anchored on the
            # ASCII part of each line, because how a captured child's `→`
            # survives depends on the console encoding of the host running the
            # suite, and this fixture is about order rather than about bytes.
            $text = $run.Output -join [Environment]::NewLine
            $pushIndex = $text.IndexOf('pushing feature/windows-capture-core')
            $reportIndex = $text.IndexOf('feature/windows-capture-core -> feature/windows-capture-core')
            $openIndex = $text.IndexOf('opening a pull request against dev')
            $pushIndex | Should -BeGreaterThan -1
            $reportIndex | Should -BeGreaterThan -1
            $openIndex | Should -BeGreaterThan -1
            $pushIndex | Should -BeLessThan $reportIndex
            $reportIndex | Should -BeLessThan $openIndex
        }

        It 'publishes nothing and writes nothing when the answer is not y' {
            Skip-WithoutEndToEnd 'an answer that is not y'

            $fixture = New-PublishWorkspace
            $run = Invoke-Capture -Fixture $fixture -Argument @('-Feature', 'core', '-Publish') -Answer 'n'

            $run.ExitCode | Should -Be 1
            $run.Output | Should -Contain 'Aborted. Nothing was written.'
            @(Get-GhLog $fixture | Where-Object { $_ -like 'pr create *' -or $_ -like 'pr merge *' }).Count |
                Should -Be 0
            @(& git -C $fixture.Repo for-each-ref --format='%(refname)' refs/heads) |
                Should -Not -Contain 'refs/heads/feature/windows-capture-core'
            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) |
                Should -Be @('refs/heads/dev')
            @(& git -C $fixture.Repo status --porcelain).Count | Should -Be 0
        }

        It 'prints the branch, the title, the body and the commands under -WhatIf and writes nothing' {
            Skip-WithoutEndToEnd 'the -WhatIf plan'

            $fixture = New-PublishWorkspace
            $before = @(& git -C $fixture.Repo for-each-ref --format='%(refname)' refs/heads)
            $run = Invoke-Capture -Fixture $fixture -Argument @('-Feature', 'core', '-Publish', '-WhatIf')

            $run.ExitCode | Should -Be 0
            $text = $run.Output -join [Environment]::NewLine
            $text | Should -Match ([regex]::Escape('branch: feature/windows-capture-core (new, from origin/dev)'))
            $text | Should -Match ([regex]::Escape('pull request title: feat(windows): capture core settings from the host'))
            $text | Should -Match 'pull request body:'
            $text | Should -Match ([regex]::Escape('git push --set-upstream origin feature/windows-capture-core'))
            $text | Should -Match ([regex]::Escape('gh pr create --base dev --head feature/windows-capture-core'))
            $text | Should -Match ([regex]::Escape('gh pr merge --auto --merge <the pull request that opens>'))
            $text | Should -Match ([regex]::Escape('What if: nothing was written and no commit was made.'))

            # Read-only gh calls are allowed here and writing ones are not.
            @(Get-GhLog $fixture) | Should -Be @(
                'auth status --hostname github.com',
                'api repos/{owner}/{repo} --jq .allow_auto_merge',
                'pr list --head feature/windows-capture-core --state open --json baseRefName,isCrossRepository,url')
            @(& git -C $fixture.Repo for-each-ref --format='%(refname)' refs/heads) | Should -Be $before
            @(& git -C $fixture.Repo status --porcelain).Count | Should -Be 0
            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) | Should -Be @('refs/heads/dev')
        }

        It 'leaves the commit local and names the branch when the pre-push hook rejects the push' {
            Skip-WithoutEndToEnd 'a rejected pre-push hook'

            $fixture = New-PublishWorkspace
            # Installed after the seed push, so it gates only the run under test.
            $hook = Join-Path $fixture.Repo '.githooks/pre-push'
            [void](New-Item -ItemType Directory -Path (Split-Path -Parent $hook) -Force)
            [IO.File]::WriteAllText($hook, "#!/bin/sh`necho '- the Windows checks failed' >&2`nexit 1`n")
            if (-not $IsWindows) { & chmod +x $hook }
            & git -C $fixture.Repo config core.hooksPath .githooks | Out-Null

            $run = Invoke-Capture -Fixture $fixture -Argument @('-Feature', 'core', '-Publish') -Answer 'y'

            $run.ExitCode | Should -Be 1
            $text = $run.Output -join [Environment]::NewLine
            $text | Should -Match 'The push was rejected'
            $text | Should -Match ([regex]::Escape('feature/windows-capture-core'))
            $text | Should -Match 'nothing here retries with a bypass'
            # The hook's own output reached the operator.
            $text | Should -Match 'the Windows checks failed'

            @(Get-GhLog $fixture | Where-Object { $_ -like 'pr create *' -or $_ -like 'pr merge *' }).Count |
                Should -Be 0
            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) | Should -Be @('refs/heads/dev')
            (& git -C $fixture.Repo branch --show-current).Trim() | Should -Be 'feature/windows-capture-core'
            (& git -C $fixture.Repo log --oneline -1).Trim() | Should -Match 'capture core settings from the host'
        }

        It 'never reaches the push when the commit itself is rejected' {
            Skip-WithoutEndToEnd 'a rejected commit'

            # The most consequential ordering in the whole run: the commit is
            # piped so a copy of its output can reach the pull request, and a
            # pipeline that lost the commit's exit status would push a change
            # the local gate had just refused.
            $fixture = New-PublishWorkspace
            $hook = Join-Path $fixture.Repo '.githooks/pre-commit'
            [void](New-Item -ItemType Directory -Path (Split-Path -Parent $hook) -Force)
            [IO.File]::WriteAllText($hook, "#!/bin/sh`necho '- hygiene refused this payload'`nexit 1`n")
            if (-not $IsWindows) { & chmod +x $hook }
            & git -C $fixture.Repo config core.hooksPath .githooks | Out-Null

            $run = Invoke-Capture -Fixture $fixture -Argument @('-Feature', 'core', '-Publish') -Answer 'y'

            $run.ExitCode | Should -Be 1
            $text = $run.Output -join [Environment]::NewLine
            $text | Should -Match 'The commit was rejected'
            $text | Should -Match ([regex]::Escape('You are now on feature/windows-capture-core, which this run created.'))
            @(Get-GhLog $fixture | Where-Object { $_ -like 'pr create *' -or $_ -like 'pr merge *' }).Count |
                Should -Be 0
            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) | Should -Be @('refs/heads/dev')
            # The branch this run created carries no commit, and the payload is
            # staged where the operator can read or discard it.
            (& git -C $fixture.Repo rev-parse HEAD).Trim() |
                Should -Be (& git -C $fixture.Repo rev-parse refs/remotes/origin/dev).Trim()
            @(& git -C $fixture.Repo diff --cached --name-only) |
                Should -Be @('windows/desired/files/sample.json')
        }

        It 'names the commit it already made when a later feature''s commit is rejected' {
            Skip-WithoutEndToEnd 'a rejected second commit'
            # One commit per feature means a rejection can arrive with an
            # earlier feature already committed on the branch this run made.
            # An operator who followed the recovery advice without being told
            # would be left holding a commit nobody named.
            $fixture = New-PublishWorkspace
            $hook = Join-Path $fixture.Repo '.githooks/commit-msg'
            [void](New-Item -ItemType Directory -Path (Split-Path -Parent $hook) -Force)
            [IO.File]::WriteAllText($hook,
                "#!/bin/sh`nif grep -q 'capture extra settings' `"`$1`"; then exit 1; fi`nexit 0`n")
            if (-not $IsWindows) { & chmod +x $hook }
            & git -C $fixture.Repo config core.hooksPath .githooks | Out-Null

            $run = Invoke-Capture -Fixture $fixture -Argument @('-Publish') -Answer 'y'

            $run.ExitCode | Should -Be 1
            $text = $run.Output -join [Environment]::NewLine
            $text | Should -Match 'The commit was rejected'
            $text | Should -Match 'This run already committed, and these commits remain on the branch:'
            $text | Should -Match ([regex]::Escape('feat(windows): capture core settings from the host'))
            # And that commit really is on the branch this run created.
            (& git -C $fixture.Repo log --oneline -1).Trim() |
                Should -Match ([regex]::Escape('capture core settings from the host'))
            (& git -C $fixture.Repo branch --show-current).Trim() |
                Should -Be 'feature/windows-capture-core-extra'
            @(Get-GhLog $fixture | Where-Object { $_ -like 'pr create *' -or $_ -like 'pr merge *' }).Count |
                Should -Be 0
            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) | Should -Be @('refs/heads/dev')
            @(& git -C $fixture.Repo diff --cached --name-only) |
                Should -Be @('windows/desired/files/other.json')
        }

        It 'reuses a pull request already open against dev without printing a body it would discard' {
            Skip-WithoutEndToEnd 'the reuse path'

            $fixture = New-PublishWorkspace
            $listing = '[{"baseRefName":"dev","isCrossRepository":false,' +
            '"url":"https://github.com/example/repo/pull/7"}]'
            $run = Invoke-Capture -Fixture $fixture -Argument @('-Feature', 'core', '-Publish') `
                -Answer 'y' -Environment @{ STUB_GH_PR_LIST = $listing }

            $run.ExitCode | Should -Be 0
            $text = $run.Output -join [Environment]::NewLine
            $text | Should -Match ([regex]::Escape(
                    'pull request: https://github.com/example/repo/pull/7 (existing; title and body unchanged)'))
            # Showing a body nobody will read would promise a reviewer evidence
            # that never reaches the pull request.
            $text | Should -Not -Match 'pull request body:'
            $run.Output[-1] | Should -Be 'https://github.com/example/repo/pull/7'

            @(Get-GhLog $fixture | Where-Object { $_ -like 'pr create *' }).Count | Should -Be 0
            @(Get-GhLog $fixture)[-1] | Should -Be 'pr merge --auto --merge https://github.com/example/repo/pull/7'
        }

        It 'titles a run that captured two features generally and lists both commits' {
            Skip-WithoutEndToEnd 'a two-feature run'

            $fixture = New-PublishWorkspace
            $run = Invoke-Capture -Fixture $fixture -Argument @('-Publish') -Answer 'y'

            $run.ExitCode | Should -Be 0
            @(Get-GhLog $fixture | Where-Object { $_ -like 'pr create *' })[0] |
                Should -Match ([regex]::Escape('--title feat(windows): capture settings from the host'))
            $body = Get-Content -LiteralPath $fixture.Body -Raw
            $body | Should -Match ([regex]::Escape('- feat(windows): capture core settings from the host'))
            $body | Should -Match ([regex]::Escape('- feat(windows): capture extra settings from the host'))
            $body | Should -Match 'Feature selection: core, extra'
        }

        It 'names the commits the branch already carries before the confirmation' {
            Skip-WithoutEndToEnd 'the carried-commit disclosure'

            $fixture = New-PublishWorkspace
            & git -C $fixture.Repo switch -q -c feature/windows-existing | Out-Null
            [IO.File]::WriteAllText((Join-Path $fixture.Repo 'windows/desired/files/other.json'),
                "{`n  `"size`": 12`n}`n")
            & git -C $fixture.Repo commit -q -a -m 'an unrelated commit already on this branch' | Out-Null

            $run = Invoke-Capture -Fixture $fixture -Argument @('-Feature', 'core', '-Publish', '-WhatIf')

            $run.ExitCode | Should -Be 0
            $text = $run.Output -join [Environment]::NewLine
            $text | Should -Match 'this branch also carries, and will publish and merge:'
            $text | Should -Match 'an unrelated commit already on this branch'
            $text | Should -Match ([regex]::Escape('branch: feature/windows-existing (current)'))
        }

        It 'refuses -Publish on a detached HEAD, which is no branch to publish' {
            Skip-WithoutEndToEnd 'a detached HEAD'

            $fixture = New-PublishWorkspace
            & git -C $fixture.Repo switch -q --detach HEAD | Out-Null

            $run = Invoke-Capture -Fixture $fixture -Argument @('-Feature', 'core', '-Publish') -Answer 'y'

            $run.ExitCode | Should -Be 1
            ($run.Output -join [Environment]::NewLine) | Should -Match 'HEAD is detached'
            # Decided before gh is consulted and before anything is written.
            (Get-GhLog $fixture).Count | Should -Be 0
            @(& git -C $fixture.Repo status --porcelain).Count | Should -Be 0
            @(& git -C $fixture.Remote for-each-ref --format='%(refname)' refs/heads) | Should -Be @('refs/heads/dev')
        }

    }
}

Describe 'repository isolation' {
    BeforeAll {
        $isolate = Join-Path $repositoryRoot 'tools\isolate-git.ps1'
        $pwshPath = (Get-Process -Id $PID).Path

        # Runs one git command in a child pwsh whose environment names a decoy
        # repository the way a hook run from a linked worktree would, and
        # returns the git-dir that command resolved. With the isolation script
        # dot-sourced first the probe repository answers; without it the decoy
        # does, which is the failure this fixture exists to keep visible.
        function Get-ResolvedGitDir {
            param([bool] $Isolated)
            $decoy = Join-Path $TestDrive 'decoy.git'
            $probe = Join-Path $TestDrive ('probe-' + [guid]::NewGuid().ToString('N'))
            & git init --bare -q $decoy 2>$null
            [void](New-Item -ItemType Directory -Path $probe -Force)
            $prelude = if ($Isolated) { ". '$isolate'; " } else { '' }
            $command = $prelude + "git -C '$probe' init -q; git -C '$probe' rev-parse --absolute-git-dir"
            $savedGitDir = $env:GIT_DIR
            try {
                $env:GIT_DIR = $decoy
                return (& $pwshPath -NoProfile -Command $command 2>$null | Select-Object -Last 1)
            }
            finally {
                $env:GIT_DIR = $savedGitDir
            }
        }
    }

    It 'INV windows/no-inherited-git-context: a fixture repository is the only repository the suite reaches' {
        $resolved = Get-ResolvedGitDir -Isolated $true
        $resolved | Should -Match 'probe-[0-9a-f]{32}'
        $resolved | Should -Not -Match 'decoy'
    }

    It 'INV windows/no-inherited-git-context: without the isolation script the inherited context wins' {
        (Get-ResolvedGitDir -Isolated $false) | Should -Match 'decoy'
    }
}

Describe 'Windows tree isolation' {
    BeforeAll {
        # INV windows/no-unix-host-required
        # A read into a Unix-like tree is a path in a script, so the scan
        # reads each script the way PowerShell does, as tokens, and looks at
        # the tokens a path can be -- a string, a bare command argument, and
        # the tokens nested inside an expandable string -- so a comment that
        # mentions a Unix-like path is not a read. The pattern names the
        # Unix-like roots -- the payload and module trees, the flake, its
        # checks -- rather than every path above windows/, because the
        # applied-commit code legitimately resolves the repository's own git
        # metadata from the repository root. Case-sensitive on purpose:
        # PowerShell's own 'Modules' directory is not the Nix module tree.
        $UnixLikeTreePattern = '(^|[\\/''" ])(assets|modules)([\\/]|$)|flake\.(nix|lock)|tool[\\/]checks'
        $StringTokenKinds = @('StringLiteral', 'StringExpandable', 'HereStringLiteral', 'HereStringExpandable')

        function Get-UnixLikeTreeReference {
            param([string] $Path)
            $tokens = $null
            $errors = $null
            [void][System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errors)
            $queue = [System.Collections.Generic.Queue[object]]::new()
            foreach ($token in $tokens) { $queue.Enqueue($token) }
            while ($queue.Count) {
                $token = $queue.Dequeue()
                if ($token -is [System.Management.Automation.Language.StringExpandableToken] -and $token.NestedTokens) {
                    foreach ($nested in $token.NestedTokens) { $queue.Enqueue($nested) }
                }
                $kind = [string]$token.Kind
                $text = if ($StringTokenKinds -contains $kind) { [string]$token.Value }
                elseif ($kind -eq 'Generic') { [string]$token.Text }
                else { continue }
                if ($text -cmatch $UnixLikeTreePattern) {
                    "$($Path):$($token.Extent.StartLineNumber): $($token.Text)"
                }
            }
        }
    }

    It 'INV windows/no-unix-host-required: no script under windows/ reads a Unix-like tree' {
        $scripts = @(Get-ChildItem -Path $repositoryRoot -Recurse -File |
            Where-Object { $_.Extension -in '.ps1', '.psm1' })
        $scripts.Count | Should -BeGreaterThan 0
        $hits = @(foreach ($script in $scripts) { Get-UnixLikeTreeReference -Path $script.FullName })
        ($hits -join "`n") | Should -BeNullOrEmpty
    }

    It 'INV windows/no-unix-host-required: the scan names a script that reads a Unix-like payload and passes a comment that mentions one' {
        # The offending path is assembled from pieces so this file, which
        # the case above scans, does not carry the shape it looks for. Three
        # spellings of the same read: a quoted string, a bare argument, and
        # a string nested inside an expandable one.
        $unixPayload = 'as' + 'sets' + '\wezterm\fonts.json'
        $unixRoot = 'as' + 'sets'
        $offender = Join-Path $TestDrive 'reads-unixlike.ps1'
        [IO.File]::WriteAllText($offender, (@(
                    "`$fonts = Get-Content (Join-Path `$root '$unixPayload')"
                    "`$fonts = Get-Content (Join-Path `$root $unixPayload)"
                    "`$fonts = Get-Content `"`$root/`$(Join-Path '$unixRoot' 'wezterm')`""
                ) -join "`n") + "`n")
        $hit = @(Get-UnixLikeTreeReference -Path $offender)
        $hit.Count | Should -Be 3
        $hit[0] | Should -Match 'reads-unixlike\.ps1:1: '
        $hit[1] | Should -Match 'reads-unixlike\.ps1:2: '
        $hit[2] | Should -Match 'reads-unixlike\.ps1:3: '

        $mention = Join-Path $TestDrive 'mentions-unixlike.ps1'
        [IO.File]::WriteAllText($mention, "# The Unix-like copy lives under $($unixPayload.Replace('\', '/')).`n`$own = 'files\wezterm\fonts.json'`n")
        @(Get-UnixLikeTreeReference -Path $mention).Count | Should -Be 0
    }
}

Describe 'check entry points' {
    BeforeAll {
        $bootstrap = Join-Path $repositoryRoot 'bootstrap.ps1'
        $pwshPath = (Get-Process -Id $PID).Path

        # Runs the real entry point in a child pwsh with an empty PATH, so no
        # winget.exe is reachable and the prerequisite branch is the one that
        # answers. The same shape holds on Windows and on a Unix-like host.
        function Invoke-BootstrapCheck {
            param([string] $RequireNative)
            $savedPath = $env:PATH
            $savedNative = $env:REQUIRE_NATIVE
            try {
                $env:PATH = ''
                $env:REQUIRE_NATIVE = $RequireNative
                & $pwshPath -NoProfile -File $bootstrap -Check *> $null
                return $LASTEXITCODE
            }
            finally {
                $env:PATH = $savedPath
                $env:REQUIRE_NATIVE = $savedNative
            }
        }
    }

    It 'INV windows/check-exit-contract: reports a missing prerequisite under -Check as unverified' {
        Invoke-BootstrapCheck -RequireNative $null | Should -Be 69
    }

    It 'INV windows/check-exit-contract: turns a missing prerequisite into a failure when native evidence is required' {
        Invoke-BootstrapCheck -RequireNative '1' | Should -Be 1
    }
}
