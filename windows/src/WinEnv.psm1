Set-StrictMode -Version Latest

# WinGet's documented statuses, as signed 32-bit values because that is what
# $LASTEXITCODE carries: 0x8A150014 APPINSTALLER_CLI_ERROR_NO_APPLICATIONS_FOUND
# and 0x8A15002B APPINSTALLER_CLI_ERROR_UPDATE_NOT_APPLICABLE.
$script:WinGetNoPackageExitCode = -1978335212
$script:WinGetNoApplicableUpdateExitCode = -1978335189
$script:Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

# Every comparison mode a managed file may declare. The manifest is validated
# against this list when it loads, so a misspelled mode names the entry at
# fault instead of reaching a host and failing there as an unknown mode with
# the file already written.
$script:WinEnvComparisonMode = @('Text', 'ExactJson', 'JsonSubset', 'ExactJsonWithGeneratedProfiles')

# The two host queries this domain's detection depends on. They are script-
# scope defaults rather than inline calls so that every outcome, including the
# one a given host cannot produce, has a fixture. Nothing but a test passes
# anything else.
$script:DefaultAppxQuery = { param([string] $PackageName) Get-AppxPackage -Name $PackageName -ErrorAction SilentlyContinue }
$script:DefaultRegistrationQuery = { param([string] $PackageId) Get-WinGetRegistration -Id $PackageId }

function Get-WinEnvManifest {
    param([Parameter(Mandatory)][string] $Path)

    $manifest = Get-Content -LiteralPath $Path -Raw -Encoding utf8 |
        ConvertFrom-Json -AsHashtable -ErrorAction Stop
    if ($manifest.SchemaVersion -ne 4) { throw "Unsupported manifest schema: $($manifest.SchemaVersion)" }
    [void][System.Management.Automation.SemanticVersion]$manifest.ProjectVersion
    # Every consumer reads the manifest through here, so the feature model is
    # validated once instead of separately in setup, the check tool, and tests.
    Assert-WinEnvFeatureModel -Manifest $manifest
    Assert-WinEnvManagedFileModel -Manifest $manifest
    return $manifest
}

function Get-WinEnvFeatureRequires {
    param([Parameter(Mandatory)][hashtable] $Feature)

    if (-not $Feature.ContainsKey('Requires')) { return @() }
    return @($Feature.Requires | ForEach-Object { [string]$_ })
}

function Get-WinEnvFeatureId {
    param([Parameter(Mandatory)][hashtable] $Manifest)

    return @($Manifest.Features | ForEach-Object { [string]$_.Id })
}

function Get-WinEnvRequiredFeatureId {
    param([Parameter(Mandatory)][hashtable] $Manifest)

    return @(
        $Manifest.Features |
            Where-Object { $_.ContainsKey('Required') -and $_.Required } |
            ForEach-Object { [string]$_.Id })
}

function Assert-WinEnvFeatureModel {
    param([Parameter(Mandatory)][hashtable] $Manifest)

    if (-not $Manifest.ContainsKey('Features')) { throw 'The manifest declares no features.' }

    $declared = [System.Collections.Generic.List[string]]::new()
    foreach ($feature in $Manifest.Features) {
        if (-not $feature.ContainsKey('Id')) { throw 'A feature is declared without an Id.' }
        $id = [string]$feature.Id
        if ($declared.Contains($id)) { throw "Feature '$id' is declared more than once." }
        $declared.Add($id)
    }

    if (-not (Get-WinEnvRequiredFeatureId -Manifest $Manifest)) {
        throw 'No feature is declared Required; every selection would deploy nothing.'
    }

    foreach ($feature in $Manifest.Features) {
        foreach ($required in (Get-WinEnvFeatureRequires -Feature $feature)) {
            if (-not $declared.Contains($required)) {
                throw "Feature '$($feature.Id)' requires undeclared feature '$required'."
            }
        }
    }

    # A cycle would make the closure order arbitrary and let a selection report
    # a feature it never resolved.
    foreach ($feature in $Manifest.Features) {
        $start = [string]$feature.Id
        $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
        $queue = [System.Collections.Generic.Queue[string]]::new()
        foreach ($required in (Get-WinEnvFeatureRequires -Feature $feature)) { $queue.Enqueue($required) }
        while ($queue.Count) {
            $id = $queue.Dequeue()
            if ($id -eq $start) { throw "Feature '$start' takes part in a Requires cycle." }
            if (-not $seen.Add($id)) { continue }
            $next = $Manifest.Features | Where-Object { [string]$_.Id -eq $id } | Select-Object -First 1
            foreach ($required in (Get-WinEnvFeatureRequires -Feature $next)) { $queue.Enqueue($required) }
        }
    }

    # Nothing deployable may be unowned: an item without a feature could never
    # be selected, and one naming an undeclared feature would be dropped from
    # every plan without saying so.
    $owned = @()
    foreach ($package in $Manifest.Packages) { $owned += , @('package', [string]$package.Id, $package) }
    foreach ($definition in $Manifest.ManagedFiles) { $owned += , @('managed file', [string]$definition.Id, $definition) }
    $owned += , @('font', [string]$Manifest.Font.Name, $Manifest.Font)
    $owned += , @('terminal delegation', 'Terminal', $Manifest.Terminal)

    foreach ($entry in $owned) {
        $kind, $name, $item = $entry
        if (-not $item.ContainsKey('Feature')) { throw "The $kind '$name' declares no Feature." }
        $feature = [string]$item.Feature
        if (-not $declared.Contains($feature)) {
            throw "The $kind '$name' names undeclared feature '$feature'."
        }
    }

    foreach ($feature in $Manifest.Features) {
        if ($feature.ContainsKey('Lifecycle') -and [string]$feature.Lifecycle -ne 'PowerToys') {
            throw "Feature '$($feature.Id)' declares unknown lifecycle '$($feature.Lifecycle)'."
        }
    }

    foreach ($package in $Manifest.Packages) {
        if ($package.ContainsKey('Bootstrap') -and $package.Bootstrap -and
            (Get-WinEnvRequiredFeatureId -Manifest $Manifest) -notcontains [string]$package.Feature) {
            throw "Package '$($package.Id)' bootstraps this host but is not owned by a required feature."
        }
    }
}

