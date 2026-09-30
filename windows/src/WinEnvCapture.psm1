# INV windows/capture-owns-host-originals: capture observes selected app units,
# previews host documents and explicitly saves originals without provider writes.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:CaptureWindowsRoot = Split-Path -Parent $PSScriptRoot
$script:CaptureToolDigests = [ordered]@{}
foreach ($relative in @('src/WinEnvCapture.psm1', 'tool/capture.ps1')) {
    $script:CaptureToolDigests[$relative] = (Get-FileHash -LiteralPath (Join-Path $script:CaptureWindowsRoot $relative) -Algorithm SHA256).Hash.ToLowerInvariant()
}
Import-Module (Join-Path $PSScriptRoot 'WinEnvGeneration.psm1') -Scope Local
Import-Module (Join-Path $PSScriptRoot 'WinEnv.psm1') -Scope Local

function Assert-WinEnvCapturePath {
    param([string] $Path)
    $cursor = [IO.Path]::GetFullPath($Path)
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            if ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw 'Capture paths cannot use a symbolic link/reparse point.'
            }
            if (Test-Path -LiteralPath (Join-Path $cursor 'generation.json') -PathType Leaf) {
                throw 'Capture saves host originals, never a generated configuration.'
            }
        }
        $next = Split-Path -Parent $cursor
        if ($next -eq $cursor) { break }
        $cursor = $next
    }
}

