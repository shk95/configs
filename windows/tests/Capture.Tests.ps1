BeforeAll {
    $windows = Split-Path -Parent $PSScriptRoot
    . (Join-Path $windows 'tool/isolate-git.ps1')
    Import-Module (Join-Path $windows 'src/WinEnvCapture.psm1') -Force
    Import-Module (Join-Path $windows 'src/WinEnvGeneration.psm1')
    Import-Module (Join-Path $windows 'src/WinEnv.psm1')
    function Write-CaptureJson { param($Path,$Value); [IO.File]::WriteAllText($Path,($Value | ConvertTo-Json -Depth 100),[Text.UTF8Encoding]::new($false)) }
    function Commit-CaptureFixture {
        & git -C $provider -c core.hooksPath=disabled add windows
        & git -C $provider -c core.hooksPath=disabled -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm fixture
        if ($LASTEXITCODE) { throw 'Synthetic provider commit failed.' }
        $script:pin = (& git -C $provider rev-parse HEAD).Trim()
    }
    function New-CaptureEnvironment { param($Units=@{},$Features=@('powertoys')); Write-CaptureJson $environment @{formatVersion=1;provider=@{commit=$pin};features=@($Features);units=$Units} }
    function New-CapturePlan { param($Units=@('advancedPaste'),$Documents=@('settings/paste.json')); Get-WinEnvHostCapturePlan -SourceRoot $provider -Environment $environment -Unit $Units -Document $Documents }
    function Clear-CaptureFixtureObjects {
        # Git marks only these owned synthetic object's regular files readonly
        # on Windows. Skip reparse points; never recurse through runtime links.
        $objects = Join-Path $provider '.git/objects'
        if (Test-Path $objects) {
            foreach ($directory in Get-ChildItem -LiteralPath $objects -Directory -Force) {
                if ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
                foreach ($file in Get-ChildItem -LiteralPath $directory.FullName -File -Force) {
                    if ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
                    $file.Attributes = $file.Attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
                }
            }
        }
    }
}