function Assert-WinEnvManagedFileModel {
    <#
        .SYNOPSIS
        Validate the declared shape of every managed file.

        .DESCRIPTION
        A managed file declares how it is compared and which sources it may
        deploy, and both are validated here so a mistake in either names the
        entry at fault while the manifest loads.

        Comparison is one mode per entry rather than a mode plus a set of
        per-entry tolerances. A tolerance that could be attached to any mode
        would have combinations nothing implements -- a text file with a JSON
        profile rule -- and each would read as meaningful and do nothing.
        `ExactJsonWithGeneratedProfiles` reads its payload as JSON, so an
        entry whose parser is not `Json` is declaring a mode that cannot apply
        to it.

        Schema 3 lets one managed file declare alternative sources selected by
        the host's Windows build. One entry was chosen over two mutually
        exclusive entries because it keeps one Id, one Target, one Compare mode
        and one owning feature, so drift, backup and deselection continue to
        reason about one logical file.

        Two entries would have needed an invariant nothing here enforces:
        exactly one of them must select on any host. Conditions that overlapped
        would deploy twice, conditions that all failed would deploy nothing,
        and neither failure is visible in the file the manifest declares. This
        shape makes that invariant structural instead. An ordered list whose
        bounds descend strictly and whose last variant carries no condition
        makes resolution a total function, and this assertion is what keeps the
        list in that shape.
    #>
    param([Parameter(Mandatory)][hashtable] $Manifest)

    foreach ($definition in $Manifest.ManagedFiles) {
        $id = [string]$definition.Id

        $compare = if ($definition.ContainsKey('Compare')) { [string]$definition.Compare } else { '' }
        if ($script:WinEnvComparisonMode -cnotcontains $compare) {
            throw ("The managed file '$id' declares unknown comparison mode '$compare'; " +
                "the modes are: $($script:WinEnvComparisonMode -join ', ').")
        }
        if ($compare -ceq 'ExactJsonWithGeneratedProfiles') {
            $parser = if ($definition.ContainsKey('Parser')) { [string]$definition.Parser } else { '' }
            if ($parser -cne 'Json') {
                throw ("The managed file '$id' declares comparison mode '$compare' with parser '$parser'; " +
                    'that mode reads both sides as JSON and can only be declared on a Json payload.')
            }
        }

        $hasSource = $definition.ContainsKey('Source')
        $hasSources = $definition.ContainsKey('Sources')
        if ($hasSource -and $hasSources) {
            throw "The managed file '$id' declares both Source and Sources."
        }
        if (-not $hasSource -and -not $hasSources) {
            throw "The managed file '$id' declares no Source."
        }
        if (-not $hasSources) { continue }

        $variants = @($definition.Sources)
        if ($variants.Count -lt 2) {
            throw "The managed file '$id' declares fewer than two source variants; use a scalar Source."
        }

        $previousBound = $null
        for ($index = 0; $index -lt $variants.Count; $index++) {
            $variant = $variants[$index]
            # A variant chooses a payload and nothing else. Every other field
            # -- Compare, Parser, Feature, Target -- stays on the entry, which
            # is what keeps two payloads one logical file. Accepting an unknown
            # key would let a per-variant Compare or Feature read as meaningful
            # and do nothing, because New-ResolvedManagedFile copies those from
            # the entry alone.
            foreach ($key in $variant.Keys) {
                if (@('Source', 'MinimumBuild') -notcontains [string]$key) {
                    throw "A source variant of the managed file '$id' declares unknown key '$key'."
                }
            }
            if (-not $variant.ContainsKey('Source')) {
                throw "A source variant of the managed file '$id' declares no Source."
            }
            # Caught here rather than as 'Managed source is missing: <root>' from
            # check-desired-state.ps1, which names a path that is really the
            # desired-state root and says nothing about the entry at fault.
            if ([string]::IsNullOrWhiteSpace([string]$variant.Source)) {
                throw "A source variant of the managed file '$id' declares an empty Source."
            }

            $isLast = $index -eq $variants.Count - 1
            $hasBound = $variant.ContainsKey('MinimumBuild')
            if ($isLast -and $hasBound) {
                throw ("The last source variant of the managed file '$id' declares MinimumBuild; " +
                    'it must be unconditional so every host resolves to exactly one variant.')
            }
            if (-not $isLast -and -not $hasBound) {
                throw ("A source variant of the managed file '$id' declares no MinimumBuild and is not last; " +
                    'only the last variant may be unconditional.')
            }
            if (-not $hasBound) { continue }

            $bound = 0
            if (-not [int]::TryParse([string]$variant.MinimumBuild, [ref]$bound) -or $bound -le 0) {
                throw "The managed file '$id' declares a MinimumBuild that is not a positive Windows build number."
            }
            if ($null -ne $previousBound -and $bound -ge $previousBound) {
                throw ("The managed file '$id' declares MinimumBuild values that do not descend; " +
                    'the first variant a host satisfies must be the highest bound it meets.')
            }
            $previousBound = $bound
        }
    }
}

function Get-WinEnvFeatureSelection {
    param(
        [Parameter(Mandatory)][hashtable] $Manifest,
        [AllowEmptyCollection()][string[]] $Requested = @()
    )

    $declared = Get-WinEnvFeatureId -Manifest $Manifest
    $required = Get-WinEnvRequiredFeatureId -Manifest $Manifest
    $asked = @($Requested | Where-Object { $_ } | ForEach-Object { [string]$_ })
    foreach ($id in $asked) {
        if ($declared -notcontains $id) {
            throw "Unknown feature '$id'. The manifest declares: $($declared -join ', ')."
        }
    }

    $resolved = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $queue = [System.Collections.Generic.Queue[string]]::new()
    # Both operands are wrapped: PowerShell unrolls a single-element array on
    # return, and 'core' + @('terminal') concatenates into one string.
    foreach ($id in (@($required) + @($asked))) { $queue.Enqueue($id) }
    while ($queue.Count) {
        $id = $queue.Dequeue()
        if (-not $resolved.Add($id)) { continue }
        $feature = $Manifest.Features | Where-Object { [string]$_.Id -eq $id } | Select-Object -First 1
        foreach ($next in (Get-WinEnvFeatureRequires -Feature $feature)) { $queue.Enqueue($next) }
    }

    # Manifest order, not resolution order, so a plan, its summary, and the
    # recorded state read the same on every host.
    $selected = @($declared | Where-Object { $resolved.Contains($_) })

    return [pscustomobject]@{
        Selected  = $selected
        Requested = $asked
        Implied   = @($selected | Where-Object { $asked -notcontains $_ -and $required -notcontains $_ })
        Excluded  = @($declared | Where-Object { -not $resolved.Contains($_) })
    }
}

