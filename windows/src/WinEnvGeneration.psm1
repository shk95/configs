# Windows-owned declaration and generation; local Git is the initial transport.
# INV windows/host-generation-bound: versioned explicit inputs and exact source
# identity are checked before materialization or reconciliation.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:ExecutionToolDigests = [ordered]@{}
$script:ExecutionWindowsRoot = Split-Path -Parent $PSScriptRoot
foreach ($relative in @('src/WinEnvGeneration.psm1', 'src/WinEnv.psm1', 'tool/consumer.ps1', 'win-env.ps1')) {
    $script:ExecutionToolDigests[$relative] = (Get-FileHash -LiteralPath (Join-Path $script:ExecutionWindowsRoot $relative) -Algorithm SHA256).Hash.ToLowerInvariant()
}
Import-Module (Join-Path $PSScriptRoot 'WinEnv.psm1') -Scope Local

function Assert-WinEnvJsonKeys {
    param([System.Text.Json.JsonElement] $Element)
    if ($Element.ValueKind -eq [System.Text.Json.JsonValueKind]::Object) {
        $keys = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach ($p in $Element.EnumerateObject()) {
            if (-not $keys.Add($p.Name)) { throw "Duplicate or ambiguous JSON key '$($p.Name)'." }
            Assert-WinEnvJsonKeys $p.Value
        }
    }
    elseif ($Element.ValueKind -eq [System.Text.Json.JsonValueKind]::Array) {
        foreach ($v in $Element.EnumerateArray()) { Assert-WinEnvJsonKeys $v }
    }
}

function Read-WinEnvContractJson {
    param([Parameter(Mandatory)][string] $Path)
    $bytes = [IO.File]::ReadAllBytes($Path)
    $offset = 0
    # Accept an optional UTF-8 BOM; never autodetect UTF-16 or replace bad bytes.
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) { $offset = 3 }
    try { $text = [Text.UTF8Encoding]::new($false, $true).GetString($bytes, $offset, $bytes.Length - $offset) }
    catch { throw 'Contract documents must be strict UTF-8 JSON.' }
    $json = [System.Text.Json.JsonDocument]::Parse($text)
    try { Assert-WinEnvJsonKeys $json.RootElement } finally { $json.Dispose() }
    return ($text | ConvertFrom-Json -AsHashtable -Depth 100)
}

function Assert-WinEnvContractFields {
    param($Value, [string[]] $Required, [string[]] $Optional = @(), [string] $Label)
    if ($Value -isnot [System.Collections.IDictionary]) { throw "$Label must be an object." }
    foreach ($key in $Value.Keys) {
        if (@($Required) + @($Optional) -cnotcontains $key) { throw "$Label has unknown field '$key'." }
    }
    foreach ($key in $Required) {
        if (@($Value.Keys) -cnotcontains $key) { throw "$Label is missing '$key'." }
    }
}

function Assert-WinEnvFormatVersion {
    param($Value, [string] $Label)
    if (($Value -isnot [int] -and $Value -isnot [long]) -or $Value -ne 1) {
        throw "Unsupported $Label formatVersion; expected 1."
    }
}