Describe 'host capture originals' {
    # INV windows/capture-owns-host-originals
    # INV windows/host-generation-bound
    # INV windows/subset-owns-declared-keys
    # INV windows/one-placeholder
    # INV windows/external-profile-blocks-preserved
    BeforeEach {
        $provider = Join-Path $TestDrive ([guid]::NewGuid().ToString('N'))
        [void](New-Item -ItemType Directory -Path $provider)
        Copy-Item $windows -Destination (Join-Path $provider 'windows') -Recurse
        & git -C $provider -c core.hooksPath=disabled init -q
        $originals = Join-Path $TestDrive ([guid]::NewGuid().ToString('N'))
        $targets = Join-Path $TestDrive ([guid]::NewGuid().ToString('N'))
        [void](New-Item -ItemType Directory -Path $originals,$targets)
        $environment = Join-Path $originals 'environment.json'
        $manifestPath = Join-Path $provider 'windows/desired/manifest.json'
        $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json -AsHashtable -Depth 100
        $manifest.ManagedFiles = @($manifest.ManagedFiles | Where-Object Id -In @('powershellProfile','advancedPaste','awake','windowsTerminal'))
        foreach ($definition in $manifest.ManagedFiles) {
            $definition.Target = Join-Path $targets ($definition.Id + '.payload')
            if ($definition.Id -eq 'advancedPaste') {
                [IO.File]::WriteAllText((Join-Path $provider ('windows/desired/' + $definition.Source)), '{"owned":1,"nested":{"color":"light"},"items":[{"a":1}]}')
            }
            if ($definition.Id -eq 'awake') { [IO.File]::WriteAllText((Join-Path $provider ('windows/desired/' + $definition.Source)), '{"enabled":true}') }
            $content = [IO.File]::ReadAllText((Join-Path $provider ('windows/desired/' + $definition.Source)))
            [IO.File]::WriteAllText($definition.Target,$content,[Text.UTF8Encoding]::new($false))
        }
        Write-CaptureJson $manifestPath $manifest
        Commit-CaptureFixture
        New-CaptureEnvironment
        $paste = Join-Path $targets 'advancedPaste.payload'
        $document = Join-Path $originals 'settings/paste.json'
    }
    AfterEach { Clear-CaptureFixtureObjects }

    It 'previews a no-drift first ownership transfer without writing any source or original' {
        $before = Get-WinEnvFileDigest $environment
        $plan = New-CapturePlan
        $plan.Units[0].Status | Should -Be prepared -Because $plan.Units[0].Reason
        $plan.Units[0].Payload.source | Should -Be host
        (ConvertTo-WinEnvHostCapturePreview $plan).units[0].firstConnection | Should -BeTrue
        Test-Path $document | Should -BeFalse
        Get-WinEnvFileDigest $environment | Should -BeExactly $before
        (& git -C $provider status --porcelain) | Should -BeNullOrEmpty
    }

    It 'projects chosen object keys, preserves the whole observed array and excludes unknown runtime keys' {
        [IO.File]::WriteAllText($paste,'{"owned":2,"nested":{"color":"dark","runtime":9},"items":[{"a":2,"whole":true},{"new":3}],"runtime":99}')
        $payload = (New-CapturePlan).Units[0].Payload.settings
        $payload.owned | Should -Be 2
        $payload.nested.color | Should -Be dark
        $payload.Keys | Should -Not -Contain runtime
        $payload.nested.Keys | Should -Not -Contain runtime
        @($payload.items).Count | Should -Be 2
        $payload.items[0].whole | Should -BeTrue
    }

    It 'keeps case-insensitive subset lookup without replacing an observed scalar with null' {
        [IO.File]::WriteAllText($paste,'{"OWNED":7,"NESTED":{"COLOR":"blue"},"ITEMS":[]}')
        $payload = (New-CapturePlan).Units[0].Payload.settings
        $payload.owned | Should -Be 7
        $payload.nested.color | Should -Be blue
        @($payload.items).Count | Should -Be 0
    }

    It 'refuses missing keys or migrated shapes instead of inventing deletion' {
        foreach ($content in @('{"owned":2,"items":[]}', '{"owned":2,"nested":[],"items":[]}')) {
            [IO.File]::WriteAllText($paste,$content)
            $plan = New-CapturePlan
            $plan.Units[0].Status | Should -Be refused
            (Save-WinEnvHostCapture $plan).Units[0].Status | Should -Be refused
            Test-Path $document | Should -BeFalse
        }
    }

    It 'saves document then first connection and regenerates the captured complete host source' {
        [IO.File]::WriteAllText($paste,'{"owned":2,"nested":{"color":"dark"},"items":[],"runtime":99}')
        $before = Get-WinEnvFileDigest $paste
        $saved = Save-WinEnvHostCapture (New-CapturePlan)
        $saved.Units[0].Status | Should -Be saved
        (Read-WinEnvContractJson $environment).units.advancedPaste.document | Should -BeExactly 'settings/paste.json'
        (Read-WinEnvContractJson $document).settings.owned | Should -Be 2
        Get-WinEnvFileDigest $paste | Should -BeExactly $before
        (& git -C $provider status --porcelain) | Should -BeNullOrEmpty
        $output = Join-Path $TestDrive ([guid]::NewGuid().ToString('N'))
        $generation = New-WinEnvGeneration -Environment $environment -SourceRoot $provider -Output $output
        Assert-WinEnvGeneratedIntegrity $output | Should -Not -BeNullOrEmpty
        $emitted = Read-WinEnvContractJson (Join-Path $output 'windows/desired/files/powertoys/AdvancedPaste/settings.json')
        $emitted.owned | Should -Be 2
        $emitted.Keys | Should -Not -Contain runtime
        $oldIdentity = $generation.identity
        [IO.File]::WriteAllText($paste,'{"owned":3,"nested":{"color":"dark"},"items":[]}')
        (Save-WinEnvHostCapture (New-CapturePlan -Documents @())).Units[0].Status | Should -Be saved
        { Assert-WinEnvGeneratedIntegrity $output } | Should -Throw '*original*'
        (New-WinEnvGeneration -Environment $environment -SourceRoot $provider -Output $output).identity | Should -Not -BeExactly $oldIdentity
    }

    It 'later host projection does not absorb provider updates or previously unowned host keys' {
        [void](Save-WinEnvHostCapture (New-CapturePlan))
        $definition = @($manifest.ManagedFiles | Where-Object Id -EQ advancedPaste)[0]
        [IO.File]::WriteAllText((Join-Path $provider ('windows/desired/' + $definition.Source)), '{"newProvider":4}')
        Commit-CaptureFixture
        $record = Read-WinEnvContractJson $environment
        $record.provider.commit = $pin
        Write-CaptureJson $environment $record
        [IO.File]::WriteAllText($paste,'{"owned":8,"nested":{"color":"dark"},"items":[],"newProvider":99}')
        $payload = (New-CapturePlan -Documents @()).Units[0].Payload.settings
        $payload.owned | Should -Be 8
        $payload.Keys | Should -Not -Contain newProvider
    }

    It 'keeps WhatIf read-only with the same prepared first connection' {
        $before = Get-WinEnvFileDigest $environment
        $saved = Save-WinEnvHostCapture (New-CapturePlan) -WhatIf
        $saved.Units[0].Status | Should -Be prepared
        Test-Path $document | Should -BeFalse
        Get-WinEnvFileDigest $environment | Should -BeExactly $before
    }

    It 'refuses unknown, duplicate, unselected and disabled units with no automatic selection' {
        foreach ($units in @(@('missing'),@('advancedPaste','advancedPaste'),@('windowsTerminal'))) {
            { New-CapturePlan -Units $units -Documents @() } | Should -Throw
        }
        New-CaptureEnvironment -Units @{advancedPaste=@{enabled=$false}}
        { New-CapturePlan } | Should -Throw '*selected and enabled*'
        Test-Path $document | Should -BeFalse
    }

    It 'refuses unsafe, duplicate, provider-overlap and generated document destinations' {
        foreach ($path in @('../outside.json','C:/outside.json','nested\path.json','environment.json')) {
            { New-CapturePlan -Documents @($path) } | Should -Throw
        }
        { New-CapturePlan -Units @('advancedPaste','awake') -Documents @('same.json','same.json') } | Should -Throw
        $generated = Join-Path $originals 'generated'
        [void](New-Item -ItemType Directory $generated)
        Write-CaptureJson (Join-Path $generated 'generation.json') @{formatVersion=1}
        { New-CapturePlan -Documents @('generated/settings.json') } | Should -Throw '*generated*'
        Copy-Item $environment (Join-Path $provider 'environment.json')
        { Get-WinEnvHostCapturePlan -SourceRoot $provider -Environment (Join-Path $provider 'environment.json') -Unit advancedPaste -Document settings/paste.json } | Should -Throw '*outside provider*'
    }

    It 'rejects reparse document parents rather than following another directory' {
        $outside = Join-Path $TestDrive ([guid]::NewGuid().ToString('N'))
        [void](New-Item -ItemType Directory $outside)
        $link = Join-Path $originals 'link'
        $kind = if ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) { 'Junction' } else { 'SymbolicLink' }
        [void](New-Item -ItemType $kind -Path $link -Target $outside)
        try { { New-CapturePlan -Documents @('link/settings.json') } | Should -Throw '*reparse*' }
        finally { [IO.Directory]::Delete($link) }
        Test-Path $outside | Should -BeTrue
    }

    It 'refuses changed originals, targets, provider or destinations before saving' {
        $plan = New-CapturePlan
        [IO.File]::AppendAllText($paste,' ')
        (Save-WinEnvHostCapture $plan).Units[0].Status | Should -Be failed
        Test-Path $document | Should -BeFalse
        $plan = New-CapturePlan
        [IO.File]::AppendAllText($environment,' ')
        (Save-WinEnvHostCapture $plan).Units[0].Status | Should -Be failed
        $plan = New-CapturePlan
        [void](New-Item -ItemType Directory (Split-Path -Parent $document))
        Write-CaptureJson $document @{formatVersion=1;source='host';settings=@{conflict=1}}
        (Save-WinEnvHostCapture $plan).Units[0].Status | Should -Be failed
    }

    It 'prepares all units before any durable write when another requested projection is invalid' {
        [IO.File]::WriteAllText((Join-Path $targets 'awake.payload'),'{broken')
        $plan = New-CapturePlan -Units @('advancedPaste','awake') -Documents @('settings/paste.json','settings/awake.json')
        $result = Save-WinEnvHostCapture $plan
        $result.Units[1].Status | Should -Be refused
        Test-Path $document | Should -BeFalse
    }

    It 'document failure leaves declaration unchanged and no first connection' {
        Mock Write-WinEnvCaptureDocument -ModuleName WinEnvCapture { throw 'payload failure' }
        $before = Get-WinEnvFileDigest $environment
        $result = Save-WinEnvHostCapture (New-CapturePlan)
        $result.Units[0].Status | Should -Be failed
        $result.Units[0].Saved | Should -BeFalse
        Get-WinEnvFileDigest $environment | Should -BeExactly $before
        Test-Path $document | Should -BeFalse
    }

    It 'connection failure leaves a reported inert document and explicit matching retry connects it' {
        Mock Write-WinEnvCaptureConnection -ModuleName WinEnvCapture { throw 'connection failure' }
        $before = Get-WinEnvFileDigest $environment
        $result = Save-WinEnvHostCapture (New-CapturePlan)
        $result.Units[0].Status | Should -Be unconnected
        $result.Units[0].Saved | Should -BeTrue
        Get-WinEnvFileDigest $environment | Should -BeExactly $before
        $retry = New-CapturePlan
        $retry.Units[0].Status | Should -Be prepared
        $retry.Units[0].Before | Should -Not -Be '<absent>'
        Mock Write-WinEnvCaptureConnection -ModuleName WinEnvCapture { param($Path,$Content); Write-WinEnvAtomicText $Path $Content }
        (Save-WinEnvHostCapture $retry).Units[0].Status | Should -Be saved
        $record = Read-WinEnvContractJson $environment
        $record.units.Remove('advancedPaste')
        Write-CaptureJson $environment $record
        Write-CaptureJson $document @{formatVersion=1;source='host';settings=@{conflict=1}}
        (New-CapturePlan).Units[0].Status | Should -Be refused
    }

    It 'reports completed units, inert connection failure and pending later units without rollback' {
        Mock Write-WinEnvCaptureConnection -ModuleName WinEnvCapture {
            param($Path,$Content)
            if (($Content | ConvertFrom-Json).units.awake) { throw 'second connection failure' }
            Write-WinEnvAtomicText $Path $Content
        }
        $result = Save-WinEnvHostCapture (New-CapturePlan -Units @('advancedPaste','awake','powershellProfile') -Documents @('settings/paste.json','settings/awake.json','settings/profile.json'))
        $result.Units.Status | Should -Be @('saved','unconnected','pending')
        (Read-WinEnvContractJson $environment).units.Keys | Should -Contain advancedPaste
        (Read-WinEnvContractJson $environment).units.Keys | Should -Not -Contain awake
        Test-Path (Join-Path $originals 'settings/awake.json') | Should -BeTrue
    }

    It 'existing atomic replacement failure preserves prior connected content' {
        [void](Save-WinEnvHostCapture (New-CapturePlan))
        $before = Get-WinEnvFileDigest $document
        [IO.File]::WriteAllText($paste,'{"owned":2,"nested":{"color":"dark"},"items":[]}')
        Mock Write-WinEnvCaptureDocument -ModuleName WinEnvCapture { throw 'replace failure' }
        (Save-WinEnvHostCapture (New-CapturePlan -Documents @())).Units[0].Status | Should -Be failed
        Get-WinEnvFileDigest $document | Should -BeExactly $before
        { New-CapturePlan -Documents @('settings/renamed.json') } | Should -Throw '*rename*'
    }

    It 'excludes generated Terminal profiles while retaining supported human profiles' {
        New-CaptureEnvironment -Features @('terminal')
        $target = Join-Path $targets 'windowsTerminal.payload'
        $actual = Read-WinEnvContractJson $target
        $actual.profiles.list += @{guid='{generated-test}';name='Generated';source='fixture'}
        Write-CaptureJson $target $actual
        $payload = (New-CapturePlan -Units @('windowsTerminal') -Documents @('settings/terminal.json')).Units[0].Payload.settings
        @($payload.profiles.list.guid) | Should -Not -Contain '{generated-test}'
        $actual.profiles.list += $actual.profiles.list[0]
        Write-CaptureJson $target $actual
        (New-CapturePlan -Units @('windowsTerminal') -Documents @('settings/terminal.json')).Units[0].Status | Should -Be refused
    }

    It 'captures only the managed profile payload and restores its single supported placeholder' {
        $target = Join-Path $targets 'powershellProfile.payload'
        [IO.File]::WriteAllText($target,'# synthetic managed profile')
        $foreign = Join-Path $targets 'shared-profile.ps1'
        [IO.File]::WriteAllText($foreign,'# foreign block')
        $before = Get-WinEnvFileDigest $foreign
        $payload = (New-CapturePlan -Units @('powershellProfile') -Documents @('settings/profile.json')).Units[0].Payload.settings
        $payload | Should -BeExactly '# synthetic managed profile'
        Get-WinEnvFileDigest $foreign | Should -BeExactly $before
        $hostPath = @{LocalAppData='C:\fixture\local';UserProfile='C:\fixture\user';AppData='C:\fixture\roaming';UserName='synthetic'}
        $local = $hostPath.LocalAppData.Replace('\','\\')
        (ConvertFrom-WinEnvTemplate -Content "{`"directory`":`"$local`"}" -HostPath $hostPath).Content | Should -Match '__LOCALAPPDATA_JSON__'
    }

    It 'refuses malformed UTF8, UTF16 BOM and NUL text without repairing observed bytes' {
        $target = Join-Path $targets 'powershellProfile.payload'
        foreach ($bytes in @([byte[]]@(35,32,255), [byte[]]@(255,254,35,0), [byte[]]@(35,0,32,0))) {
            [IO.File]::WriteAllBytes($target,$bytes)
            $before = Get-WinEnvFileDigest $target
            $plan = New-CapturePlan -Units @('powershellProfile') -Documents @('settings/profile.json')
            $plan.Units[0].Status | Should -Be refused
            (Save-WinEnvHostCapture $plan).Units[0].Status | Should -Be refused
            Get-WinEnvFileDigest $target | Should -BeExactly $before
            Test-Path (Join-Path $originals 'settings/profile.json') | Should -BeFalse
        }
    }

    It 'accepts optional UTF8 BOM while preserving text newline content and private literal values' {
        $target = Join-Path $targets 'powershellProfile.payload'
        $text = "# synthetic private value`r`n"
        [IO.File]::WriteAllBytes($target,([byte[]]@(239,187,191)+[Text.Encoding]::UTF8.GetBytes($text)))
        $plan = New-CapturePlan -Units @('powershellProfile') -Documents @('settings/profile.json')
        $plan.Units[0].Payload.settings | Should -BeExactly $text
    }

    It 'marks an absent parser as unavailable and refuses Save without treating it as valid' {
        Mock Test-WinEnvSourceFile -ModuleName WinEnvCapture { 'synthetic parser unavailable' }
        $plan = New-CapturePlan
        $plan.Units[0].Status | Should -Be refused
        $plan.Units[0].Unavailable | Should -BeTrue
        (Save-WinEnvHostCapture $plan).Units[0].Status | Should -Be refused
        Test-Path $document | Should -BeFalse
    }

    It 'refuses dirty provider tools, malformed formats and source-bound execution mismatch' {
        $plan = New-CapturePlan
        [IO.File]::AppendAllText((Join-Path $provider 'windows/tool/capture.ps1'),"`n# changed")
        (Save-WinEnvHostCapture $plan).Units[0].Status | Should -Be failed
        Test-Path $document | Should -BeFalse
        Commit-CaptureFixture
        New-CaptureEnvironment
        { New-CapturePlan } | Should -Throw '*execution tools*'
        $record=Read-WinEnvContractJson $environment
        $record.formatVersion=99
        Write-CaptureJson $environment $record
        { New-CapturePlan } | Should -Throw '*formatVersion*'
    }

    It 'rejects runtime targets and malformed JSON without changing observations or originals' {
        [IO.File]::WriteAllText($paste,'{"owned":1,"owned":2}')
        (New-CapturePlan).Units[0].Status | Should -Be refused
        $definition=@($manifest.ManagedFiles | Where-Object Id -EQ advancedPaste)[0]
        $definition.Target=Join-Path $targets 'workspaces.json'
        [IO.File]::WriteAllText($definition.Target,'{}')
        Write-CaptureJson $manifestPath $manifest
        Commit-CaptureFixture
        New-CaptureEnvironment
        $plan=New-CapturePlan
        $plan.Units[0].Status | Should -Be refused
        $plan.Units[0].Reason | Should -Match 'runtime'
    }

    It 'validates actual entry preview/save/status forwarding on native Windows using synthetic targets only' {
        if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { Set-ItResult -Skipped -Because 'Native capture entry observation requires Windows'; return }
        $pwsh=(Get-Process -Id $PID).Path
        $entry=Join-Path $provider 'windows/win-env.ps1'
        $before=Get-WinEnvFileDigest $paste
        $output=& $pwsh -NoProfile -File $entry capture -SourceRoot $provider -Environment $environment -Unit advancedPaste -Document settings/paste.json 2>&1
        $LASTEXITCODE | Should -Be 0
        ($output | Out-String | ConvertFrom-Json).units[0].firstConnection | Should -BeTrue
        Test-Path $document | Should -BeFalse
        $output=& $pwsh -NoProfile -File $entry capture -SourceRoot $provider -Environment $environment -Unit advancedPaste -Document settings/paste.json -Save 2>&1
        $LASTEXITCODE | Should -Be 0
        ($output | Out-String | ConvertFrom-Json).units[0].status | Should -Be saved
        Get-WinEnvFileDigest $paste | Should -BeExactly $before
        (& git -C $provider status --porcelain) | Should -BeNullOrEmpty
    }
}