function Expand-WinEnvFeatureArgument {
    # bootstrap.ps1 hands its arguments to pwsh with -File, where every value
    # arrives as one literal string. Splitting here lets 'a,b' from that entry
    # point and -Feature a,b from a direct call mean the same thing.
    param([AllowEmptyCollection()][string[]] $Value)

    if ($null -eq $Value) { return @() }
    return @($Value | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

function Get-WinEnvRequestedFeature {
    param(
        [Parameter(Mandatory)][hashtable] $Manifest,
        [AllowEmptyCollection()][string[]] $Applied = @(),
        [bool] $HasState = $false,
        [string[]] $Feature,
        [string[]] $Add,
        [switch] $Minimal,
        [switch] $All
    )

    $selectors = @()
    if ($null -ne $Feature) { $selectors += '-Feature' }
    if ($null -ne $Add) { $selectors += '-Add' }
    if ($Minimal) { $selectors += '-Minimal' }
    if ($All) { $selectors += '-All' }
    if ($selectors.Count -gt 1) {
        throw "Supply one selection at a time; $($selectors -join ' and ') describe different selections."
    }

    if ($Minimal) { return @() }
    if ($All) { return (Get-WinEnvFeatureId -Manifest $Manifest) }
    if ($null -ne $Feature) { return (Expand-WinEnvFeatureArgument -Value $Feature) }
    if ($null -ne $Add) { return (@($Applied) + @(Expand-WinEnvFeatureArgument -Value $Add)) }
    # No selection given: an applied host keeps what it recorded, and a host
    # that has never applied takes everything, which is what this repository
    # deployed before selection existed.
    if ($HasState) { return @($Applied) }
    return (Get-WinEnvFeatureId -Manifest $Manifest)
}

function Get-WinEnvAppliedFeature {
    param(
        [Parameter(Mandatory)][hashtable] $Manifest,
        $State
    )

    if (-not $State) { return @() }
    # A schema 1 state predates selection and was therefore written by a full
    # deployment. Reading it as the complete feature set keeps an already
    # applied host on exactly what it already has.
    if (-not $State.PSObject.Properties['features']) { return (Get-WinEnvFeatureId -Manifest $Manifest) }
    return @($State.features | ForEach-Object { [string]$_ })
}

function Get-WinEnvAppxPresence {
    # One capability probe for every Appx question this domain asks. It has
    # three answers: the module answered and the package is there, the module
    # answered and it is not, or the module could not be loaded and presence is
    # not knowable by this route.
    #
    # The third answer is why this exists. PowerShell 7 fails while autoloading
    # the Appx module on hosts whose Windows build only offers it through the
    # compatibility layer, so the error is raised during command discovery,
    # before Get-AppxPackage runs; -ErrorAction cannot suppress what was never
    # bound, and only a try/catch sees it. That is a prerequisite the host
    # cannot supply, which docs/architecture.md calls unverified. It is not
    # evidence of absence, and reporting it as absence is wrong in both
    # directions. Read Usable before Present: Present is $null when the module
    # did not answer, so absence is not representable in that case.
    #
    # This asks whether Appx works, never which Windows this is. A capability
    # question keeps its meaning when Microsoft changes which builds ship the
    # module; a build comparison does not.
    # Position is declared so the query seam cannot be bound positionally by
    # accident; once one parameter has an explicit position the rest are
    # name-only.
    param(
        [Parameter(Mandatory, Position = 0)][string] $Name,
        [scriptblock] $Query = $script:DefaultAppxQuery
    )

    try {
        $package = & $Query $Name
        return [pscustomobject]@{
            Name    = $Name
            Usable  = $true
            Present = [bool]$package
            Reason  = $null
        }
    }
    catch {
        return [pscustomobject]@{
            Name    = $Name
            Usable  = $false
            Present = $null
            Reason  = $_.Exception.Message
        }
    }
}

function Test-WinEnvFeaturePrecondition {
    # Returns the two answers separately, because they rank differently: a
    # failure blocks an Apply, an unverified precondition only says this host
    # could not decide it. An unknown precondition type still throws, since an
    # undeclared type is a broken manifest rather than an undecidable host.
    param(
        [Parameter(Mandatory, Position = 0)][hashtable] $Feature,
        [scriptblock] $AppxQuery = $script:DefaultAppxQuery
    )

    $failures = [System.Collections.Generic.List[string]]::new()
    $unverified = [System.Collections.Generic.List[string]]::new()
    if ($Feature.ContainsKey('Preconditions')) {
        foreach ($precondition in $Feature.Preconditions) {
            switch ([string]$precondition.Type) {
                'Appx' {
                    $probe = Get-WinEnvAppxPresence -Name $precondition.Name -Query $AppxQuery
                    if (-not $probe.Usable) {
                        $unverified.Add("$($precondition.Name) Appx presence is undecidable on this host: $($probe.Reason)")
                    }
                    elseif (-not $probe.Present) {
                        $failures.Add("$($precondition.Name) Appx is missing; $($precondition.Message)")
                    }
                }
                default { throw "Unknown precondition type '$($precondition.Type)'." }
            }
        }
    }

    return [pscustomobject]@{
        Failures   = $failures.ToArray()
        Unverified = $unverified.ToArray()
    }
}

function Get-WinEnvCheckStatus {
    # The run's status contract, in one place so the ranking is stated rather
    # than implied by the order of a few exits.
    #
    #   0   nothing drifted and everything was decided
    #   1   something could not be decided and native evidence was required
    #   2   something drifted
    #   69  nothing drifted and something could not be decided here
    #
    # Ranking: a failure outranks everything, per docs/architecture.md, which
    # is the whole effect of RequireNative; then drift outranks unverified.
    # -Check exists to answer whether an Apply is needed, and drift is a
    # positive answer to that question while an undecidable item is not, so a
    # known 2 is never collapsed into a 69, and 69 is reserved for a run whose
    # only open item could not be decided here. The cost is written down
    # because it is real: on a host with both, the status alone does not say
    # the check was also incomplete, which is why the caller always names the
    # undecided items in its summary.
    param(
        [Parameter(Mandatory)][int] $DriftCount,
        [Parameter(Mandatory)][int] $UnverifiedCount,
        # CI sets REQUIRE_NATIVE so the merge gate never accepts an item nobody
        # could decide; hosts and hooks leave it unset so a host that cannot
        # decide one is not blocked.
        [switch] $RequireNative
    )

    if ($RequireNative -and $UnverifiedCount -gt 0) { return 1 }
    if ($DriftCount -gt 0) { return 2 }
    if ($UnverifiedCount -gt 0) { return 69 }
    return 0
}

function Compare-WinEnvVersion {
    param(
        [Parameter(Mandatory)][string] $RepositoryVersion,
        [Parameter(Mandatory)][string] $AppliedVersion
    )

    $repository = [System.Management.Automation.SemanticVersion]$RepositoryVersion
    $applied = [System.Management.Automation.SemanticVersion]$AppliedVersion
    return $repository.CompareTo($applied)
}

function Get-WinEnvWindowsBuild {
    <#
        .SYNOPSIS
        This host's Windows build number, or $null when it cannot be
        determined.

        .DESCRIPTION
        The build is the discriminator and the major version is never used:
        [Environment]::OSVersion.Version.Major is 10 on Windows 10 and on
        Windows 11 alike, so a major-version comparison silently classifies
        every Windows 11 host as Windows 10. Windows 11 begins at build 22000.

        The build is read in process rather than from WMI or the registry,
        either of which can be unavailable on a host that is otherwise fine.
        PowerShell 7 runs on .NET 5 or newer, where OSVersion comes from
        RtlGetVersion and is not capped by the Win32 compatibility-manifest
        shim, so the number returned is the host's real build.

        Only the build is returned. A revision (UBR) is a servicing level
        rather than an OS version, this source carries none, and comparing one
        would classify a host that is merely behind on cumulative updates as
        below a bound its Windows version meets.
    #>

    $os = [Environment]::OSVersion
    if ($os.Platform -ne [System.PlatformID]::Win32NT) { return $null }
    $build = $os.Version.Build
    if ($build -le 0) { return $null }
    return [int]$build
}

# Private, like Get-WinGetRegistration: a definition copy carrying a scalar
# Source is an implementation detail of the two resolvers below, not part of
# this module's contract.
function New-ResolvedManagedFile {
    param(
        [Parameter(Mandatory, Position = 0)][hashtable] $Definition,
        [Parameter(Mandatory)][string] $Source
    )

    $resolved = @{}
    foreach ($key in $Definition.Keys) { $resolved[$key] = $Definition[$key] }
    [void]$resolved.Remove('Sources')
    $resolved['Source'] = $Source
    return $resolved
}

function Get-WinEnvManagedFileVariant {
    <#
        .SYNOPSIS
        Every declared source variant of one managed file, in declaration
        order, each as a definition carrying a scalar Source.

        .DESCRIPTION
        For the consumers that must see all of a file's payloads rather than
        the one this host deploys: the desired-state hash, so the hash never
        depends on the build of the host that computed it, and
        check-desired-state.ps1, so the merge gate parses a payload that is
        never the local answer.
    #>
    param([Parameter(Mandatory, Position = 0)][hashtable] $Definition)

    if (-not $Definition.ContainsKey('Sources')) { return , @($Definition) }
    return @(
        foreach ($variant in $Definition.Sources) {
            New-ResolvedManagedFile -Definition $Definition -Source ([string]$variant.Source)
        })
}

function Resolve-WinEnvManagedFile {
    <#
        .SYNOPSIS
        The single source variant this host deploys, as a definition carrying a
        scalar Source.

        .DESCRIPTION
        The conditional shape is collapsed here and nowhere else, so parsing,
        drift comparison, backup and the write itself keep taking a definition
        with a scalar Source exactly as they did under schema 2.

        Build arrives as data. This is deliberately not the capability seam the
        Appx probe uses: whether the Appx module loads is a question a probe can
        put to the host directly, while no probe can ask whether the WSL VM
        honours a .wslconfig key, because the file is read only after a restart
        this domain does not perform and an unhonoured key is ignored in
        silence. Two mechanisms, one motivation, and neither routes through the
        other.

        A $null build selects the unconditional last variant. That is the
        documented behaviour rather than an arbitrary default: it is the only
        variant every supported build honours, so a key is never deployed to a
        host that was not shown to honour it.
    #>
    param(
        [Parameter(Mandatory, Position = 0)][hashtable] $Definition,
        [AllowNull()][object] $Build = (Get-WinEnvWindowsBuild)
    )

    if (-not $Definition.ContainsKey('Sources')) { return $Definition }

    $chosen = $null
    foreach ($variant in $Definition.Sources) {
        if (-not $variant.ContainsKey('MinimumBuild')) { $chosen = $variant; break }
        if ($null -ne $Build -and [int]$Build -ge [int]$variant.MinimumBuild) { $chosen = $variant; break }
    }

    # Unreachable for a manifest that loaded, because
    # Assert-WinEnvManagedFileModel requires the last variant to be
    # unconditional. Kept so a synthetic definition that never reached the
    # loader fails loudly instead of deploying nothing.
    if (-not $chosen) {
        throw "No source variant of the managed file '$($Definition.Id)' applies to this host."
    }

    return New-ResolvedManagedFile -Definition $Definition -Source ([string]$chosen.Source)
}

function Get-WinEnvDesiredStateHash {
    param(
        [Parameter(Mandatory)][string] $Root,
        [Parameter(Mandatory)][hashtable] $Manifest,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]] $Feature
    )

    # Scoped to what this host deploys. Hashing the whole tree made an edit to
    # a payload the host never selected look like drift and forced an Apply
    # that could not change anything. The manifest is always included: it
    # carries the font hashes, the terminal GUIDs, and the feature model, none
    # of which have a payload file of their own.
    $resolvedRoot = [System.IO.Path]::GetFullPath($Root)
    $relatives = [System.Collections.Generic.SortedSet[string]]::new([System.StringComparer]::Ordinal)
    [void]$relatives.Add('manifest.json')
    foreach ($definition in $Manifest.ManagedFiles) {
        if ($Feature -notcontains [string]$definition.Feature) { continue }
        # Every declared variant, not the one this host resolved. A
        # host-dependent hash would make two hosts of different build classes
        # disagree about the same desired state, and a host that crossed a
        # build bound would report drift no Apply could clear.
        foreach ($variant in (Get-WinEnvManagedFileVariant -Definition $definition)) {
            [void]$relatives.Add(([string]$variant.Source).Replace('\', '/'))
        }
    }

    $entries = foreach ($relative in $relatives) {
        $path = Join-Path $resolvedRoot $relative
        $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        "$relative`0$hash"
    }
    $bytes = $script:Utf8NoBom.GetBytes(($entries -join "`n"))
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
}

function Resolve-WinEnvPath {
    param([Parameter(Mandatory)][string] $Path)

    return $Path.Replace('{LOCALAPPDATA}', $env:LOCALAPPDATA).Replace('{APPDATA}', $env:APPDATA).Replace('{USERPROFILE}', $env:USERPROFILE)
}

function Expand-WinEnvTemplate {
    param([Parameter(Mandatory)][string] $Content)

    $jsonLocalAppData = $env:LOCALAPPDATA.Replace('\', '\\')
    return $Content.Replace('__LOCALAPPDATA_JSON__', $jsonLocalAppData)
}

function Get-WinEnvState {
    param([Parameter(Mandatory)][string] $Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        $state = Get-Content -LiteralPath $Path -Raw -Encoding utf8 | ConvertFrom-Json -ErrorAction Stop
        if ($state.schemaVersion -ne 1 -and $state.schemaVersion -ne 2) { throw 'Unsupported state schema.' }
        # Schema 1 recorded no selection because none existed; it is read as a
        # full deployment rather than rejected.
        if ($state.schemaVersion -eq 2) {
            if (-not $state.PSObject.Properties['features']) { throw 'Missing features.' }
            if (-not @($state.features).Count) { throw 'Empty features.' }
        }
        [void][System.Management.Automation.SemanticVersion]$state.projectVersion
        if ([string]::IsNullOrWhiteSpace($state.appliedAtUtc)) { throw 'Missing appliedAtUtc.' }
        if ([string]::IsNullOrWhiteSpace($state.gitCommit)) { throw 'Missing gitCommit.' }
        if ($state.PSObject.Properties['fontRegisteredAtUtc'] -and -not [string]::IsNullOrWhiteSpace($state.fontRegisteredAtUtc)) {
            [void][DateTimeOffset]::Parse($state.fontRegisteredAtUtc)
        }
        if ($state.PSObject.Properties['bundleHash'] -and $state.bundleHash -notmatch '^[0-9a-f]{64}$') {
            throw 'Invalid bundleHash.'
        }
        return $state
    }
    catch {
        throw "State file '$Path' is invalid: $($_.Exception.Message)"
    }
}

function Write-WinEnvAtomicText {
    param(
        [Parameter(Mandatory)][string] $Path,
        [Parameter(Mandatory)][AllowEmptyString()][string] $Content
    )

    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory)) { [void](New-Item -ItemType Directory -Path $directory -Force) }
    $temporary = Join-Path $directory ('.win-env-{0}.tmp' -f [guid]::NewGuid().ToString('N'))
    try {
        [System.IO.File]::WriteAllText($temporary, $Content, $script:Utf8NoBom)
        if (Test-Path -LiteralPath $Path) {
            [System.IO.File]::Move($temporary, $Path, $true)
        }
        else {
            [System.IO.File]::Move($temporary, $Path)
        }
    }
    finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
    }
}