function Get-WinEnvFileDigest {
    param([string] $Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-WinEnvRecordDigest {
    param($Value)
    $bytes = [Text.Encoding]::UTF8.GetBytes(($Value | ConvertTo-Json -Depth 100 -Compress))
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($algorithm.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
}

function Resolve-WinEnvContractPath {
    param([string] $Root, [string] $Relative)
    if ([string]::IsNullOrWhiteSpace($Relative) -or [IO.Path]::IsPathRooted($Relative) -or
        $Relative -match '[:\\]' -or ($Relative.Split('/') -contains '..')) {
        throw "Settings connection must be an explicit relative path without traversal: '$Relative'."
    }
    $base = [IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $full = [IO.Path]::GetFullPath((Join-Path $base $Relative))
    if (-not $full.StartsWith($base + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Settings connection escapes its declaration directory.'
    }
    $cursor = $full
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            if ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw 'Settings connection or its directory is a symbolic link/reparse point.'
            }
        }
        $parent = Split-Path -Parent $cursor
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw "Connected settings document is missing: '$Relative'." }
    return $full
}

function Invoke-WinEnvSourceGit {
    param([string] $Root, [string[]] $Argument)
    $git = Get-Command git.exe, git -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $git) { throw 'Local Git is required for provider provenance.' }
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $git.Source
    $info.UseShellExecute = $false
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    foreach ($name in @($info.Environment.Keys)) {
        if ($name -like 'GIT_*') { [void]$info.Environment.Remove($name) }
    }
    foreach ($arg in @('-c', 'core.quotePath=false', '-C', $Root) + $Argument) { $info.ArgumentList.Add($arg) }
    $p = [Diagnostics.Process]::Start($info)
    try {
        $text = $p.StandardOutput.ReadToEnd()
        $errorText = $p.StandardError.ReadToEnd()
        $p.WaitForExit()
        if ($p.ExitCode -ne 0) { throw "Provider Git provenance unavailable: $errorText" }
        return $text.TrimEnd("`r", "`n")
    }
    finally { $p.Dispose() }
}

function Get-WinEnvProviderSource {
    param([Parameter(Mandatory)][string] $SourceRoot, [string] $Commit)
    $root = (Resolve-Path -LiteralPath $SourceRoot).ProviderPath
    $actual = Invoke-WinEnvSourceGit $root @('rev-parse', '--verify', 'HEAD^{commit}')
    if ($actual -cnotmatch '\A[0-9a-f]{40}\z') { throw 'Provider commit must be a full 40-character SHA.' }
    if ($Commit -and $Commit -cne $actual) { throw 'Local provider checkout does not match environment.provider.commit.' }
    Assert-WinEnvSourceIndexFlags $root
    if (Invoke-WinEnvSourceGit $root @('status', '--porcelain', '--untracked-files=all', '--', 'windows')) {
        throw 'Provider Windows source/tools differ from the pinned commit; use a clean exact checkout.'
    }
    $paths = @( (Invoke-WinEnvSourceGit $root @('ls-tree', '-r', '--name-only', 'HEAD', '--', 'windows')) -split "`n" )
    foreach ($path in $paths) { [void](Resolve-WinEnvContractPath -Root $root -Relative $path) }
    foreach ($relative in $script:ExecutionToolDigests.Keys) {
        if ((Get-WinEnvFileDigest (Join-Path $root "windows/$relative")) -cne $script:ExecutionToolDigests[$relative]) {
            throw "Generation execution tools differ from the pinned provider ('$relative'); use its own inspect/generate entry point."
        }
    }
    $manifest = Get-WinEnvManifest -Path (Join-Path $root 'windows/desired/manifest.json')
    $formats = Read-WinEnvContractJson (Join-Path $root 'windows/tool/consumer-format.json')
    Assert-WinEnvContractFields $formats @('formatVersion', 'environment', 'settings', 'generation') @() 'provider formats'
    foreach ($value in $formats.Values) { Assert-WinEnvFormatVersion $value 'provider consumer' }
    return [pscustomobject]@{
        Root = $root; Commit = $actual; Manifest = $manifest; Paths = $paths
        Tree = (Invoke-WinEnvSourceGit $root @('rev-parse', 'HEAD:windows'))
    }
}

function Assert-WinEnvSourceIndexFlags {
    param([string] $Root)
    foreach ($entry in ((Invoke-WinEnvSourceGit $Root @('ls-files', '-v', '--', 'windows')) -split "`n")) {
        if ($entry -cmatch '\A(?:[a-z]|S) ') {
            throw 'Provider Windows source uses assume-unchanged/skip-worktree index flags; a fully checked clean checkout is required.'
        }
    }
}

function Get-WinEnvConsumerContract {
    param([Parameter(Mandatory)][string] $SourceRoot)
    $source = Get-WinEnvProviderSource $SourceRoot
    return [ordered]@{
        formatVersion = 1
        provider = [ordered]@{ commit = $source.Commit; windowsTree = $source.Tree }
        formats = [ordered]@{ environment = 1; settings = 1; generation = 1 }
        features = @($source.Manifest.Features)
        units = @($source.Manifest.ManagedFiles | ForEach-Object {
            [ordered]@{ id = $_.Id; feature = $_.Feature; parser = $_.Parser; compare = $_.Compare; defaultSource = 'configs' }
        })
        clientBaseline = [ordered]@{ edition = 'Windows 10 IoT Enterprise LTSC 21H2'; architecture = 'x64'; build = 19044 }
        excludedCapabilities = @('defaultTerminalDelegation', 'wslConfig', 'fancyZonesCustomLayouts', 'fancyZonesLayoutHotkeys')
        verificationRuntime = Read-WinEnvContractJson (Join-Path $source.Root 'windows/tool/ci-runtime.json')
    }
}

function Get-WinEnvEnvironmentPlan {
    param([Parameter(Mandatory)][string] $Environment, [Parameter(Mandatory)][string] $SourceRoot)
    $environmentPath = (Resolve-Path -LiteralPath $Environment).ProviderPath
    $record = Read-WinEnvContractJson $environmentPath
    Assert-WinEnvContractFields $record @('formatVersion', 'provider', 'features', 'units') @() 'environment'
    Assert-WinEnvFormatVersion $record.formatVersion 'environment'
    Assert-WinEnvContractFields $record.provider @('commit') @() 'environment.provider'
    if ($record.provider.commit -isnot [string] -or $record.provider.commit -cnotmatch '\A[0-9a-f]{40}\z') {
        throw 'environment.provider.commit must be a full 40-character SHA.'
    }
    $source = Get-WinEnvProviderSource -SourceRoot $SourceRoot -Commit $record.provider.commit
    if ($record.features -isnot [array]) { throw 'environment.features must be an array.' }
    $featureNames = @($source.Manifest.Features | ForEach-Object { $_.Id })
    $seenFeatures = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($id in $record.features) {
        if ($id -isnot [string] -or $featureNames -cnotcontains $id) { throw "Unknown active feature '$id'." }
        if (-not $seenFeatures.Add($id)) { throw "Duplicate selected feature '$id'." }
    }
    $selection = Get-WinEnvFeatureSelection -Manifest $source.Manifest -Requested $record.features
    if ($record.units -isnot [System.Collections.IDictionary]) { throw 'environment.units must be an object.' }
    $inputs = [Collections.Generic.List[object]]::new()
    $inputs.Add([ordered]@{ path = $environmentPath; sha256 = Get-WinEnvFileDigest $environmentPath })
    $connections = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $unitPlans = [Collections.Generic.List[object]]::new()
    foreach ($id in $record.units.Keys) {
        if ([string]::IsNullOrWhiteSpace($id)) { throw 'Unit identity must be nonempty.' }
        $entry = $record.units[$id]
        Assert-WinEnvContractFields $entry @('enabled') @('document') "unit '$id'"
        if ($entry.enabled -isnot [bool]) { throw "Unit '$id' enabled must be a boolean." }
        $definition = @($source.Manifest.ManagedFiles | Where-Object { $_.Id -ceq $id })
        if (-not $definition.Count -and $entry.enabled) { throw "Unknown active unit '$id'." }
        if ($entry.Contains('document')) {
            if ($entry.document -isnot [string]) { throw "Unit '$id' document must be a string." }
            $path = Resolve-WinEnvContractPath (Split-Path -Parent $environmentPath) $entry.document
            if (-not $connections.Add($path)) { throw "Duplicate resolved settings connection for '$id'." }
            $document = Read-WinEnvContractJson $path
            Assert-WinEnvContractFields $document @('formatVersion', 'source', 'settings') @() "settings '$id'"
            Assert-WinEnvFormatVersion $document.formatVersion 'settings'
            if ($document.source -isnot [string] -or @('configs', 'host') -cnotcontains $document.source) { throw "Unknown settings source for '$id'." }
            if ($document.source -ceq 'configs' -and $null -ne $document.settings) { throw 'configs settings must be null; host values are never ignored.' }
            if ($document.source -ceq 'host' -and $document.settings -isnot [string] -and $document.settings -isnot [System.Collections.IDictionary]) {
                throw 'host settings must be a JSON object or text string.'
            }
            $inputs.Add([ordered]@{ path = $path; sha256 = Get-WinEnvFileDigest $path })
        }
    }
    foreach ($definition in $source.Manifest.ManagedFiles) {
        $id = [string]$definition.Id
        if ($selection.Selected -cnotcontains $definition.Feature) { continue }
        $entry = if ($record.units.Contains($id)) { $record.units[$id] } else { $null }
        if ($entry -and -not $entry.enabled) { continue }
        $document = $null
        if ($entry -and $entry.Contains('document')) {
            $document = Read-WinEnvContractJson (Resolve-WinEnvContractPath (Split-Path -Parent $environmentPath) $entry.document)
        }
        $choice = if ($document) { $document.source } else { 'configs' }
        if ($choice -ceq 'host') {
            if ($definition.Parser -ceq 'Json') {
                if ($document.settings -isnot [System.Collections.IDictionary]) { throw "Active Json unit '$id' requires object settings." }
                $content = $document.settings | ConvertTo-Json -Depth 100
                if ($definition.Compare -ceq 'ExactJsonWithGeneratedProfiles') {
                    [void](Test-WinEnvJsonWithGeneratedProfiles -Expected $content -Actual $content)
                }
            }
            else {
                if ($document.settings -isnot [string]) { throw "Active text unit '$id' requires string settings." }
                $content = $document.settings
            }
        }
        else { $content = [IO.File]::ReadAllText((Join-Path $source.Root "windows/desired/$($definition.Source)")) }
        $unitPlans.Add([pscustomobject]@{ Definition = $definition; Source = $choice; Content = $content })
    }
    return [pscustomobject]@{ Source = $source; Selection = $selection; Inputs = $inputs.ToArray(); Units = $unitPlans.ToArray() }
}

function Assert-WinEnvGeneratedIntegrity {
    param([Parameter(Mandatory)][string] $Generation)
    $root = (Resolve-Path -LiteralPath $Generation).ProviderPath
    $record = Read-WinEnvContractJson (Join-Path $root 'generation.json')
    Assert-WinEnvContractFields $record @('formatVersion', 'provider', 'inputs', 'selected', 'units', 'files', 'identity') @() 'generation'
    Assert-WinEnvFormatVersion $record.formatVersion 'generation'
    Assert-WinEnvContractFields $record.provider @('commit', 'windowsTree') @() 'generation.provider'
    foreach ($field in @('commit', 'windowsTree')) {
        if ($record.provider[$field] -isnot [string] -or $record.provider[$field] -cnotmatch '\A[0-9a-f]{40}\z') {
            throw "Invalid generation provider $field."
        }
    }
    foreach ($field in @('inputs', 'selected', 'units', 'files')) {
        if ($record[$field] -isnot [array]) { throw "generation.$field must be an array." }
    }
    if (-not $record.inputs.Count -or -not $record.files.Count -or -not $record.selected.Count) { throw 'Generation requires inputs, files and selected closure.' }
    foreach ($input in $record.inputs) {
        Assert-WinEnvContractFields $input @('path', 'sha256') @() 'generation input'
        if ($input.path -isnot [string] -or -not [IO.Path]::IsPathRooted($input.path) -or
            $input.sha256 -isnot [string] -or $input.sha256 -cnotmatch '\A[0-9a-f]{64}\z') { throw 'Invalid generation input identity.' }
    }
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($file in $record.files) {
        Assert-WinEnvContractFields $file @('path', 'sha256') @() 'generation file'
        if ($file.path -isnot [string] -or -not $seen.Add($file.path) -or
            $file.sha256 -isnot [string] -or $file.sha256 -cnotmatch '\A[0-9a-f]{64}\z') { throw 'Invalid or duplicate generation file identity.' }
    }
    $seen.Clear()
    foreach ($id in $record.selected) {
        if ($id -isnot [string] -or -not $seen.Add($id)) { throw 'Invalid or duplicate selected generation feature.' }
    }
    $seen.Clear()
    foreach ($unit in $record.units) {
        Assert-WinEnvContractFields $unit @('id', 'source') @() 'generation unit'
        if ($unit.id -isnot [string] -or -not $seen.Add($unit.id) -or
            $unit.source -isnot [string] -or @('configs','host') -cnotcontains $unit.source) { throw 'Invalid or duplicate generation unit.' }
    }
    $identity = $record.identity
    [void]$record.Remove('identity')
    if ($identity -isnot [string] -or $identity -cne (Get-WinEnvRecordDigest $record)) { throw 'Generated metadata identity changed; regenerate.' }
    $record.Add('identity', $identity)
    foreach ($input in $record.inputs) {
        if (-not (Test-Path -LiteralPath $input.path -PathType Leaf) -or (Get-WinEnvFileDigest $input.path) -cne $input.sha256) {
            throw 'Original environment/settings input changed or is missing; regenerate before Check/Apply.'
        }
        [void](Resolve-WinEnvContractPath -Root (Split-Path -Parent $input.path) -Relative (Split-Path -Leaf $input.path))
    }
    foreach ($file in $record.files) {
        $path = Resolve-WinEnvContractPath $root $file.path
        if ((Get-WinEnvFileDigest $path) -cne $file.sha256) { throw "Generated payload/tool '$($file.path)' changed; regenerate." }
    }
    $actual = @(Get-ChildItem -LiteralPath $root -File -Recurse -Force | ForEach-Object {
        [IO.Path]::GetRelativePath($root, $_.FullName).Replace('\', '/')
    } | Where-Object { $_ -cne 'generation.json' } | Sort-Object)
    $expected = @($record.files | ForEach-Object { $_.path } | Sort-Object)
    if (($actual -join "`n") -cne ($expected -join "`n")) { throw 'Generated file set changed; regenerate.' }
    $manifest = Get-WinEnvManifest (Join-Path $root 'windows/desired/manifest.json')
    $selection = Get-WinEnvFeatureSelection -Manifest $manifest -Requested $record.selected
    if (($selection.Selected -join ',') -cne ($record.selected -join ',')) { throw 'Generation selection is not its complete ordered dependency closure.' }
    if ((@($manifest.ManagedFiles | ForEach-Object { $_.Id }) -join ',') -cne (@($record.units | ForEach-Object { $_.id }) -join ',')) {
        throw 'Generation unit metadata differs from its active manifest.'
    }
    if (@($manifest.ManagedFiles | Where-Object { $record.selected -cnotcontains $_.Feature }).Count) { throw 'Generation contains an unselected unit.' }
    return $record
}

function Publish-WinEnvGenerationDirectory {
    param([string] $Prepared, [string] $Output)
    $backup = "$Output.previous-$([guid]::NewGuid().ToString('N'))"
    $hadPrevious = Test-Path -LiteralPath $Output
    try {
        if ($hadPrevious) { Move-WinEnvGenerationDirectory $Output $backup }
        Move-WinEnvGenerationDirectory $Prepared $Output
    }
    catch {
        if ($hadPrevious -and (Test-Path -LiteralPath $backup) -and -not (Test-Path -LiteralPath $Output)) {
            Move-WinEnvGenerationDirectory $backup $Output
        }
        throw
    }
    if ($hadPrevious) {
        try { Remove-Item -LiteralPath $backup -Recurse -Force }
        catch { Write-Warning "Published generation is current; its previous directory remains at '$backup'." }
    }
}

function Move-WinEnvGenerationDirectory {
    param([string] $Source, [string] $Destination)
    [IO.Directory]::Move($Source, $Destination)
}

function New-WinEnvGeneration {
    param([Parameter(Mandatory)][string] $Environment, [Parameter(Mandatory)][string] $SourceRoot,
        [Parameter(Mandatory)][string] $Output)
    $plan = Get-WinEnvEnvironmentPlan $Environment $SourceRoot
    $outputPath = [IO.Path]::GetFullPath($Output).TrimEnd([IO.Path]::DirectorySeparatorChar)
    foreach ($protected in @($plan.Source.Root, (Split-Path -Parent $plan.Inputs[0].path))) {
        $base = [IO.Path]::GetFullPath($protected).TrimEnd([IO.Path]::DirectorySeparatorChar)
        if ($outputPath -eq $base -or $outputPath.StartsWith($base + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
            $base.StartsWith($outputPath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Generation output must not overlap the provider or host originals.'
        }
    }
    $parent = Split-Path -Parent $outputPath
    if (Test-Path -LiteralPath $outputPath) {
        if (-not (Test-Path -LiteralPath (Join-Path $outputPath 'generation.json') -PathType Leaf)) {
            throw 'Existing output is not a generation; choose a dedicated output directory.'
        }
        Assert-WinEnvFormatVersion (Read-WinEnvContractJson (Join-Path $outputPath 'generation.json')).formatVersion 'previous generation'
    }
    $cursor = $outputPath
    while ($cursor) {
        if ((Test-Path -LiteralPath $cursor) -and ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Generation output or its parent is a symbolic link/reparse point.'
        }
        $next = Split-Path -Parent $cursor
        if ($next -eq $cursor) { break }
        $cursor = $next
    }
    [void](New-Item -ItemType Directory -Path $parent -Force)
    $prepared = Join-Path $parent ('.win-env-generation-' + [guid]::NewGuid().ToString('N'))
    try {
        [void](New-Item -ItemType Directory -Path $prepared)
        foreach ($path in $plan.Source.Paths) {
            if ($path -notmatch '\Awindows/(src/|tool/|win-env\.ps1\z|toolchain\.json\z)') { continue }
            $target = Join-Path $prepared $path
            [void](New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force)
            Copy-Item -LiteralPath (Join-Path $plan.Source.Root $path) -Destination $target
        }
        $desired = Join-Path $prepared 'windows/desired'
        [void](New-Item -ItemType Directory -Path $desired -Force)
        [void](New-Item -ItemType Directory -Path (Join-Path $desired 'files') -Force)
        $manifest = $plan.Source.Manifest
        $manifest.ManagedFiles = @($plan.Units | ForEach-Object { $_.Definition })
        Write-WinEnvAtomicText (Join-Path $desired 'manifest.json') ($manifest | ConvertTo-Json -Depth 100)
        foreach ($unit in $plan.Units) {
            $target = Join-Path $desired $unit.Definition.Source
            Write-WinEnvAtomicText $target $unit.Content
            $reason = Test-WinEnvSourceFile -Definition $unit.Definition -RepositoryRoot $desired
            if ($reason) { throw "Generation requires the active parser for '$($unit.Definition.Id)': $reason" }
        }
        $files = @(Get-ChildItem -LiteralPath $prepared -File -Recurse | Sort-Object FullName | ForEach-Object {
            [ordered]@{ path = [IO.Path]::GetRelativePath($prepared, $_.FullName).Replace('\', '/'); sha256 = Get-WinEnvFileDigest $_.FullName }
        })
        $record = [ordered]@{
            formatVersion = 1
            provider = [ordered]@{ commit = $plan.Source.Commit; windowsTree = $plan.Source.Tree }
            inputs = @($plan.Inputs)
            selected = @($plan.Selection.Selected)
            units = @($plan.Units | ForEach-Object { [ordered]@{ id = $_.Definition.Id; source = $_.Source } })
            files = $files
        }
        $record.identity = Get-WinEnvRecordDigest $record
        Write-WinEnvAtomicText (Join-Path $prepared 'generation.json') ($record | ConvertTo-Json -Depth 100)
        [void](Assert-WinEnvGeneratedIntegrity $prepared)
        [void](Get-WinEnvManifest (Join-Path $desired 'manifest.json'))
        Assert-WinEnvSourceIndexFlags $plan.Source.Root
        if ((Invoke-WinEnvSourceGit $plan.Source.Root @('rev-parse', '--verify', 'HEAD^{commit}')) -cne $plan.Source.Commit -or
            (Invoke-WinEnvSourceGit $plan.Source.Root @('status', '--porcelain', '--untracked-files=all', '--', 'windows'))) {
            throw 'Pinned provider changed during generation; previous result was preserved.'
        }
        Publish-WinEnvGenerationDirectory $prepared $outputPath
        return [ordered]@{ output = $outputPath; identity = $record.identity; provider = $record.provider; selected = $record.selected }
    }
    finally { if (Test-Path -LiteralPath $prepared) { Remove-Item -LiteralPath $prepared -Recurse -Force } }
}

function Get-WinEnvLegacySelectionProposal {
    param([Parameter(Mandatory)][string] $SourceRoot, [string] $State)
    $source = Get-WinEnvProviderSource $SourceRoot
    $stateRecord = if ($State) { Get-WinEnvState $State } else { $null }
    $features = @()
    $provenance = 'first-use core-only proposal'
    if ($stateRecord) {
        if ($stateRecord.schemaVersion -eq 3) { throw 'State already belongs to a host generation; use its original declaration.' }
        if ($stateRecord.schemaVersion -eq 2) {
            $features = @($stateRecord.features)
            $provenance = 'schema 2 recorded selection'
        }
        else {
            if ($stateRecord.gitCommit -notmatch '\A[0-9a-f]{40}\z') { throw 'Schema 1 needs its full recorded commit to reconstruct historical selection.' }
            $old = Invoke-WinEnvSourceGit $source.Root @('show', "$($stateRecord.gitCommit):windows/desired/manifest.json")
            $oldManifest = $old | ConvertFrom-Json -AsHashtable -Depth 100
            $features = @($oldManifest.Features | ForEach-Object { $_.Id })
            $provenance = 'schema 1 exact recorded source manifest'
        }
    }
    $known = @($source.Manifest.Features | ForEach-Object { $_.Id })
    $actions = @($features | Where-Object { $known -cnotcontains $_ } | ForEach-Object {
        "Selection '$_' is retired/unknown: explicit correction and host-owned management are required before generation."
    })
    return [ordered]@{
        formatVersion = 1; provenance = $provenance; blocked = [bool]$actions.Count; actions = $actions
        environment = [ordered]@{ formatVersion = 1; provider = [ordered]@{ commit = $source.Commit }; features = $features; units = [ordered]@{} }
    }
}

function Write-WinEnvGenerationAttempt {
    param([Parameter(Mandatory)][string] $Path, [Parameter(Mandatory)] $Generation,
        [Parameter(Mandatory)][string] $ProjectVersion, [Parameter(Mandatory)][string] $BundleHash,
        [string[]] $Feature, [ValidateSet('success', 'failed')][string] $Outcome,
        [AllowEmptyCollection()][string[]] $Completed = @(), [string] $FontRegisteredAtUtc)
    $stamp = [DateTimeOffset]::UtcNow.ToString('o')
    $record = [ordered]@{
        schemaVersion = 3; projectVersion = $ProjectVersion; features = @($Feature)
        gitCommit = $Generation.provider.commit; bundleHash = $BundleHash
        generationIdentity = $Generation.identity; outcome = $Outcome; attemptedAtUtc = $stamp
        completed = @($Completed); appliedAtUtc = if ($Outcome -ceq 'success') { $stamp } else { $null }
    }
    if ($FontRegisteredAtUtc) { $record.fontRegisteredAtUtc = $FontRegisteredAtUtc }
    Write-WinEnvAtomicText $Path ($record | ConvertTo-Json -Depth 100)
}
Export-ModuleMember -Function Read-WinEnvContractJson, Get-WinEnvFileDigest, Get-WinEnvRecordDigest, Resolve-WinEnvContractPath, Invoke-WinEnvSourceGit, Get-WinEnvProviderSource, Get-WinEnvConsumerContract, Get-WinEnvEnvironmentPlan, Assert-WinEnvGeneratedIntegrity, Publish-WinEnvGenerationDirectory, New-WinEnvGeneration, Get-WinEnvLegacySelectionProposal, Write-WinEnvGenerationAttempt