Describe 'host capture public entry' {
    # INV windows/capture-owns-host-originals
    # INV windows/entry-point-forwards-status
    It 'contains no provider writer, Git publication helper or legacy publishing parameter' {
        $module = [IO.File]::ReadAllText((Join-Path $windows 'src/WinEnv.psm1'))
        $module | Should -Not -Match 'function (Save-WinEnvCapturedPayload|Publish-WinEnvCapture|New-WinEnvCaptureBranch|Remove-WinEnvMergedLocalBranch)'
        $tokens=$null;$errors=$null
        $ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $windows 'tool/capture.ps1'),[ref]$tokens,[ref]$errors)
        $errors.Count | Should -Be 0
        $parameters=@($ast.ParamBlock.Parameters | ForEach-Object { $_.Name.VariablePath.UserPath })
        $parameters | Should -Contain Save
        $parameters | Should -Not -Contain Publish
        $parameters | Should -Not -Contain Branch
        $capture=[IO.File]::ReadAllText((Join-Path $windows 'tool/capture.ps1'))
        $capture | Should -Not -Match 'git (add|commit|push|switch)|gh pr|--auto'
    }
    It 'forwards legacy parameter refusal and missing host inputs before any original exists' {
        $entry=Join-Path $windows 'win-env.ps1'
        $pwsh=(Get-Process -Id $PID).Path
        $output=& $pwsh -NoProfile -File $entry capture -Publish 2>&1
        $LASTEXITCODE | Should -Be 1
        ($output | Out-String) | Should -Match 'Publish'
        $output=& $pwsh -NoProfile -File $entry capture 2>&1
        $LASTEXITCODE | Should -Be 64
    }
    It 'refuses host observation on a foreign host' {
        if ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) { Set-ItResult -Skipped -Because 'Foreign-host refusal does not apply on native Windows'; return }
        $pwsh=(Get-Process -Id $PID).Path
        $output=& $pwsh -NoProfile -File (Join-Path $windows 'win-env.ps1') capture -SourceRoot nonexistent -Environment nonexistent -Unit advancedPaste 2>&1
        $LASTEXITCODE | Should -Be 1
        ($output | Out-String) | Should -Match 'only runs on Windows'
    }
}