function Write-WinEnvState {
    param(
        [Parameter(Mandatory)][string] $Path,
        [Parameter(Mandatory)][string] $ProjectVersion,
        [Parameter(Mandatory)][string] $GitCommit,
        [Parameter(Mandatory)][string] $DesiredStateHash,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]] $Feature,
        [string] $FontRegisteredAtUtc
    )

    $state = [ordered]@{
        schemaVersion  = 2
        projectVersion = $ProjectVersion
        # The selected feature set is host state, not desired state: the
        # manifest declares what exists, this file records how much of it this
        # host deployed.
        features       = @($Feature)
        appliedAtUtc   = [DateTimeOffset]::UtcNow.ToString('o')
        gitCommit      = $GitCommit
        # Retain the state key for compatibility with already-applied state.
        bundleHash     = $DesiredStateHash
    }
    if (-not [string]::IsNullOrWhiteSpace($FontRegisteredAtUtc)) {
        $state.fontRegisteredAtUtc = $FontRegisteredAtUtc
    }
    Write-WinEnvAtomicText -Path $Path -Content ($state | ConvertTo-Json -Depth 5)
}

function Get-WinEnvGitCommit {
    param([Parameter(Mandatory)][string] $RepositoryRoot)

    $gitDirectory = Join-Path $RepositoryRoot '.git'
    $head = $null
    if (Test-Path -LiteralPath $gitDirectory -PathType Leaf) {
        $gitFile = Get-Content -LiteralPath $gitDirectory -Raw
        if ($gitFile -match '^gitdir:\s*(.+)\s*$') {
            $candidate = $matches[1]
            $gitDirectory = if ([System.IO.Path]::IsPathRooted($candidate)) { $candidate } else { Join-Path $RepositoryRoot $candidate }
        }
    }
    if (Test-Path -LiteralPath $gitDirectory -PathType Container) {
        $head = (Get-Content -LiteralPath (Join-Path $gitDirectory 'HEAD') -Raw).Trim()
        if ($head -match '^ref:\s+(.+)$') {
            $reference = $matches[1]
            $referencePath = Join-Path $gitDirectory ($reference.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
            if (Test-Path -LiteralPath $referencePath -PathType Leaf) {
                $head = (Get-Content -LiteralPath $referencePath -Raw).Trim()
            }
            else {
                $packedRefs = Join-Path $gitDirectory 'packed-refs'
                if (Test-Path -LiteralPath $packedRefs -PathType Leaf) {
                    $packed = Get-Content -LiteralPath $packedRefs | Where-Object { $_ -match "^([0-9a-fA-F]{40,64})\s+$([regex]::Escape($reference))$" } | Select-Object -First 1
                    if ($packed -and $packed -match '^([0-9a-fA-F]{40,64})') { $head = $matches[1] }
                }
            }
        }
        if ($head -match '^[0-9a-fA-F]{40,64}$') { return $head.ToLowerInvariant() }
    }
    if ($head -match '^ref:\s+') { return 'unborn' }

    $git = Get-Command git.exe, git -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $git) { throw 'Git is required to record the applied commit.' }
    $commit = (& $git.Source -C $RepositoryRoot rev-parse HEAD 2>$null | Select-Object -First 1)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($commit)) { throw 'Unable to resolve the repository Git commit.' }
    return $commit.Trim()
}