function Resolve-WinEnvCaptureDocument {
    param([string] $Environment, [string] $Relative, [string] $ProviderRoot)
    if ([string]::IsNullOrWhiteSpace($Relative) -or [IO.Path]::IsPathRooted($Relative) -or
        $Relative -match '[:\\]' -or ($Relative.Split('/') -contains '..')) {
        throw 'Capture document requires an explicit relative path without traversal.'
    }
    $base = [IO.Path]::GetFullPath((Split-Path -Parent $Environment)).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $path = [IO.Path]::GetFullPath((Join-Path $base $Relative))
    if (-not $path.StartsWith($base + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Capture document escapes its declaration directory.'
    }
    $provider = [IO.Path]::GetFullPath($ProviderRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if ($path -eq $provider -or $path.StartsWith($provider + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Capture cannot write provider source.'
    }
    Assert-WinEnvCapturePath $path
    if ((Test-Path -LiteralPath $path) -and -not (Test-Path -LiteralPath $path -PathType Leaf)) { throw 'Capture document is not a file.' }
    if ($path -eq $Environment) { throw 'Settings document cannot be its own declaration.' }
    return $path
}

function Get-WinEnvCaptureDigest {
    param([string] $Path)
    Assert-WinEnvCapturePath $Path
    if (Test-Path -LiteralPath $Path -PathType Leaf) { return Get-WinEnvFileDigest $Path }
    if (Test-Path -LiteralPath $Path) { throw 'Expected a capture file, not a directory.' }
    return '<absent>'
}

function Read-WinEnvCaptureText {
    param([string] $Path)
    $bytes = [IO.File]::ReadAllBytes($Path)
    $offset = 0
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) { $offset = 3 }
    try { $text = [Text.UTF8Encoding]::new($false,$true).GetString($bytes,$offset,$bytes.Length-$offset) }
    catch { throw 'Observed capture content must be strict UTF-8; unsupported encoding or malformed bytes are refused.' }
    if ($text.Contains([char]0)) { throw 'Observed capture content contains NUL; unsupported text encoding is refused.' }
    return $text
}

function Get-WinEnvHostJsonProjection {
    param($Declared, $Actual, [string] $Path = '')
    $declaredKind = Get-WinEnvJsonValueKind $Declared
    $actualKind = Get-WinEnvJsonValueKind $Actual
    if ($declaredKind -cne $actualKind) { throw "Observed shape differs at '$Path'; capture does not migrate or delete keys." }
    if ($declaredKind -ceq 'object') {
        $result = [ordered]@{}
        foreach ($property in Get-WinEnvObjectProperties $Declared) {
            $actualProperties = @(Get-WinEnvObjectProperties $Actual | Where-Object Name -IEQ $property.Name)
            if ($actualProperties.Count -ne 1) { throw "Observed key missing or ambiguous at '$Path.$($property.Name)'." }
            $result[$property.Name] = Get-WinEnvHostJsonProjection $property.Value $actualProperties[0].Value "$Path.$($property.Name)"
        }
        return $result
    }
    if ($declaredKind -ceq 'list') { return ,@($Actual) }
    return $Actual
}

function Test-WinEnvCaptureContent {
    param([hashtable] $Definition, [string] $Content)
    # Parser inputs are task-owned temporary files, never app/source/originals.
    $temporary = Join-Path ([IO.Path]::GetTempPath()) ('win-env-capture-parser-' + [guid]::NewGuid().ToString('N'))
    try {
        [void][IO.Directory]::CreateDirectory($temporary)
        $testDefinition = @{} + $Definition
        $testDefinition.Source = 'payload'
        [IO.File]::WriteAllText((Join-Path $temporary 'payload'), $Content, [Text.UTF8Encoding]::new($false))
        $reason = Test-WinEnvSourceFile -Definition $testDefinition -RepositoryRoot $temporary
        if ($reason) {
            $error = [InvalidOperationException]::new("Capture parser unavailable: $reason")
            $error.Data['unavailable'] = $true
            throw $error
        }
    }
    finally {
        $payload = Join-Path $temporary 'payload'
        if (Test-Path -LiteralPath $payload -PathType Leaf) { [IO.File]::Delete($payload) }
        if (Test-Path -LiteralPath $temporary -PathType Container) { [IO.Directory]::Delete($temporary) }
    }
}

function Get-WinEnvHostCapturePlan {
    param([Parameter(Mandatory)][string] $SourceRoot, [Parameter(Mandatory)][string] $Environment,
        [Parameter(Mandatory)][string[]] $Unit, [string[]] $Document = @())
    if (-not $Unit.Count -or ($Document.Count -and $Document.Count -ne $Unit.Count)) { throw 'Document paths must align with the explicitly requested Unit IDs.' }
    $plan = Get-WinEnvEnvironmentPlan -Environment $Environment -SourceRoot $SourceRoot
    foreach ($relative in $script:CaptureToolDigests.Keys) {
        if ((Get-WinEnvFileDigest (Join-Path $plan.Source.Root "windows/$relative")) -cne $script:CaptureToolDigests[$relative]) {
            throw 'Capture execution tools differ from the pinned provider; use its own capture entry point.'
        }
    }
    $environmentPath = $plan.Inputs[0].path
    Assert-WinEnvCapturePath $environmentPath
    $provider = $plan.Source.Root.TrimEnd([IO.Path]::DirectorySeparatorChar)
    if ($environmentPath.StartsWith($provider + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Host declaration must be outside provider source.'
    }
    $record = Read-WinEnvContractJson $environmentPath
    $destinations = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $units = [Collections.Generic.List[object]]::new()
    for ($index = 0; $index -lt $Unit.Count; $index++) {
        $id = $Unit[$index]
        if (-not $seen.Add($id)) { throw "Duplicate capture Unit '$id'." }
        $selected = @($plan.Units | Where-Object { $_.Definition.Id -ceq $id })
        if ($selected.Count -ne 1) { throw "Capture unit '$id' must be known, selected and enabled." }
        $definition = $selected[0].Definition
        $connected = $record.units.Contains($id) -and $record.units[$id].Contains('document')
        $relative = if ($connected) { $record.units[$id].document } elseif ($Document.Count) { $Document[$index] } else { $null }
        if ($connected -and $Document.Count -and $Document[$index] -cne $relative) { throw 'Capture cannot rename an existing connection.' }
        $path = Resolve-WinEnvCaptureDocument $environmentPath $relative $plan.Source.Root
        if (-not $destinations.Add($path)) { throw 'Capture destinations must be unique.' }
        foreach ($otherId in $record.units.Keys) {
            if ($otherId -cne $id -and $record.units[$otherId].Contains('document') -and
                (Resolve-WinEnvContractPath (Split-Path -Parent $environmentPath) $record.units[$otherId].document) -eq $path) {
                throw 'Capture destination is already connected to another unit.'
            }
        }
        $resolved = Resolve-WinEnvManagedFile -Definition $definition
        $target = [IO.Path]::GetFullPath((Resolve-WinEnvPath $resolved.Target))
        Assert-WinEnvCapturePath $target
        if ($target -eq $environmentPath -or $target -eq $path -or
            $target.StartsWith($provider + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Capture app target overlaps protected originals/provider.' }
        $item = [pscustomobject]@{ Id=$id; Document=$relative; Path=$path; Target=$target; TargetPattern=$resolved.Target; Connected=$connected;
            Before=(Get-WinEnvCaptureDigest $path); TargetBefore=(Get-WinEnvCaptureDigest $target);
            Payload=$null; Content=$null; Status='prepared'; Reason=$null; Unavailable=$false; Saved=$false; ConnectionSaved=$false }
        try {
            if ($item.TargetBefore -ceq '<absent>' -or (Test-WinEnvRuntimeStatePath $target)) { throw 'Capture target is absent or excluded runtime state.' }
            $actual = Read-WinEnvCaptureText $target
            if ($definition.Compare -ceq 'JsonSubset') {
                $actualJson = Read-WinEnvContractJson $target
                $declaredJson = $selected[0].Content | ConvertFrom-Json -Depth 100
                $actual = Get-WinEnvHostJsonProjection $declaredJson $actualJson | ConvertTo-Json -Depth 100
            }
            elseif ($definition.Compare -ceq 'ExactJsonWithGeneratedProfiles') {
                [void](Read-WinEnvContractJson $target)
                $actual = Remove-WinEnvGeneratedProfile $selected[0].Content $actual
                [void](Test-WinEnvJsonWithGeneratedProfiles -Expected $actual -Actual $actual)
            }
            elseif ($definition.Parser -ceq 'Json') { [void](Read-WinEnvContractJson $target) }
            $restored = ConvertFrom-WinEnvTemplate -Content $actual
            # Host originals are private, so unrepresented private paths are
            # retained as host data rather than forced into provider publication.
            $content = [string]$restored.Content
            Test-WinEnvCaptureContent $definition $content
            $settings = if ($definition.Parser -ceq 'Json') { $content | ConvertFrom-Json -AsHashtable -Depth 100 } else { $content }
            if ($definition.Parser -ceq 'Json' -and $settings -isnot [Collections.IDictionary]) { throw 'Active Json unit requires object settings.' }
            $item.Payload = [ordered]@{ formatVersion=1; source='host'; settings=$settings }
            $item.Content = $item.Payload | ConvertTo-Json -Depth 100
            if ((Get-WinEnvCaptureDigest $target) -cne $item.TargetBefore) { throw 'Observed app target changed during preparation.' }
            if (-not $connected -and $item.Before -cne '<absent>') {
                $orphan = Read-WinEnvContractJson $path
                if ((Get-WinEnvRecordDigest $orphan) -cne (Get-WinEnvRecordDigest $item.Payload)) { throw 'Unconnected document conflicts; capture will not overwrite it.' }
            }
        }
        catch { $item.Status='refused'; $item.Reason=$_.Exception.Message; $item.Unavailable=[bool]$_.Exception.Data['unavailable'] }
        $units.Add($item)
    }
    # Targets cannot alias any original or another unit's pending destination.
    foreach ($item in $units) {
        if ($destinations.Contains($item.Target) -or @($plan.Inputs | Where-Object { $_.path -eq $item.Target }).Count) { throw 'Capture target overlaps a connected original.' }
    }
    return [pscustomobject]@{ SourceRoot=$plan.Source.Root; Commit=$plan.Source.Commit; Environment=$environmentPath;
        Record=$record; Inputs=$plan.Inputs; EnvironmentDigest=$plan.Inputs[0].sha256; Units=$units.ToArray() }
}

function Assert-WinEnvCapturePending {
    param($Plan, [string] $EnvironmentDigest, [hashtable] $Digests)
    [void](Get-WinEnvProviderSource -SourceRoot $Plan.SourceRoot -Commit $Plan.Commit)
    foreach ($relative in $script:CaptureToolDigests.Keys) {
        if ((Get-WinEnvFileDigest (Join-Path $Plan.SourceRoot "windows/$relative")) -cne $script:CaptureToolDigests[$relative]) { throw 'Capture execution tools changed.' }
    }
    if ((Get-WinEnvCaptureDigest $Plan.Environment) -cne $EnvironmentDigest) { throw 'Capture declaration changed since preparation.' }
    foreach ($input in $Plan.Inputs) {
        if ($input.path -eq $Plan.Environment -or $Digests.ContainsKey($input.path)) { continue }
        if ((Get-WinEnvCaptureDigest $input.path) -cne $input.sha256) { throw 'Connected original changed since preparation.' }
    }
    foreach ($item in $Plan.Units) {
        [void](Resolve-WinEnvCaptureDocument $Plan.Environment $item.Document $Plan.SourceRoot)
        if ([IO.Path]::GetFullPath((Resolve-WinEnvPath $item.TargetPattern)) -cne $item.Target) { throw 'Resolved app target changed since preparation.' }
        if ((Get-WinEnvCaptureDigest $item.Target) -cne $item.TargetBefore) { throw 'Observed app target changed since preparation.' }
        if ((Get-WinEnvCaptureDigest $item.Path) -cne $Digests[$item.Path]) { throw 'Capture document changed since preparation.' }
    }
}

function Save-WinEnvHostCapture {
    [CmdletBinding(SupportsShouldProcess)]
    param([Parameter(Mandatory)] $Plan)
    if (@($Plan.Units | Where-Object Status -NE prepared).Count) { return $Plan }
    if (-not $PSCmdlet.ShouldProcess($Plan.Environment, 'Save prepared host unit documents and explicit connections')) { return $Plan }
    $digests = @{}
    foreach ($item in $Plan.Units) { $digests[$item.Path] = $item.Before }
    $environmentDigest = $Plan.EnvironmentDigest
    foreach ($item in $Plan.Units) {
        try {
            Assert-WinEnvCapturePending $Plan $environmentDigest $digests
            if ($item.Connected -or $item.Before -ceq '<absent>') {
                Write-WinEnvCaptureDocument $item.Path $item.Content
                $digests[$item.Path] = Get-WinEnvCaptureDigest $item.Path
            }
            $item.Saved = $true
            if (-not $item.Connected) {
                # No automatic rollback: the validated document remains inert
                # if adding its explicit connection fails.
                Assert-WinEnvCapturePending $Plan $environmentDigest $digests
                $updated = $Plan.Record | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable -Depth 100
                $updated.units[$item.Id] = @{ enabled=$true; document=$item.Document }
                Write-WinEnvCaptureConnection $Plan.Environment ($updated | ConvertTo-Json -Depth 100)
                $Plan.Record = $updated
                $environmentDigest = Get-WinEnvCaptureDigest $Plan.Environment
                $item.ConnectionSaved = $true
            }
            $item.Status = 'saved'
        }
        catch {
            $item.Status = if ($item.Saved -and -not $item.Connected -and -not $item.ConnectionSaved) { 'unconnected' } else { 'failed' }
            $item.Reason = $_.Exception.Message
            break
        }
    }
    foreach ($item in $Plan.Units) { if ($item.Status -ceq 'prepared') { $item.Status='pending' } }
    return $Plan
}

function Write-WinEnvCaptureDocument { param([string] $Path, [string] $Content); Write-WinEnvAtomicText $Path $Content }
function Write-WinEnvCaptureConnection { param([string] $Path, [string] $Content); Write-WinEnvAtomicText $Path $Content }

function ConvertTo-WinEnvHostCapturePreview {
    param($Plan)
    return [ordered]@{ formatVersion=1; provider=@{commit=$Plan.Commit}; environment=$Plan.Environment;
        units=@($Plan.Units | ForEach-Object { [ordered]@{ id=$_.Id; document=$_.Document;
            firstConnection=(-not $_.Connected); payload=$_.Payload; status=$_.Status; reason=$_.Reason;
            unavailable=$_.Unavailable; documentSaved=$_.Saved; connectionSaved=$_.ConnectionSaved } }) }
}
Export-ModuleMember -Function Get-WinEnvHostCapturePlan, Save-WinEnvHostCapture, ConvertTo-WinEnvHostCapturePreview