function Enter-WinEnvLock {
    $sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $mutex = [System.Threading.Mutex]::new($false, "Local\win-env-setup-$sid")
    try {
        if (-not $mutex.WaitOne(0)) {
            $mutex.Dispose()
            throw 'Another win-env setup is already running for this user.'
        }
    }
    catch [System.Threading.AbandonedMutexException] {
        Write-Warning 'Recovered an abandoned win-env setup lock.'
    }
    return $mutex
}

function Exit-WinEnvLock {
    param([Parameter(Mandatory)] $Mutex)
    try { $Mutex.ReleaseMutex() } finally { $Mutex.Dispose() }
}

function Get-WinGetRegistration {
    param([Parameter(Mandatory)][string] $Id)

    $null = & winget.exe list --id $Id --exact --source winget --accept-source-agreements --disable-interactivity 2>&1
    if ($LASTEXITCODE -eq 0) { return $true }
    if ($LASTEXITCODE -eq $script:WinGetNoPackageExitCode) { return $false }
    throw "WinGet failed while detecting '$Id' (exit $LASTEXITCODE)."
}

function Get-WinEnvPackageStatus {
    param(
        [Parameter(Mandatory, Position = 0)][hashtable] $Package,
        [scriptblock] $AppxQuery = $script:DefaultAppxQuery,
        [scriptblock] $RegistrationQuery = $script:DefaultRegistrationQuery
    )

    $registered = & $RegistrationQuery $Package.Id
    $detected = $registered
    $unverified = $null
    switch ($Package.Detection) {
        'Command' { $detected = [bool](Get-Command $Package.Command -ErrorAction SilentlyContinue) }
        'Appx' {
            # When the module cannot answer, $detected keeps the registration
            # this host could establish. Two consequences are deliberate. There
            # is no conflict, because a comparison needs two answers and only
            # one arrived. And the package is reported missing only when WinGet
            # itself says so, which is the claim a WinGet-detected package
            # already makes; the silent second source is reported as unverified
            # instead of being read as absence.
            $probe = Get-WinEnvAppxPresence -Name $Package.AppxName -Query $AppxQuery
            if ($probe.Usable) { $detected = $probe.Present }
            else { $unverified = "$($Package.AppxName) Appx presence is undecidable on this host: $($probe.Reason)" }
        }
        'WinGet' { $detected = $registered }
        default { throw "Unknown detection method '$($Package.Detection)'." }
    }

    [pscustomobject]@{
        Name       = $Package.Name
        Id         = $Package.Id
        Registered = $registered
        Detected   = $detected
        Conflict   = ($registered -ne $detected)
        Missing    = (-not $registered -and -not $detected)
        Unverified = $unverified
    }
}

function Install-WinEnvPackage {
    param([Parameter(Mandatory, Position = 0)][hashtable] $Package)

    & winget.exe install --id $Package.Id --exact --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity
    if ($LASTEXITCODE -eq 0) { return }
    # WinGet answering "already installed, no applicable update" is the install
    # succeeding at what it was for, not a failed one. It happens when the host
    # has the package by a route this domain's registration query does not see,
    # which a Store-installed application on a host whose Appx module will not
    # load can reach: detection could not decide, WinGet's own source reported
    # nothing, and the item was recorded missing. Aborting the whole Apply
    # there would stop a run mid-deployment over a package that is present.
    if ($LASTEXITCODE -eq $script:WinGetNoApplicableUpdateExitCode) {
        Write-Warning "'$($Package.Id)' is already installed by a route WinGet's configured source does not report; nothing was installed."
        return
    }
    throw "Installation of '$($Package.Id)' failed (exit $LASTEXITCODE)."
}

function Update-WinEnvProcessPath {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machinePath;$userPath"
}

function Test-WinEnvDirectWriteFont {
    param([Parameter(Mandatory)][string] $FamilyName)

    if (-not ('WinEnv.DirectWriteFontProbe' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

namespace WinEnv
{
    public static class DirectWriteFontProbe
    {
        [ComImport]
        [Guid("B859EE5A-D838-4B5B-A2E8-1ADC7D93DB48")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface IDWriteFactory
        {
            void GetSystemFontCollection(out IDWriteFontCollection collection, [MarshalAs(UnmanagedType.Bool)] bool checkForUpdates);
        }

        [ComImport]
        [Guid("A84CEE02-3EEA-4EEE-A827-87C1A02A0FCC")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface IDWriteFontCollection
        {
            uint GetFontFamilyCount();
            void GetFontFamily(uint index, out IntPtr family);
            void FindFamilyName([MarshalAs(UnmanagedType.LPWStr)] string familyName, out uint index, [MarshalAs(UnmanagedType.Bool)] out bool exists);
        }

        [DllImport("dwrite.dll", PreserveSig = true)]
        private static extern int DWriteCreateFactory(uint factoryType, ref Guid iid, [MarshalAs(UnmanagedType.IUnknown)] out object factory);

        public static bool Contains(string familyName)
        {
            Guid iid = typeof(IDWriteFactory).GUID;
            object factoryObject;
            int result = DWriteCreateFactory(0, ref iid, out factoryObject);
            if (result < 0) Marshal.ThrowExceptionForHR(result);

            IDWriteFactory factory = (IDWriteFactory)factoryObject;
            IDWriteFontCollection collection = null;
            try
            {
                factory.GetSystemFontCollection(out collection, true);
                uint index;
                bool exists;
                collection.FindFamilyName(familyName, out index, out exists);
                return exists;
            }
            finally
            {
                if (collection != null) Marshal.ReleaseComObject(collection);
                Marshal.ReleaseComObject(factory);
            }
        }
    }
}
'@
    }

    return [WinEnv.DirectWriteFontProbe]::Contains($FamilyName)
}

function Test-WinEnvWindowsTerminalFontCache {
    param([string] $FontRegisteredAtUtc)

    if ([string]::IsNullOrWhiteSpace($FontRegisteredAtUtc)) { return $true }
    $registeredAt = [DateTimeOffset]::Parse($FontRegisteredAtUtc).UtcDateTime
    foreach ($terminal in @(Get-Process -Name WindowsTerminal -ErrorAction SilentlyContinue)) {
        try {
            if ($terminal.StartTime.ToUniversalTime() -lt $registeredAt) { return $false }
        }
        catch {
            return $false
        }
    }
    return $true
}

function Get-WinEnvFontStatus {
    param([Parameter(Mandatory)][hashtable] $Font)

    $fontDirectory = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
    $registryPath = 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'
    $registry = if (Test-Path $registryPath) { Get-ItemProperty -Path $registryPath } else { $null }
    $systemRegistryPath = 'HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'
    $systemRegistry = if (Test-Path $systemRegistryPath) { Get-ItemProperty -Path $systemRegistryPath } else { $null }
    $systemFamilyDetected = [bool]($systemRegistry -and ($systemRegistry.PSObject.Properties.Name | Where-Object { $_ -like "$($Font.Name)*" }))
    $validFiles = 0
    $validRegistrations = 0
    $artifacts = 0
    foreach ($fontFile in $Font.Files) {
        $path = Join-Path $fontDirectory $fontFile.FileName
        $filePresent = Test-Path -LiteralPath $path -PathType Leaf
        $property = if ($registry) { $registry.PSObject.Properties[$fontFile.RegistryName] } else { $null }
        if ($filePresent -or $property) { $artifacts++ }
        if (-not $filePresent) { continue }

        $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($hash -ne $fontFile.Sha256) { continue }
        $validFiles++
        if ($property -and [string]$property.Value -ieq $path) { $validRegistrations++ }
    }

    $directWriteDetected = Test-WinEnvDirectWriteFont -FamilyName $Font.Name
    $registered = $systemFamilyDetected -or $validRegistrations -eq $Font.Files.Count
    $installed = $registered -and $directWriteDetected
    $registrationRepairable = -not $systemFamilyDetected -and $validFiles -eq $Font.Files.Count -and $validRegistrations -ne $Font.Files.Count
    $conflict = -not $installed -and -not $registrationRepairable -and ($artifacts -gt 0 -or $systemFamilyDetected)
    [pscustomobject]@{
        Installed              = $installed
        Missing                = (-not $installed -and -not $registrationRepairable -and -not $conflict)
        Conflict               = $conflict
        RegistrationRepairable = $registrationRepairable
        DirectWriteDetected     = $directWriteDetected
    }
}

function Register-WinEnvFont {
    param([Parameter(Mandatory)][hashtable] $Font)

    $fontDirectory = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
    $registryPath = 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'
    if (-not (Test-Path $registryPath)) { [void](New-Item -Path $registryPath -Force) }

    if (-not ('WinEnv.NativeFont' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

namespace WinEnv
{
    public static class NativeFont
    {
        [DllImport("gdi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        public static extern int AddFontResourceEx(string fileName, uint flags, IntPtr reserved);

        [DllImport("user32.dll", SetLastError = true)]
        public static extern IntPtr SendMessageTimeout(IntPtr window, uint message, UIntPtr wParam, IntPtr lParam, uint flags, uint timeout, out UIntPtr result);
    }
}
'@
    }

    foreach ($fontFile in $Font.Files) {
        $path = Join-Path $fontDirectory $fontFile.FileName
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Font file is missing: $path" }
        $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($hash -ne $fontFile.Sha256) { throw "Font file hash mismatch for $($fontFile.FileName)." }
        Set-ItemProperty -Path $registryPath -Name $fontFile.RegistryName -Value $path -Type String
        if ([WinEnv.NativeFont]::AddFontResourceEx($path, 0, [IntPtr]::Zero) -eq 0) {
            throw "Windows could not load font file '$path'."
        }
    }

    $result = [UIntPtr]::Zero
    [void][WinEnv.NativeFont]::SendMessageTimeout([IntPtr]0xffff, 0x001D, [UIntPtr]::Zero, [IntPtr]::Zero, 0x0002, 5000, [ref]$result)
}

function Install-WinEnvFont {
    param([Parameter(Mandatory)][hashtable] $Font)

    $temporaryDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ('win-env-font-' + [guid]::NewGuid().ToString('N'))
    [void](New-Item -ItemType Directory -Path $temporaryDirectory)
    try {
        $archive = Join-Path $temporaryDirectory 'font.zip'
        Invoke-WebRequest -Uri $Font.Url -OutFile $archive
        $archiveHash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($archiveHash -ne $Font.Sha256) { throw "Font archive hash mismatch: $archiveHash" }
        Expand-Archive -LiteralPath $archive -DestinationPath $temporaryDirectory

        $fontDirectory = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
        if (-not (Test-Path $fontDirectory)) { [void](New-Item -ItemType Directory -Path $fontDirectory -Force) }
        foreach ($fontFile in $Font.Files) {
            $source = Join-Path $temporaryDirectory $fontFile.FileName
            $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($sourceHash -ne $fontFile.Sha256) { throw "Font file hash mismatch for $($fontFile.FileName)." }
            Copy-Item -LiteralPath $source -Destination (Join-Path $fontDirectory $fontFile.FileName)
        }
        Register-WinEnvFont -Font $Font
    }
    finally {
        if (Test-Path -LiteralPath $temporaryDirectory) { Remove-Item -LiteralPath $temporaryDirectory -Recurse -Force }
    }
}

function Get-WinEnvObjectProperties {
    param($Value)
    if ($Value -is [System.Collections.IDictionary]) {
        return @($Value.Keys | ForEach-Object { [pscustomobject]@{ Name = [string]$_; Value = $Value[$_] } })
    }
    return @($Value.PSObject.Properties | Where-Object MemberType -in 'NoteProperty', 'Property')
}

function Get-WinEnvJsonMember {
    <#
        .SYNOPSIS
        Read one member of a parsed JSON value, or $null when it has none.

        .DESCRIPTION
        The name is matched ordinally. PSObject's own indexer is
        case-insensitive while every comparison built on this helper is
        ordinal, so reading `Source` as `source` would let an entry Windows
        Terminal did not write pass as one it generated.

        Every return is comma-wrapped because a bare `return $array` writes the
        array's elements to the pipeline one at a time, and a one-element
        array comes back to the caller as its single element. A settings file
        declaring one profile would then be read as an object rather than a
        list.
    #>
    param(
        $Value,
        [Parameter(Mandatory)][string] $Name
    )

    if ($null -eq $Value) { return $null }
    if ($Value -is [System.Collections.IDictionary]) {
        if ($Value.Contains($Name)) { return , $Value[$Name] }
        return $null
    }
    $property = $Value.PSObject.Properties | Where-Object { $_.Name -ceq $Name } | Select-Object -First 1
    if (-not $property) { return $null }
    return , $property.Value
}

function Test-WinEnvJsonSubset {
    param($Expected, $Actual)

    if ($null -eq $Expected) { return $null -eq $Actual }
    if ($null -eq $Actual) { return $false }
    if ($Expected -is [string] -or $Expected -is [ValueType]) { return $Expected -eq $Actual }
    if ($Expected -is [System.Collections.IList]) {
        if ($Actual -isnot [System.Collections.IList] -or $Expected.Count -ne $Actual.Count) { return $false }
        for ($i = 0; $i -lt $Expected.Count; $i++) {
            if (-not (Test-WinEnvJsonSubset -Expected $Expected[$i] -Actual $Actual[$i])) { return $false }
        }
        return $true
    }

    foreach ($property in (Get-WinEnvObjectProperties $Expected)) {
        $actualProperty = $Actual.PSObject.Properties[$property.Name]
        if (-not $actualProperty) { return $false }
        if (-not (Test-WinEnvJsonSubset -Expected $property.Value -Actual $actualProperty.Value)) { return $false }
    }
    return $true
}

function ConvertTo-WinEnvCanonicalJson {
    param([Parameter(Mandatory)][string] $Content)
    return (($Content | ConvertFrom-Json -ErrorAction Stop) | ConvertTo-Json -Depth 100 -Compress)
}

function Test-WinEnvGeneratedProfileList {
    <#
        .SYNOPSIS
        Compare a declared Windows Terminal profile list with a host's.

        .DESCRIPTION
        Declared profiles are matched by guid rather than by position, because
        Windows Terminal decides where in the list it writes the profiles its
        fragments and dynamic generators produce. Every declared guid must
        appear exactly once and its object must be equal, so a changed
        declared profile is still drift.

        An entry the payload does not declare is tolerated only when it
        carries a non-empty string `guid` and a non-empty string `source`,
        which is how Windows Terminal records that a fragment extension or a
        profile generator produced it. An undeclared entry without `source`
        was written by a person or by another tool, and one without a `guid`
        is not the shape this rule can key on at all, so both stay drift:
        this is a tolerance for one known writer, not a licence for the file
        to hold anything.
    #>
    param(
        [Parameter(Mandatory)] $Expected,
        $Actual
    )

    if ($Actual -isnot [System.Collections.IList]) { return $false }

    $declared = [System.Collections.Generic.Dictionary[string, object]]::new([System.StringComparer]::Ordinal)
    foreach ($entry in $Expected) {
        $guid = [string](Get-WinEnvJsonMember -Value $entry -Name 'guid')
        if ([string]::IsNullOrWhiteSpace($guid)) {
            throw 'A declared Windows Terminal profile has no guid; this mode matches declared profiles by guid.'
        }
        if ($declared.ContainsKey($guid)) {
            throw "The declared Windows Terminal profiles use the guid '$guid' more than once."
        }
        $declared[$guid] = $entry
    }

    $matched = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($entry in $Actual) {
        $guid = Get-WinEnvJsonMember -Value $entry -Name 'guid'
        if ($guid -is [string] -and $declared.ContainsKey($guid)) {
            # A second entry carrying a declared guid is ambiguous rather than
            # generated, whatever its source says.
            if (-not $matched.Add($guid)) { return $false }
            $expectedJson = $declared[$guid] | ConvertTo-Json -Depth 100 -Compress
            $actualJson = $entry | ConvertTo-Json -Depth 100 -Compress
            if ($expectedJson -cne $actualJson) { return $false }
            continue
        }
        # Both members are tested as strings rather than coerced to one: a
        # `source` of 0 or false is not a generator's name, and an entry with
        # no guid is not something this rule could key on.
        if ($guid -isnot [string] -or [string]::IsNullOrWhiteSpace($guid)) { return $false }
        $source = Get-WinEnvJsonMember -Value $entry -Name 'source'
        if ($source -isnot [string] -or [string]::IsNullOrWhiteSpace($source)) { return $false }
    }

    return $matched.Count -eq $declared.Count
}

function Test-WinEnvJsonWithGeneratedProfiles {
    <#
        .SYNOPSIS
        Compare two Windows Terminal settings documents, tolerating the
        profiles the application generated.

        .DESCRIPTION
        This is `ExactJson` everywhere except inside `profiles.list`. Apply
        still writes the whole payload; only the read side accepts that
        Windows Terminal materialises its fragment and dynamic profiles back
        into the file it co-owns, which under plain `ExactJson` made a host
        that merely runs Windows Terminal permanently drifted and left a
        deployed host unrecorded when post-apply validation threw.
    #>
    param(
        [Parameter(Mandatory)][string] $Expected,
        [Parameter(Mandatory)][string] $Actual
    )

    $expectedDocument = $Expected | ConvertFrom-Json -ErrorAction Stop
    $actualDocument = $Actual | ConvertFrom-Json -ErrorAction Stop

    $expectedList = Get-WinEnvJsonMember -Value (Get-WinEnvJsonMember -Value $expectedDocument -Name 'profiles') -Name 'list'
    if ($expectedList -isnot [System.Collections.IList]) {
        throw 'A payload compared as ExactJsonWithGeneratedProfiles declares no profiles.list array.'
    }

    $actualProfiles = Get-WinEnvJsonMember -Value $actualDocument -Name 'profiles'
    $actualList = Get-WinEnvJsonMember -Value $actualProfiles -Name 'list'
    if (-not (Test-WinEnvGeneratedProfileList -Expected $expectedList -Actual $actualList)) { return $false }

    # Every declared profile is present exactly once and equal, so putting the
    # declared list back in place of the host's removes the generated entries
    # and nothing else. What remains is held to the same canonical equality
    # ExactJson applies, key set, key order and case included.
    $actualProfiles.list = $expectedList
    return (ConvertTo-WinEnvCanonicalJson $Expected) -ceq ($actualDocument | ConvertTo-Json -Depth 100 -Compress)
}

function Test-WinEnvManagedFile {
    param(
        [Parameter(Mandatory)][hashtable] $Definition,
        [Parameter(Mandatory)][string] $RepositoryRoot
    )

    $sourcePath = Join-Path $RepositoryRoot $Definition.Source
    $targetPath = Resolve-WinEnvPath $Definition.Target
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw "Managed source is missing: $sourcePath" }
    if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) { return $false }
    $expectedText = Expand-WinEnvTemplate (Get-Content -LiteralPath $sourcePath -Raw -Encoding utf8)
    $actualText = Get-Content -LiteralPath $targetPath -Raw -Encoding utf8
    switch ($Definition.Compare) {
        'Text' { return $expectedText.Replace("`r`n", "`n") -eq $actualText.Replace("`r`n", "`n") }
        'ExactJson' { return (ConvertTo-WinEnvCanonicalJson $expectedText) -ceq (ConvertTo-WinEnvCanonicalJson $actualText) }
        'JsonSubset' {
            $expected = $expectedText | ConvertFrom-Json -ErrorAction Stop
            $actual = $actualText | ConvertFrom-Json -ErrorAction Stop
            return Test-WinEnvJsonSubset -Expected $expected -Actual $actual
        }
        'ExactJsonWithGeneratedProfiles' {
            return Test-WinEnvJsonWithGeneratedProfiles -Expected $expectedText -Actual $actualText
        }
        default { throw "Unknown comparison mode '$($Definition.Compare)'." }
    }
}

$script:WinEnvLuaCompiler = $null
$script:WinEnvLuaCompilerResolved = $false

function Get-WinEnvLuaCompiler {
    # Resolved once. There is no single spelling of the Lua compiler across the
    # ways it reaches a Windows PATH, and probing per file made the cost scale
    # with the number of payloads.
    if (-not $script:WinEnvLuaCompilerResolved) {
        $script:WinEnvLuaCompiler =
            Get-Command luac.exe, luac5.4.exe, luac54.exe, luac5.1.exe, luac51.exe, luac `
                -ErrorAction SilentlyContinue |
            Select-Object -First 1
        $script:WinEnvLuaCompilerResolved = $true
    }

    return $script:WinEnvLuaCompiler
}

function Test-WinEnvSourceFile {
    <#
        .SYNOPSIS
        Parse one managed source with the parser that will consume it.

        .DESCRIPTION
        Returns $null when the file was parsed, or a reason when this host has
        no parser for it. A syntax error still throws, because a parser that
        ran and rejected the file is a failure rather than missing evidence.

        Callers decide what an unverified source means. This function must not,
        which is what it used to do by skipping a missing Zellij in silence and
        reporting the file as valid.
    #>
    param(
        [Parameter(Mandatory)][hashtable] $Definition,
        [Parameter(Mandatory)][string] $RepositoryRoot
    )

    $path = Join-Path $RepositoryRoot $Definition.Source
    switch ($Definition.Parser) {
        'Json' { $null = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json -ErrorAction Stop }
        'Ini' {
            $section = $null
            $lineNumber = 0
            foreach ($line in (Get-Content -LiteralPath $path)) {
                $lineNumber++
                $trimmed = $line.Trim()
                if (-not $trimmed -or $trimmed.StartsWith('#') -or $trimmed.StartsWith(';')) { continue }
                if ($trimmed -match '^\[([^\[\]]+)\]$') {
                    $section = $matches[1]
                    continue
                }
                if (-not $section -or $trimmed -notmatch '^[^=\s]+\s*=\s*.+$') {
                    throw "INI syntax error in '$path' at line $lineNumber."
                }
            }
        }
        'PowerShell' {
            $tokens = $null; $errors = $null
            [void][System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors)
            if ($errors.Count) { throw "PowerShell syntax error in '$path': $($errors[0].Message)" }
        }
        'Kdl' {
            $zellij = Get-Command zellij.exe -ErrorAction SilentlyContinue
            if (-not $zellij) { return 'zellij.exe is unavailable' }
            $null = & $zellij.Source --config $path setup --check 2>&1
            if ($LASTEXITCODE -ne 0) { throw "Zellij rejected '$path'." }
        }
        'Lua' {
            # WezTerm loads these files on native Windows, so luac is the
            # parser that decides whether they are well formed.
            $luac = Get-WinEnvLuaCompiler
            if (-not $luac) { return 'no luac compiler is available' }
            $null = & $luac.Source -p $path 2>&1
            if ($LASTEXITCODE -ne 0) { throw "Lua rejected '$path'." }
        }
        'Text' {
            # Existence and content are checked by the managed-file path.
        }
    }

    return $null
}

function Backup-WinEnvFile {
    param(
        [Parameter(Mandatory)][string] $Id,
        [Parameter(Mandatory)][string] $Target,
        [Parameter(Mandatory)][string] $BackupRoot
    )

    if (-not (Test-Path -LiteralPath $Target -PathType Leaf)) { return }
    if (-not (Test-Path -LiteralPath $BackupRoot)) { [void](New-Item -ItemType Directory -Path $BackupRoot -Force) }
    $backup = Join-Path $BackupRoot ($Id + '.bak')
    if (-not (Test-Path -LiteralPath $backup)) { Copy-Item -LiteralPath $Target -Destination $backup }
}

function Set-WinEnvManagedFile {
    param(
        [Parameter(Mandatory)][hashtable] $Definition,
        [Parameter(Mandatory)][string] $RepositoryRoot
    )

    $sourcePath = Join-Path $RepositoryRoot $Definition.Source
    $targetPath = Resolve-WinEnvPath $Definition.Target
    $content = Expand-WinEnvTemplate (Get-Content -LiteralPath $sourcePath -Raw -Encoding utf8)
    Write-WinEnvAtomicText -Path $targetPath -Content $content
}

function Get-WinEnvProfileHook {
    return @'
#region win-env
. (Join-Path $env:LOCALAPPDATA 'win-env\powershell\profile.ps1')
#endregion win-env
'@
}

function Test-WinEnvProfileHook {
    param([Parameter(Mandatory)][string] $ProfilePath)

    if (-not (Test-Path -LiteralPath $ProfilePath -PathType Leaf)) { return $false }
    $content = Get-Content -LiteralPath $ProfilePath -Raw
    $matches = [regex]::Matches($content, '(?ms)^#region win-env\r?\n.*?^#endregion win-env\s*')
    if ($matches.Count -ne 1) { return $false }
    return $matches[0].Value.Trim() -eq (Get-WinEnvProfileHook).Trim()
}

function Set-WinEnvProfileHook {
    param([Parameter(Mandatory)][string] $ProfilePath)

    $content = if (Test-Path -LiteralPath $ProfilePath) { Get-Content -LiteralPath $ProfilePath -Raw } else { '' }
    $starts = ([regex]::Matches($content, '(?m)^#region win-env\s*$')).Count
    $ends = ([regex]::Matches($content, '(?m)^#endregion win-env\s*$')).Count
    if ($starts -ne $ends) { throw 'The existing PowerShell profile contains an unmatched win-env marker.' }
    $clean = [regex]::Replace($content, '(?ms)^#region win-env\r?\n.*?^#endregion win-env\s*', '').TrimEnd()
    $newContent = if ($clean) { $clean + "`r`n`r`n" + (Get-WinEnvProfileHook).Trim() + "`r`n" } else { (Get-WinEnvProfileHook).Trim() + "`r`n" }
    Write-WinEnvAtomicText -Path $ProfilePath -Content $newContent
}

function Get-WinEnvPowerShellProfilePath {
    return $PROFILE.CurrentUserAllHosts
}

function Test-WinEnvTerminalDelegation {
    param([Parameter(Mandatory)][hashtable] $Terminal)
    $key = Get-ItemProperty -Path 'HKCU:\Console\%%Startup' -ErrorAction SilentlyContinue
    return [bool]($key -and $key.DelegationTerminal -eq $Terminal.DelegationTerminal -and $key.DelegationConsole -eq $Terminal.DelegationConsole)
}

function Set-WinEnvTerminalDelegation {
    param([Parameter(Mandatory)][hashtable] $Terminal)
    $path = 'HKCU:\Console\%%Startup'
    if (-not (Test-Path $path)) { [void](New-Item -Path $path -Force) }
    Set-ItemProperty -Path $path -Name DelegationTerminal -Value $Terminal.DelegationTerminal -Type String
    Set-ItemProperty -Path $path -Name DelegationConsole -Value $Terminal.DelegationConsole -Type String
}

function Stop-WinEnvPowerToys {
    $running = [bool](Get-Process -Name PowerToys -ErrorAction SilentlyContinue)
    if (-not $running) { return $false }

    # PowerToys has multiple hidden message-loop windows. Each non-forced taskkill
    # closes one of them, so repeat until taskkill can no longer find the process.
    for ($attempt = 0; $attempt -lt 100; $attempt++) {
        $null = & taskkill.exe /IM PowerToys.exe 2>&1
        if ($LASTEXITCODE -ne 0) { break }
    }

    if (Get-Process -Name PowerToys -ErrorAction SilentlyContinue) {
        $elevatedScript = @'
for ($attempt = 0; $attempt -lt 100; $attempt++) {
    & taskkill.exe /IM PowerToys.exe 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { exit 0 }
}
exit 1
'@
        $encodedScript = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($elevatedScript))
        try {
            $taskKill = Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile', '-NonInteractive', '-EncodedCommand', $encodedScript -Verb RunAs -Wait -PassThru
        }
        catch {
            throw "PowerToys requires elevation to close, but the elevated close request failed or was cancelled: $($_.Exception.Message)"
        }
        if ($taskKill.ExitCode -ne 0 -and (Get-Process -Name PowerToys -ErrorAction SilentlyContinue)) {
            throw "The elevated PowerToys close request failed with exit code $($taskKill.ExitCode)."
        }
    }

    $deadline = [DateTime]::UtcNow.AddSeconds(15)
    while ((Get-Process -Name PowerToys -ErrorAction SilentlyContinue) -and [DateTime]::UtcNow -lt $deadline) {
        Start-Sleep -Milliseconds 250
    }
    if (Get-Process -Name PowerToys -ErrorAction SilentlyContinue) { throw 'PowerToys did not exit within 15 seconds.' }
    return $true
}

function Start-WinEnvPowerToys {
    if (Get-Process -Name PowerToys -ErrorAction SilentlyContinue) { return }
    $task = Get-ScheduledTask -TaskPath '\PowerToys\' -TaskName "Autorun for $env:USERNAME" -ErrorAction SilentlyContinue
    if ($task) {
        Start-ScheduledTask -InputObject $task
    }
    else {
        $candidates = @(
            (Join-Path $env:ProgramFiles 'PowerToys\PowerToys.exe'),
            (Join-Path $env:LOCALAPPDATA 'PowerToys\PowerToys.exe')
        )
        $executable = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        if (-not $executable) { throw 'PowerToys is installed but PowerToys.exe could not be located.' }
        Start-Process -FilePath $executable
    }

    $deadline = [DateTime]::UtcNow.AddSeconds(15)
    while (-not (Get-Process -Name PowerToys -ErrorAction SilentlyContinue) -and [DateTime]::UtcNow -lt $deadline) {
        Start-Sleep -Milliseconds 250
    }
    if (-not (Get-Process -Name PowerToys -ErrorAction SilentlyContinue)) { throw 'PowerToys did not start within 15 seconds.' }
}

Export-ModuleMember -Function *-WinEnv*
