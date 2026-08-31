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

# The three host observations the font state is derived from, as seams for the
# same reason as the two above: the states a font can be in outnumber the ones
# any single host can be put into, and the one this repository got wrong is a
# state no developer machine reproduces on demand.
$script:UserFontRegistryPath = 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'
$script:SystemFontRegistryPath = 'HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'
$script:DefaultFontDirectoryQuery = { Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts' }
$script:DefaultFontRegistryQuery = {
    param([string] $Path)
    if (Test-Path $Path) { Get-ItemProperty -Path $Path } else { $null }
}
$script:DefaultDirectWriteQuery = { param([string] $FamilyName) Test-WinEnvDirectWriteFont -FamilyName $FamilyName }

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

function Test-WinEnvWindowsHost {
    <#
        .SYNOPSIS
        Whether this run is on Windows, the only platform capture.ps1 (and
        anything else that reads a host directly) may act on.

        .DESCRIPTION
        $IsWindows is PowerShell 7's own automatic variable; every caller of
        this module already requires version 7, so it is always defined. Read
        through this function instead of inline, with an injectable override,
        so a refusal on Unix-like pwsh -- macOS or WSL included -- has a
        fixture without needing a foreign host to prove itself.
    #>
    param(
        [bool] $IsWindows = $global:IsWindows
    )

    return $IsWindows
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

function Get-WinEnvHostPath {
    <#
        .SYNOPSIS
        The host values a managed target and a payload template are written in
        terms of, plus this host's account name.

        .DESCRIPTION
        One seam for the three directories and the account name, so the deploy
        direction and the capture direction read the same host in the same way,
        and so a fixture can hand both directions a host that no test machine
        has to be. The default is this process's environment, which is what
        every caller that predates capture used directly.
    #>

    return @{
        UserProfile  = [string]$env:USERPROFILE
        LocalAppData = [string]$env:LOCALAPPDATA
        AppData      = [string]$env:APPDATA
        # [Environment]::UserName rather than the account-name environment
        # variable, which is absent on the Unix-like hosts this module's
        # fixtures run on. The two agree on Windows.
        UserName     = [string][Environment]::UserName
    }
}

function Resolve-WinEnvPath {
    param(
        [Parameter(Mandatory)][string] $Path,
        [hashtable] $HostPath = (Get-WinEnvHostPath)
    )

    return $Path.Replace('{LOCALAPPDATA}', [string]$HostPath.LocalAppData).
        Replace('{APPDATA}', [string]$HostPath.AppData).
        Replace('{USERPROFILE}', [string]$HostPath.UserProfile)
}

function Expand-WinEnvTemplate {
    param(
        [Parameter(Mandatory)][string] $Content,
        [hashtable] $HostPath = (Get-WinEnvHostPath)
    )

    $jsonLocalAppData = ([string]$HostPath.LocalAppData).Replace('\', '\\')
    return $Content.Replace('__LOCALAPPDATA_JSON__', $jsonLocalAppData)
}

function ConvertFrom-WinEnvTemplate {
    <#
        .SYNOPSIS
        The inverse of Expand-WinEnvTemplate: host content with this host's own
        directories put back as the placeholder the deploy direction expands,
        plus the list of the ones it has no placeholder for.

        .DESCRIPTION
        This domain has exactly one content placeholder, and Apply expands it
        to the JSON-escaped spelling of LOCALAPPDATA. That asymmetry is the
        design of this function rather than an oversight of it: a capture that
        wrote `{USERPROFILE}` into a payload would produce desired state Apply
        deploys literally, the host would then hold the placeholder text, and
        every later check would report drift no Apply could clear. Every
        spelling this direction cannot represent is therefore reported instead
        of rewritten, and Get-WinEnvCapturePlan refuses that file rather than
        committing a leak.

        Longest value first. USERPROFILE is a prefix of both of the others, so
        a shortest-first pass would rewrite the head of a LOCALAPPDATA
        occurrence and leave behind a path that is neither a placeholder nor a
        host path. Both spellings of each value are searched, because a JSON
        payload carries its separators doubled and a text payload carries them
        once. The match is case-insensitive because Windows accepts more than
        one spelling of the same directory while this repository's comparisons
        are ordinal, so a captured occurrence is normalised to the spelling
        Apply will write back.
    #>
    param(
        [Parameter(Mandatory)][AllowEmptyString()][string] $Content,
        [hashtable] $HostPath = (Get-WinEnvHostPath)
    )

    $variables = @(
        @{ Name = 'LOCALAPPDATA'; Value = [string]$HostPath.LocalAppData; JsonToken = '__LOCALAPPDATA_JSON__' },
        @{ Name = 'APPDATA'; Value = [string]$HostPath.AppData; JsonToken = $null },
        @{ Name = 'USERPROFILE'; Value = [string]$HostPath.UserProfile; JsonToken = $null }
    )
    $ordered = @($variables |
            Where-Object { $_.Value } |
            Sort-Object -Property @{ Expression = { ([string]$_.Value).Length } } -Descending)

    $text = $Content
    $unrepresented = [System.Collections.Generic.List[string]]::new()
    foreach ($variable in $ordered) {
        $raw = [string]$variable.Value
        $escaped = $raw.Replace('\', '\\')
        $spellings = @(
            @{ Label = 'JSON-escaped'; Text = $escaped; Token = $variable.JsonToken },
            @{ Label = 'raw'; Text = $raw; Token = $null }
        )
        foreach ($spelling in $spellings) {
            # A value with no separator has one spelling, not two. Searching for
            # it twice would report the same occurrence under both labels.
            if ($spelling.Label -eq 'raw' -and $escaped -ceq $raw) { continue }
            $pattern = '(?i)' + [regex]::Escape([string]$spelling.Text)
            if (-not [regex]::IsMatch($text, $pattern)) { continue }
            if ($spelling.Token) {
                $text = [regex]::Replace($text, $pattern, [string]$spelling.Token)
                continue
            }
            $unrepresented.Add("$($variable.Name) ($($spelling.Label))")
        }
    }

    return @{ Content = $text; Unrepresented = @($unrepresented) }
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
    # Five states, because "this host has some of the faces the manifest lists"
    # and "something foreign is sitting under the manifest's names" are
    # different claims and only the second is a reason to refuse an Apply. The
    # manifest's file list grows whenever a face is added to it, and every host
    # that installed the font before that edit then holds a valid strict subset
    # of it. That is Incomplete: install the rest. A file with a different
    # hash, a registration pointing somewhere else, or a system-wide install of
    # the same family stays Conflict, which nothing here overwrites.
    #
    # Position is declared so the query seams cannot be bound positionally by
    # accident; once one parameter has an explicit position the rest are
    # name-only.
    param(
        [Parameter(Mandatory, Position = 0)][hashtable] $Font,
        [scriptblock] $FontDirectoryQuery = $script:DefaultFontDirectoryQuery,
        [scriptblock] $FontRegistryQuery = $script:DefaultFontRegistryQuery,
        [scriptblock] $DirectWriteQuery = $script:DefaultDirectWriteQuery
    )

    $fontDirectory = & $FontDirectoryQuery
    $registry = & $FontRegistryQuery $script:UserFontRegistryPath
    $systemRegistry = & $FontRegistryQuery $script:SystemFontRegistryPath
    # Enumerated as a collection rather than through a member-access
    # projection: a key that carries no value at all is a real state on a host
    # that has never installed a font, and the projection cannot describe it.
    $systemFamilyDetected = [bool]($systemRegistry -and (@($systemRegistry.PSObject.Properties) |
                Where-Object { $_.Name -like "$($Font.Name)*" }))
    $validFiles = 0
    $validRegistrations = 0
    $invalidFiles = 0
    $foreignRegistrations = 0
    $artifacts = 0
    foreach ($fontFile in $Font.Files) {
        $path = Join-Path $fontDirectory $fontFile.FileName
        $filePresent = Test-Path -LiteralPath $path -PathType Leaf
        $property = if ($registry) { $registry.PSObject.Properties[$fontFile.RegistryName] } else { $null }
        if ($filePresent -or $property) { $artifacts++ }
        # A registration under this manifest's own name that names any other
        # path is the case the refusal exists for, whether or not the file it
        # names exists. A registration naming our own path whose file is gone
        # is not: writing that file back is exactly what Apply does.
        if ($property -and [string]$property.Value -ine $path) { $foreignRegistrations++ }
        if (-not $filePresent) { continue }

        $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($hash -ne $fontFile.Sha256) { $invalidFiles++; continue }
        $validFiles++
        if ($property -and [string]$property.Value -ieq $path) { $validRegistrations++ }
    }

    $directWriteDetected = [bool](& $DirectWriteQuery $Font.Name)
    $registered = $systemFamilyDetected -or $validRegistrations -eq $Font.Files.Count
    $installed = $registered -and $directWriteDetected
    # A host holding every listed file whose registrations are only missing.
    # A registration under one of these names pointing at another path is not a
    # missing registration and is not repaired by overwriting it, so it leaves
    # this state as well as Incomplete: both of them write, and neither may
    # write over a value this repository did not put there.
    $registrationRepairable = -not $systemFamilyDetected -and $foreignRegistrations -eq 0 -and
        $validFiles -eq $Font.Files.Count -and $validRegistrations -ne $Font.Files.Count
    # Every artifact this host holds is one of ours and valid, at least one is
    # there, and at least one listed face is not fully installed yet. Nothing
    # has to be overwritten to finish that, so nothing is refused. Registration
    # repair is decided first: a host holding every file is that narrower case,
    # not this one.
    $incomplete = -not $installed -and -not $registrationRepairable -and -not $systemFamilyDetected -and
        $invalidFiles -eq 0 -and $foreignRegistrations -eq 0 -and
        $artifacts -gt 0 -and $validRegistrations -lt $Font.Files.Count
    $conflict = -not $installed -and -not $registrationRepairable -and -not $incomplete -and
        ($artifacts -gt 0 -or $systemFamilyDetected)
    [pscustomobject]@{
        Installed              = $installed
        Missing                = (-not $installed -and -not $registrationRepairable -and -not $incomplete -and -not $conflict)
        Conflict               = $conflict
        Incomplete             = $incomplete
        RegistrationRepairable = $registrationRepairable
        DirectWriteDetected    = $directWriteDetected
        InstalledFaceCount     = $validRegistrations
        FaceCount              = $Font.Files.Count
    }
}

function Register-WinEnvFont {
    param([Parameter(Mandatory)][hashtable] $Font)

    $fontDirectory = & $script:DefaultFontDirectoryQuery
    $registryPath = $script:UserFontRegistryPath
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

    # Every listed file is validated, because a file that is not the one the
    # manifest pins must stop the run whether or not it is registered. Only a
    # registration that is not already this exact path is written: this runs
    # over faces a previous Apply already registered, and desired state that is
    # already met is not rewritten. Loading the resource is not a registration
    # and is repeated for every face, so the running session resolves the whole
    # family rather than only the part of it this Apply added.
    $registry = if (Test-Path $registryPath) { Get-ItemProperty -Path $registryPath } else { $null }
    foreach ($fontFile in $Font.Files) {
        $path = Join-Path $fontDirectory $fontFile.FileName
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Font file is missing: $path" }
        $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($hash -ne $fontFile.Sha256) { throw "Font file hash mismatch for $($fontFile.FileName)." }
        $property = if ($registry) { $registry.PSObject.Properties[$fontFile.RegistryName] } else { $null }
        if (-not ($property -and [string]$property.Value -ieq $path)) {
            Set-ItemProperty -Path $registryPath -Name $fontFile.RegistryName -Value $path -Type String
        }
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

        $fontDirectory = & $script:DefaultFontDirectoryQuery
        if (-not (Test-Path $fontDirectory)) { [void](New-Item -ItemType Directory -Path $fontDirectory -Force) }
        # This also runs for a host that is only missing some of the faces, so
        # a face that is already there byte for byte is left alone rather than
        # rewritten: Windows holds an installed font file open, and a copy over
        # it can fail for a file that needed no change at all.
        foreach ($fontFile in $Font.Files) {
            $destination = Join-Path $fontDirectory $fontFile.FileName
            if (Test-Path -LiteralPath $destination -PathType Leaf) {
                $currentHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
                if ($currentHash -eq $fontFile.Sha256) { continue }
            }
            $source = Join-Path $temporaryDirectory $fontFile.FileName
            $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($sourceHash -ne $fontFile.Sha256) { throw "Font file hash mismatch for $($fontFile.FileName)." }
            Copy-Item -LiteralPath $source -Destination $destination
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

function Get-WinEnvJsonValueKind {
    <#
        .SYNOPSIS
        Which of the three shapes a parsed JSON value has: `object`, `list`, or
        `scalar`.

        .DESCRIPTION
        The three tests are the ones Test-WinEnvJsonSubset already branches on,
        written in the same order and with the same operators, so the two
        functions can never disagree about what a value is. `null` is a scalar
        rather than a kind of its own: the read side treats a declared `null`
        and a declared string as the same kind of leaf, and a settings key that
        moves between a path and `null` is an ordinary value change rather than
        a schema change.
    #>
    param($Value)

    if ($null -eq $Value) { return 'scalar' }
    if ($Value -is [string] -or $Value -is [ValueType]) { return 'scalar' }
    if ($Value -is [System.Collections.IList]) { return 'list' }
    return 'object'
}

function Join-WinEnvJsonPath {
    # A dotted path used only to name the key a refusal is about. It is a
    # diagnostic, never a lookup, so a member name that itself holds a dot is
    # printed as it is rather than escaped.
    param(
        [Parameter(Mandatory)][AllowEmptyString()][string] $Path,
        [Parameter(Mandatory)][string] $Name
    )

    if ([string]::IsNullOrEmpty($Path)) { return $Name }
    return "$Path.$Name"
}

function Get-WinEnvJsonSubsetProjection {
    <#
        .SYNOPSIS
        One host value reduced to the key paths its payload declares.

        .DESCRIPTION
        The recursive half of ConvertTo-WinEnvJsonSubsetProjection. It walks the
        declared payload and the host document together and returns the host's
        values arranged in the payload's declared shape, or throws with the key
        path that made the projection impossible.

        Each of the three kinds is projected the way the read side compares it:

          - a declared object contributes exactly the member names it declares,
            each carrying the host's value. Every other member of the host
            object is dropped, which is the whole mechanism: a key the payload
            does not declare cannot reach desired state, so a version stamp, a
            timestamp, a telemetry flag or a window geometry the application
            keeps in the same file is never captured;
          - a declared list contributes the host's list, element by element,
            with element `i` projected onto declared element `i` where the
            payload has one and taken as the host holds it where it does not.
            The read side compares a list by position and requires equal
            length, so a payload cannot declare a member subset that survives a
            length change; taking the elements it never declared as they are is
            the only reading of the list the payload's own shape supports;
          - a declared scalar contributes the host's scalar.

        The member lookup is Test-WinEnvJsonSubset's own -- the PSObject
        indexer, which is case-insensitive -- rather than the ordinal helper
        Windows Terminal's guid matching uses. Agreeing with the comparison
        matters more here than ordinality: a host that spells a declared key
        with different case is a key the read side already found, and the
        projection writes its value back under the name the payload declares,
        so the payload's own spelling is stable across captures.

        Two host shapes are refused rather than projected, and both are shapes
        the read side already reports as drift while the payload's declared
        shape cannot express the fix:

          - a declared member the host object does not hold. Whether the key
            should be dropped from desired state or restored to the host is not
            a question this direction can answer, and guessing either way would
            silently change what the payload manages;
          - a host value whose kind is not the declared value's kind. The
            application migrated its own schema under a key this payload
            declares, and writing the new shape in would discard the whole
            declared subtree without saying so.

        Both name the key path, because a refusal an operator cannot act on is
        worse than no capture at all.
    #>
    param(
        $Declared,
        $Actual,
        [Parameter(Mandatory)][AllowEmptyString()][string] $Path
    )

    $declaredKind = Get-WinEnvJsonValueKind $Declared
    $actualKind = Get-WinEnvJsonValueKind $Actual
    if ($declaredKind -cne $actualKind) {
        $where = if ([string]::IsNullOrEmpty($Path)) { 'at the document root' } else { "at '$Path'" }
        # Spelt out rather than assembled, so the reason reads as a sentence
        # in every one of the six pairings this can report.
        $article = @{ object = 'an object'; list = 'a list'; scalar = 'a scalar' }
        throw ("the host file holds $($article[$actualKind]) $where where the payload declares " +
            "$($article[$declaredKind]); the application changed the shape of a key this payload " +
            'declares, so edit the payload by hand')
    }

    if ($declaredKind -ceq 'object') {
        $projected = [ordered]@{}
        foreach ($property in (Get-WinEnvObjectProperties $Declared)) {
            $name = [string]$property.Name
            $child = Join-WinEnvJsonPath -Path $Path -Name $name
            $actualProperty = $Actual.PSObject.Properties[$name]
            if (-not $actualProperty) {
                throw ("the host file no longer holds '$child', which the payload declares; " +
                    'remove the key from the payload or restore it in the application')
            }
            $projected[$name] =
                Get-WinEnvJsonSubsetProjection -Declared $property.Value -Actual $actualProperty.Value -Path $child
        }
        return $projected
    }

    if ($declaredKind -ceq 'list') {
        # Collected into a typed list and returned comma-wrapped rather than
        # gathered with @( ): a projected element that is itself a list would
        # be flattened into its parent by the array subexpression, and a
        # one-element result would reach the caller as its single element.
        $declaredItems = @($Declared)
        $actualItems = @($Actual)
        $items = [System.Collections.Generic.List[object]]::new()
        for ($index = 0; $index -lt $actualItems.Count; $index++) {
            if ($index -lt $declaredItems.Count) {
                $items.Add((Get-WinEnvJsonSubsetProjection -Declared $declaredItems[$index] `
                            -Actual $actualItems[$index] -Path "$Path[$index]"))
                continue
            }
            $items.Add($actualItems[$index])
        }
        return , $items.ToArray()
    }

    return $Actual
}

function ConvertTo-WinEnvJsonSubsetProjection {
    <#
        .SYNOPSIS
        One host JSON document reduced to the key paths its payload declares,
        as text.

        .DESCRIPTION
        The capture side of JsonSubset, and the reason that mode is no longer
        refused outright. The read side has always said that a JsonSubset
        payload declares which keys it owns and tolerates every other key the
        application keeps in the same file. The write direction was missing
        rather than impossible: the values of the keys the payload declares are
        read straight off the host, so the payload that would make this host
        clean is derivable after all. What is not derivable -- the keys the
        payload deliberately does not declare -- is exactly what must never
        reach desired state, so the projection drops it instead of guessing.

        This is one mechanism rather than a list of keys to ignore per file. An
        ignore list is a second declaration of what a payload owns, kept beside
        the payload and free to disagree with it; a projection has only the
        payload, so a key is captured if and only if the payload declares it,
        and widening what is captured is an edit to the payload itself.

        One warning for whoever writes the next payload, because the safety of
        the sentence above is not uniform across the three kinds. An undeclared
        object member is dropped, so an object fails safe. A declared list is
        exact -- the read side matches it by position and requires equal length
        -- so declaring one claims the whole list, and declaring an EMPTY list
        claims whatever the host happens to hold there. That is the one shape in
        which a payload can silently absorb host state. Declare a list only when
        there is content to declare; a key left undeclared owns nothing, which is
        precisely what an empty declared list cannot express. The Pester suite
        holds every JsonSubset payload in this repository to that rule.

        Projection converges the check that reported the drift, by
        construction rather than by test: every member of the result is a
        member Test-WinEnvJsonSubset looks for, holding the value it found
        there, and every list in the result has the host's own length and
        elements. There is no host this can capture from and leave drifted.
    #>
    param(
        [Parameter(Mandatory)][string] $DeclaredContent,
        [Parameter(Mandatory)][string] $HostContent
    )

    # -NoEnumerate on both sides. ConvertFrom-Json writes a top-level JSON
    # array's elements to the pipeline one at a time, so a document whose root
    # is a one-element array would reach the projection as that element and be
    # read as an object rather than as a list.
    $declared = ConvertFrom-Json -InputObject $DeclaredContent -NoEnumerate -ErrorAction Stop
    $actual = ConvertFrom-Json -InputObject $HostContent -NoEnumerate -ErrorAction Stop
    $projected = Get-WinEnvJsonSubsetProjection -Declared $declared -Actual $actual -Path ''
    return ($projected | ConvertTo-Json -Depth 100)
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
        [Parameter(Mandatory)][string] $RepositoryRoot,
        # Additive and defaulted to this process's environment, so every caller
        # that predates capture reads the same host it always did. Capture
        # passes its own so that one run cannot resolve the target against one
        # host and restore the placeholders against another.
        [hashtable] $HostPath = (Get-WinEnvHostPath)
    )

    $sourcePath = Join-Path $RepositoryRoot $Definition.Source
    $targetPath = Resolve-WinEnvPath -Path $Definition.Target -HostPath $HostPath
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw "Managed source is missing: $sourcePath" }
    if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf)) { return $false }
    $expectedText = Expand-WinEnvTemplate -Content (Get-Content -LiteralPath $sourcePath -Raw -Encoding utf8) -HostPath $HostPath
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

# Files a host writes at runtime, matched by file name against both the payload
# this repository would hold and the target on the host. PowerToys rewrites
# both while it runs, they describe one machine's session rather than desired
# state, and AGENTS.md keeps snapshots of runtime state out of every domain.
#
# By name rather than by directory, because that is how the two guards that
# already exist decide it: the Pester suite asserts neither file is tracked,
# and tool/version-control/hygiene refuses either name anywhere in the tree. A
# capture that wrote one into a directory those two do not expect would be
# refused at the commit anyway, so agreeing with them here is what makes this
# tool's refusal the same rule stated earlier rather than a third opinion.
$script:WinEnvRuntimeStateName = @(
    'workspaces.json',
    'applied-layouts.json'
)

# An absolute account path, in every spelling this domain can meet. The axes
# are the same three tool/version-control/hygiene enforces repository-wide, so
# a capture cannot write a payload that the commit's own hygiene scan then
# refuses, and the tool does not depend on that scan running: whether the POSIX
# hooks execute under Git for Windows is recorded in docs/status.md as unknown.
#
#   - a drive-letter path, with either separator, singled or doubled: a text
#     payload carries one backslash, a JSON payload doubles it, and WSL and
#     several applications write the same path with forward slashes;
#   - the POSIX form, which reaches a Windows payload through WezTerm, Zellij
#     and anything else that stores a WSL path;
#   - the WSL UNC form a Windows Terminal startingDirectory carries.
#
# Every character class is written as a class rather than as an example: spelt
# out, this source would itself hold the text it hunts, and hygiene scans the
# whole tracked tree for exactly that.
$script:WinEnvAccountName = '[A-Za-z0-9._-]+'
$script:WinEnvPathSeparator = '[\\/]{1,2}'
# The UNC form opens with two separators, and a JSON payload doubles each of
# them, so the leading run is one to four rather than one to two. Anchoring the
# alternative and then admitting only two would miss every JSON spelling of it,
# because the character before the third backslash is a backslash and no anchor
# accepts one.
$script:WinEnvUncPrefix = '[\\/]{1,4}'
# hygiene's anchoring rule, restated: a match counts only where the path opens
# at a line start or after a character a path is introduced by. Without it a
# URL path or a flake store path reads as an account directory.
$script:WinEnvPathAnchor = '(^|[ \t''"`=(,:])'
$script:WinEnvAccountPathPattern = '(?im)' +
    '([A-Za-z]:' + $script:WinEnvPathSeparator + 'Users' + $script:WinEnvPathSeparator + $script:WinEnvAccountName + ')' +
    '|(' + $script:WinEnvPathAnchor + '/(home|Users)/' + $script:WinEnvAccountName + ')' +
    '|(' + $script:WinEnvPathAnchor + $script:WinEnvUncPrefix + 'wsl(\.localhost|\$)' +
        $script:WinEnvPathSeparator + $script:WinEnvAccountName +
        $script:WinEnvPathSeparator + 'home' + $script:WinEnvPathSeparator + $script:WinEnvAccountName + ')'

# AGENTS.md, Host safety: a .wslconfig firewall value is never added without
# explicit direction, and a capture is not direction.
$script:WinEnvWslFirewallPattern = '(?im)^[ \t]*firewall[ \t]*='

# Private, like Get-WinGetRegistration: the capture outcome's shape is this
# module's contract, but the two helpers that build it are not.
function Test-RuntimeStatePath {
    param([AllowNull()][string] $Path)

    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    # Split on both separators: a target is spelled the Windows way and a
    # payload source the manifest way, and this must decide either.
    $name = @($Path.Replace('\', '/') -split '/')[-1].ToLowerInvariant()
    return $script:WinEnvRuntimeStateName -contains $name
}

function New-CaptureOutcome {
    param(
        [Parameter(Mandatory)][hashtable] $Definition,
        [Parameter(Mandatory)][string] $Status,
        [AllowNull()][string] $Source = $null,
        [AllowNull()][string] $Target = $null,
        [AllowNull()][string] $Reason = $null,
        [AllowNull()][string] $Content = $null
    )

    return [pscustomobject]@{
        Id      = [string]$Definition.Id
        Feature = [string]$Definition.Feature
        # Carried through so the write side can decide how to render Content
        # -- pretty-printing a Json parser's payload -- without re-deriving a
        # decision Get-WinEnvCapturePlan already made.
        Parser  = [string]$Definition.Parser
        Source  = $Source
        Target  = $Target
        Status  = $Status
        Reason  = $Reason
        Content = $Content
    }
}

function Remove-WinEnvGeneratedProfile {
    <#
        .SYNOPSIS
        One Windows Terminal settings document with the profiles the
        application generated removed, as text.

        .DESCRIPTION
        The capture side of ExactJsonWithGeneratedProfiles. The read side
        tolerates an entry Windows Terminal's fragments and generators
        materialised into the file it co-owns; this side must not write one
        back into desired state, or the next Apply would deploy a fragment
        profile to a host whose Git for Windows, or whose WSL distribution, is
        not the one that produced it.

        An entry whose guid the payload declares is kept as the host holds it,
        which is the point of capturing: a declared profile the maintainer
        edited in the application is exactly the change being moved into
        desired state. An undeclared entry carrying a non-empty string `source`
        is dropped, because that member is how Windows Terminal records that it
        generated the entry itself. An undeclared entry without one was written
        by a person or another tool, is drift rather than generated content
        under the read side's own rule, and is captured so that the two
        directions agree about what the payload owns.

        Two host shapes are refused rather than captured, because a payload
        holding either makes every later comparison throw instead of reporting
        drift: an entry with no usable `guid`, which is dropped, and a guid
        kept more than once, which fails the whole capture and names the guid.
        Both are shapes the read side already calls drift, so nothing it
        tolerated is lost.
    #>
    param(
        [Parameter(Mandatory)][string] $DeclaredContent,
        [Parameter(Mandatory)][string] $HostContent
    )

    $declaredDocument = $DeclaredContent | ConvertFrom-Json -ErrorAction Stop
    $declaredList = Get-WinEnvJsonMember -Value (Get-WinEnvJsonMember -Value $declaredDocument -Name 'profiles') -Name 'list'
    if ($declaredList -isnot [System.Collections.IList]) {
        throw 'A payload compared as ExactJsonWithGeneratedProfiles declares no profiles.list array.'
    }

    $declared = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($entry in $declaredList) {
        $guid = [string](Get-WinEnvJsonMember -Value $entry -Name 'guid')
        if ([string]::IsNullOrWhiteSpace($guid)) {
            throw 'A declared Windows Terminal profile has no guid; this mode matches declared profiles by guid.'
        }
        [void]$declared.Add($guid)
    }

    $document = $HostContent | ConvertFrom-Json -ErrorAction Stop
    $profiles = Get-WinEnvJsonMember -Value $document -Name 'profiles'
    $list = Get-WinEnvJsonMember -Value $profiles -Name 'list'
    if ($list -isnot [System.Collections.IList]) {
        throw 'The host Windows Terminal settings file holds no profiles.list array.'
    }

    $kept = @(
        foreach ($entry in $list) {
            $guid = Get-WinEnvJsonMember -Value $entry -Name 'guid'
            # An entry with no usable guid is dropped before anything else is
            # asked of it. The read side matches declared profiles by guid and
            # throws when a declared one has none, so capturing such an entry
            # would write a payload that makes every later -Check and Apply
            # throw instead of reporting drift. Nothing is lost that the read
            # side accepted: it already counts a guidless entry as drift.
            if ($guid -isnot [string] -or [string]::IsNullOrWhiteSpace($guid)) { continue }
            if ($declared.Contains($guid)) {
                $entry
                continue
            }
            # Tested as a string rather than coerced to one, exactly as the
            # read side tests it: a `source` of 0 or false is not a
            # generator's name.
            $source = Get-WinEnvJsonMember -Value $entry -Name 'source'
            if ($source -is [string] -and -not [string]::IsNullOrWhiteSpace($source)) { continue }
            $entry
        })

    # A guid kept twice would be written into desired state as a duplicate
    # declaration, and the read side throws on one rather than reporting drift.
    # Which of the two the operator meant is not this tool's question, so the
    # capture is refused and the guid is named.
    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($entry in $kept) {
        $guid = [string](Get-WinEnvJsonMember -Value $entry -Name 'guid')
        if (-not $seen.Add($guid)) {
            throw ("The host Windows Terminal profiles use the guid '$guid' more than once; " +
                'resolve the duplicate in the application before capturing.')
        }
    }

    $profiles.list = $kept
    return ($document | ConvertTo-Json -Depth 100)
}

function Get-WinEnvCapturePlan {
    <#
        .SYNOPSIS
        What capturing one managed file from this host would do: nothing, a
        payload, or a refusal with its reason.

        .DESCRIPTION
        Decides everything and writes nothing, so the tool that does write can
        show the whole run before its single confirmation, and so every rule
        below has a fixture that needs no Windows host and no repository
        working tree.

        Drift is decided by Test-WinEnvManagedFile, the same function
        `-Check` uses, rather than by a comparison of this direction's own. Two
        comparison implementations would eventually disagree, and the failure
        would be a capture that reports a file as changed which the check
        reports as clean, or worse the reverse.

        The refusals are ordered so that the cheapest and most categorical come
        first and every one of them is decided before the host file is read:

          1. a build-conditional entry on a host whose build is undetermined,
             because no variant was selected by this host rather than guessed;
          2. runtime state, which no branch of this tool may ever write;
          3. a target this host does not have.

        Then drift, and a file that matches its payload is untouched.

        A drifted JsonSubset file is projected rather than refused. That mode
        is most of the PowerToys inventory, and refusing it left the maintainer
        with a tool that reported the change made in the application's own UI
        and could not move it into desired state. The payload declares which
        keys it owns; the host holds a value for each of them; so the payload
        that makes this host clean is the host's values arranged in the
        payload's declared shape, and ConvertTo-WinEnvJsonSubsetProjection
        derives it. Keys the payload does not declare -- the version stamps,
        timestamps and telemetry the application keeps in the same file -- are
        dropped by the projection rather than by a per-file ignore list, so
        AGENTS.md's rule that runtime state stays out of desired state is
        enforced by the payload itself. The two host shapes the projection
        cannot express are still refused, with the key path that caused it.

        The content is read last, because the final three refusals — an
        unrepresentable host directory, a leaked account path or account name,
        and a .wslconfig firewall key — are properties of the content rather
        than of the declaration.
    #>
    param(
        [Parameter(Mandatory)][hashtable] $Definition,
        [Parameter(Mandatory)][string] $RepositoryRoot,
        [AllowNull()][object] $Build = (Get-WinEnvWindowsBuild),
        [hashtable] $HostPath = (Get-WinEnvHostPath)
    )

    if ($Definition.ContainsKey('Sources') -and $null -eq $Build) {
        return New-CaptureOutcome -Definition $Definition -Status 'Refused' `
            -Reason 'this host''s Windows build is undetermined, so no source variant is selected by it'
    }

    $resolved = Resolve-WinEnvManagedFile -Definition $Definition -Build $Build
    $source = [string]$resolved.Source
    $target = Resolve-WinEnvPath -Path ([string]$resolved.Target) -HostPath $HostPath

    if ((Test-RuntimeStatePath -Path $source) -or (Test-RuntimeStatePath -Path $target)) {
        return New-CaptureOutcome -Definition $Definition -Status 'Refused' -Source $source -Target $target `
            -Reason 'the file is runtime state; AGENTS.md keeps snapshots of it out of every domain'
    }

    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        return New-CaptureOutcome -Definition $Definition -Status 'Refused' -Source $source -Target $target `
            -Reason 'the managed target does not exist on this host'
    }

    if (Test-WinEnvManagedFile -Definition $resolved -RepositoryRoot $RepositoryRoot -HostPath $HostPath) {
        return New-CaptureOutcome -Definition $Definition -Status 'Unchanged' -Source $source -Target $target
    }

    $hostText = Get-Content -LiteralPath $target -Raw -Encoding utf8
    # Both reductions read the payload as it is committed rather than as Apply
    # would expand it. Each decides on the payload's key names and list
    # lengths, and no placeholder this domain expands appears in either; the
    # values they carry are the host's, and ConvertFrom-WinEnvTemplate below
    # puts the placeholders back.
    #
    # A host file a reduction cannot express is a refusal with its reason, not
    # a crash: the run continues and reports every other selected file, and the
    # operator is told what to fix in the application or in the payload.
    if ([string]$resolved.Compare -eq 'JsonSubset') {
        $declaredText = Get-Content -LiteralPath (Join-Path $RepositoryRoot $source) -Raw -Encoding utf8
        try {
            $hostText = ConvertTo-WinEnvJsonSubsetProjection -DeclaredContent $declaredText -HostContent $hostText
        }
        catch {
            return New-CaptureOutcome -Definition $Definition -Status 'Refused' -Source $source -Target $target `
                -Reason $_.Exception.Message
        }
    }
    if ([string]$resolved.Compare -eq 'ExactJsonWithGeneratedProfiles') {
        $declaredText = Get-Content -LiteralPath (Join-Path $RepositoryRoot $source) -Raw -Encoding utf8
        try {
            $hostText = Remove-WinEnvGeneratedProfile -DeclaredContent $declaredText -HostContent $hostText
        }
        catch {
            return New-CaptureOutcome -Definition $Definition -Status 'Refused' -Source $source -Target $target `
                -Reason $_.Exception.Message
        }
    }

    $restored = ConvertFrom-WinEnvTemplate -Content $hostText -HostPath $HostPath
    $content = [string]$restored.Content

    if (@($restored.Unrepresented).Count) {
        return New-CaptureOutcome -Definition $Definition -Status 'Refused' -Source $source -Target $target `
            -Reason ("the content holds this host's " + (@($restored.Unrepresented) -join ', ') +
                ' directory, and desired state has no placeholder Apply expands there; edit the payload by hand')
    }

    if ([regex]::IsMatch($content, $script:WinEnvAccountPathPattern)) {
        return New-CaptureOutcome -Definition $Definition -Status 'Refused' -Source $source -Target $target `
            -Reason 'the content still holds an absolute account path after placeholder restoration'
    }

    $account = [string]$HostPath.UserName
    if (-not [string]::IsNullOrWhiteSpace($account)) {
        # Bounded by the characters an account name is spelled with, so a short
        # name is not matched inside an unrelated word.
        $accountPattern = '(?i)(?<![A-Za-z0-9])' + [regex]::Escape($account) + '(?![A-Za-z0-9])'
        if ([regex]::IsMatch($content, $accountPattern)) {
            return New-CaptureOutcome -Definition $Definition -Status 'Refused' -Source $source -Target $target `
                -Reason "the content names this host's account"
        }
    }

    if ($target.ToLowerInvariant().EndsWith('.wslconfig') -and
        [regex]::IsMatch($content, $script:WinEnvWslFirewallPattern)) {
        return New-CaptureOutcome -Definition $Definition -Status 'Refused' -Source $source -Target $target `
            -Reason 'the content declares a .wslconfig firewall key, which AGENTS.md adds only on explicit direction'
    }

    return New-CaptureOutcome -Definition $Definition -Status 'Captured' -Source $source -Target $target -Content $content
}

function Get-WinEnvJsonLineBracketBalance {
    <#
        .SYNOPSIS
        The net structural depth change of one line of already-serialised
        JSON: how many braces and brackets it opens minus how many it closes.

        .DESCRIPTION
        A brace or bracket written inside a string literal is not structural,
        so it is never counted; the scan tracks whether it is inside a string
        and honours a backslash escape immediately before a quote, exactly as
        JSON itself does. This is the primitive ConvertTo-WinEnvPrettyJson
        recomputes indentation from, and it is total: every character either
        toggles string state or, outside a string, is or is not one of the
        four bracket characters.
    #>
    param([Parameter(Mandatory)][AllowEmptyString()][string] $Line)

    $balance = 0
    $inString = $false
    $escaped = $false
    foreach ($ch in $Line.ToCharArray()) {
        if ($inString) {
            if ($escaped) { $escaped = $false }
            elseif ($ch -eq '\') { $escaped = $true }
            elseif ($ch -eq '"') { $inString = $false }
            continue
        }
        switch ($ch) {
            '"' { $inString = $true }
            '{' { $balance++ }
            '[' { $balance++ }
            '}' { $balance-- }
            ']' { $balance-- }
        }
    }
    return $balance
}

function ConvertTo-WinEnvPrettyJson {
    <#
        .SYNOPSIS
        One JSON document, reformatted to this repository's two-space,
        readable style.

        .DESCRIPTION
        ConvertTo-Json's own indentation is not trusted, even though it
        already happens to be two spaces on the PowerShell 7 this repository
        requires: nothing pins that to a version number, and a Windows host is
        exactly where an older Windows PowerShell could still be first on
        PATH. Every line ConvertTo-Json produced is stripped of its own
        leading whitespace and re-indented from a depth this function
        recomputes from the structural braces and brackets on that line, so
        the result never depends on what ConvertTo-Json happened to emit.

        The recomputation relies on one invariant every JSON pretty printer
        honours: a line's structural depth never goes negative mid-line, so a
        line either opens (net positive), closes (net negative), or is
        balanced (net zero, an empty `{}`/`[]` or a scalar member on its own
        line). A closing line dedents before it is printed; an opening line
        indents at its depth before the open and only increases depth for
        what follows.

        The content must already be valid JSON. Every caller captures from a
        managed file whose comparison mode is ExactJson, JsonSubset or
        ExactJsonWithGeneratedProfiles, and Test-WinEnvManagedFile already
        parses both sides under that mode before a capture plan is ever
        reached, so an unparsable document here would already have thrown
        there; this function does not add a new place capture can fail.

        Reformatting is pure whitespace, never content: ConvertTo-WinEnvCanonicalJson
        parses both sides of a comparison rather than comparing text, so this
        can never turn an Unchanged file into a false Captured one, or the
        reverse.
    #>
    param([Parameter(Mandatory)][string] $Content)

    $parsed = $Content | ConvertFrom-Json -Depth 100 -ErrorAction Stop
    $raw = $parsed | ConvertTo-Json -Depth 100

    $depth = 0
    $lines = @($raw -split "`r?`n" | Where-Object { $_.Trim() -ne '' })
    $indented = foreach ($line in $lines) {
        $trimmed = $line.Trim()
        $balance = Get-WinEnvJsonLineBracketBalance -Line $trimmed
        $lineDepth = $depth + [Math]::Min($balance, 0)
        if ($lineDepth -lt 0) { $lineDepth = 0 }
        ('  ' * $lineDepth) + $trimmed
        $depth += $balance
    }
    return ($indented -join "`n")
}

function ConvertTo-WinEnvPayloadText {
    <#
        .SYNOPSIS
        Captured content in the line endings and final-newline convention the
        payload already on disk uses, pretty-printed first when the parser is
        Json.

        .DESCRIPTION
        A host file and its payload may disagree about line endings without
        disagreeing about anything a comparison mode reads: Text normalises
        CRLF, and both JSON modes compare parsed documents. Writing the host's
        convention would therefore turn a one-key change into a whole-file
        diff and hide the change being reviewed. A payload that does not exist
        yet cannot happen on this path, because a managed file's source is
        required to exist before drift is decided at all; the LF default is
        there so this function is total rather than because it is reachable.

        A Json payload is reformatted through ConvertTo-WinEnvPrettyJson
        before that convention is applied, so the diff the operator confirms
        at the [y/N] prompt is the diff a reviewer reads afterwards rather
        than whatever the host application's own writer produced -- often one
        compact line. Every other parser keeps the host's bytes untouched,
        because desired state for those formats has never claimed to
        normalise them, and $Parser defaults to empty so a caller that does
        not pass it -- every non-Json payload -- gets exactly today's
        behaviour.
    #>
    param(
        [Parameter(Mandatory)][AllowEmptyString()][string] $Content,
        [Parameter(Mandatory)][string] $PayloadPath,
        [string] $Parser = ''
    )

    $normalized = if ($Parser -ceq 'Json') { ConvertTo-WinEnvPrettyJson -Content $Content } else { $Content }

    $crlf = $false
    $finalNewline = $true
    if (Test-Path -LiteralPath $PayloadPath -PathType Leaf) {
        $existing = Get-Content -LiteralPath $PayloadPath -Raw -Encoding utf8
        if ($null -ne $existing) {
            $crlf = $existing.Contains("`r`n")
            $finalNewline = $existing.EndsWith("`n")
        }
    }

    $text = $normalized.Replace("`r`n", "`n").TrimEnd("`n")
    if ($finalNewline) { $text += "`n" }
    if ($crlf) { $text = $text.Replace("`n", "`r`n") }
    return $text
}

function Save-WinEnvCapturedPayload {
    <#
        .SYNOPSIS
        Write one captured payload into this repository's desired state.

        .DESCRIPTION
        The only function in this module that writes to the repository rather
        than to a host. It supports ShouldProcess, so -WhatIf reports the path
        it would write and leaves the payload byte for byte as it was.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] $Plan,
        [Parameter(Mandatory)][string] $RepositoryRoot
    )

    if ([string]$Plan.Status -ne 'Captured') {
        throw "The capture plan for '$($Plan.Id)' is $($Plan.Status), not Captured."
    }

    $path = Join-Path $RepositoryRoot ([string]$Plan.Source)
    $text = ConvertTo-WinEnvPayloadText -Content ([string]$Plan.Content) -PayloadPath $path -Parser ([string]$Plan.Parser)
    if ($PSCmdlet.ShouldProcess($path, 'Write the captured payload')) {
        Write-WinEnvAtomicText -Path $path -Content $text
    }
    return $path
}

# The exact branch-naming policy tool/version-control/audit enforces
# (`^(feature|fix)/(unixlike|windows|common|repository)-[a-z0-9][a-z0-9-]*$`),
# copied rather than shared because this module has no POSIX shell to call
# into. A default branch name always satisfies it, because manifest feature
# ids are already lower-case alnum slugs; only an explicit -Branch override
# can fail it, and unlike the Unix-like commit helper -- whose branch name
# always comes from its own slugify(), never from free-form operator input --
# capture.ps1 takes that override as a literal string.
$script:WinEnvCaptureBranchNamePattern = '^(feature|fix)/(unixlike|windows|common|repository)-[a-z0-9][a-z0-9-]*$'

function Get-WinEnvCaptureBranchPlan {
    <#
        .SYNOPSIS
        Decide which branch a capture commit belongs on, without touching the
        repository.

        .DESCRIPTION
        A copy of the branch rule `tool/version-control/commit` applies (#72),
        restated here because capture.ps1 is a copy of that helper's shape
        rather than a caller of it: the Windows domain must stay authorable
        and deployable without a Unix-like host, and the maintainer's two
        clones are separate checkouts.

        On `master`, refuse: only this repository's `dev` may enter `master`,
        by pull request and merge commit, and there is no operational bypass.
        On `dev`, this capture gets a branch of its own, `$BranchName`,
        created from `origin/dev`; that requires `$BranchName` itself to
        follow this repository's branch-naming policy -- checked here rather
        than left to `tool/version-control/audit` to catch afterwards, since
        an operator-supplied `-Branch` has no other guarantee of that shape --
        requires a fetched `origin/dev` to exist at all, requires local `dev`
        to already be it -- the branch would otherwise be cut from a tree the
        capture was never computed against -- and requires `$BranchName` to be
        unused. On any other branch, the commit stays there and `$BranchName`
        is not even read: an override is documented as ignored there, so it is
        never validated there either.

        Every check here is a read, so this is safe to call while deciding
        what to report before the `[y/N]` confirmation and under -WhatIf.
        Only New-WinEnvCaptureBranch writes, and only after that confirmation.
    #>
    param(
        [Parameter(Mandatory)][string] $RepositoryRoot,
        [Parameter(Mandatory)][string] $BranchName
    )

    $branch = & git -C $RepositoryRoot symbolic-ref --quiet --short HEAD 2>$null
    $currentBranch = if ($LASTEXITCODE -eq 0 -and $branch) { [string]$branch } else { 'detached' }

    if ($currentBranch -eq 'master') {
        return [pscustomobject]@{
            Status  = 'Refused'
            Branch  = $null
            Message = 'Refusing to commit on master.'
            Detail  = "AGENTS.md: only this repository's dev may enter master, by pull request and merge commit. There is no operational bypass."
        }
    }

    if ($currentBranch -ne 'dev') {
        return [pscustomobject]@{ Status = 'Current'; Branch = $currentBranch; Message = $null; Detail = $null }
    }

    if ($BranchName -cnotmatch $script:WinEnvCaptureBranchNamePattern) {
        return [pscustomobject]@{
            Status  = 'Refused'
            Branch  = $null
            Message = "'$BranchName' does not follow this repository's branch naming policy."
            Detail  = "tool/version-control/audit requires: $script:WinEnvCaptureBranchNamePattern"
        }
    }

    & git -C $RepositoryRoot rev-parse --verify --quiet refs/remotes/origin/dev *>$null
    if ($LASTEXITCODE -ne 0) {
        return [pscustomobject]@{
            Status  = 'Refused'
            Branch  = $null
            Message = 'origin/dev is unavailable.'
            Detail  = "This tool branches from origin/dev. Run 'git fetch origin dev' first."
        }
    }

    $devSha = ([string](& git -C $RepositoryRoot rev-parse refs/heads/dev 2>$null)).Trim()
    $originDevSha = ([string](& git -C $RepositoryRoot rev-parse refs/remotes/origin/dev 2>$null)).Trim()
    if ($devSha -cne $originDevSha) {
        return [pscustomobject]@{
            Status  = 'Refused'
            Branch  = $null
            Message = 'dev is not at origin/dev.'
            Detail  = 'Fast-forward first: git fetch origin dev && git merge --ff-only origin/dev.'
        }
    }

    & git -C $RepositoryRoot show-ref --verify --quiet "refs/heads/$BranchName" *>$null
    if ($LASTEXITCODE -eq 0) {
        return [pscustomobject]@{
            Status  = 'Refused'
            Branch  = $null
            Message = "$BranchName already exists."
            Detail  = 'That capture already has a branch. Finish or delete it before starting it again.'
        }
    }

    return [pscustomobject]@{ Status = 'Create'; Branch = $BranchName; Message = $null; Detail = $null }
}

function New-WinEnvCaptureBranch {
    <#
        .SYNOPSIS
        Create and switch to the branch Get-WinEnvCaptureBranchPlan named,
        from a freshly fetched origin/dev.

        .DESCRIPTION
        The one write the branch rule makes, so the caller invokes it only
        after the operator's [y/N] confirmation and never under -WhatIf.
        origin/dev is fetched again here rather than trusted from the plan:
        time passes while the operator reads the diff, and a dev that moved
        during that wait must not be branched from silently. A failed fetch
        refuses by name and creates nothing; the same is true if origin/dev
        moved while this was waiting for an answer. Every refusal is
        returned rather than thrown, so the caller reports it exactly like
        every other capture refusal.

        Wrapped in ShouldProcess for the same reason Save-WinEnvCapturedPayload
        is: a -WhatIf caller gets back what this would have done and the
        repository is left exactly as it was found.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string] $RepositoryRoot,
        [Parameter(Mandatory)][string] $Branch
    )

    & git -C $RepositoryRoot fetch --quiet origin dev 2>$null
    if ($LASTEXITCODE -ne 0) {
        return [pscustomobject]@{
            Status  = 'Refused'
            Message = 'git fetch origin dev failed.'
            Detail  = 'Nothing was written. Fix the remote or the network and run this again.'
        }
    }

    $devSha = ([string](& git -C $RepositoryRoot rev-parse refs/heads/dev 2>$null)).Trim()
    $originDevSha = ([string](& git -C $RepositoryRoot rev-parse refs/remotes/origin/dev 2>$null)).Trim()
    if ($devSha -cne $originDevSha) {
        return [pscustomobject]@{
            Status  = 'Refused'
            Message = 'origin/dev moved while this was waiting for an answer.'
            Detail  = 'Nothing was written. Fast-forward dev and run this again.'
        }
    }

    if ($PSCmdlet.ShouldProcess($Branch, 'Create and switch to this branch from origin/dev')) {
        & git -C $RepositoryRoot switch --quiet --create $Branch refs/remotes/origin/dev 2>$null
        if ($LASTEXITCODE -ne 0) {
            return [pscustomobject]@{
                Status  = 'Refused'
                Message = "git switch --create $Branch failed."
                Detail  = 'Nothing was committed. Resolve what git reported and run this again.'
            }
        }
    }
    return [pscustomobject]@{ Status = 'Created'; Message = $null; Detail = $null }
}

function Remove-WinEnvMergedLocalBranch {
    <#
        .SYNOPSIS
        Delete every local branch already merged into origin/dev, except the
        current branch, dev and master.

        .DESCRIPTION
        The Windows-side half of the imbalance issue #103 names: GitHub
        deletes a pull request's branch on the remote once auto-merge lands
        it, but this clone's own local copy of that branch is never told and
        lingers after every -Publish cycle. This is the one function that
        clears it, called from capture.ps1's publish path so a fixture can
        drive it without a terminal or a real remote.

        `git merge-base --is-ancestor refs/heads/<branch> refs/remotes/origin/dev`
        is the entire safety rule: a branch is deleted only once git itself
        has proven every commit it carries already reached origin/dev, never
        on this function's own reading of a merge state or a pull request.
        The current branch, dev and master are excluded by name before that
        proof is even asked for, because each of them can legitimately equal
        origin/dev's tip -- dev by definition, and master or a freshly cut
        capture branch by coincidence -- and being an ancestor is not reason
        enough to delete any of the three. A branch that carries even one
        commit origin/dev does not have fails the proof and is left exactly
        alone.

        Nothing here fetches: origin/dev is read as this clone already has
        it, the same division New-WinEnvCaptureBranch draws between deciding
        and writing. The caller fetches first if it wants a current answer.
        A clone with no origin/dev at all -- never fetched -- is read as
        having nothing to prune rather than as a refusal, because this
        cleanup is strictly optional and the rest of the publish path already
        refuses on a missing origin/dev where that actually matters.

        A deletion is `git branch -D`, not `-d`: the ancestor proof above is
        already stricter than the "merged into HEAD or its upstream" question
        `-d` asks, and asking git to reapply a weaker check of its own would
        only invent a second way for a genuinely safe deletion to be refused.
        Each attempt is independent and reported on its own branch; one
        failure -- a branch checked out in another worktree, most plainly --
        is returned as `Failed` rather than thrown, so it never stops the
        branches after it from being tried.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string] $RepositoryRoot
    )

    $PSNativeCommandUseErrorActionPreference = $false

    & git -C $RepositoryRoot rev-parse --verify --quiet refs/remotes/origin/dev *>$null
    if ($LASTEXITCODE -ne 0) { return @() }

    $head = & git -C $RepositoryRoot symbolic-ref --quiet --short HEAD 2>$null
    $currentBranch = if ($LASTEXITCODE -eq 0 -and $head) { [string]$head } else { $null }
    $protected = @($currentBranch, 'dev', 'master')

    $candidateBranch = @(& git -C $RepositoryRoot for-each-ref --format='%(refname:short)' refs/heads |
            ForEach-Object { [string]$_ } | Where-Object { $_ -and $protected -cnotcontains $_ })

    $result = @()
    foreach ($branch in $candidateBranch) {
        & git -C $RepositoryRoot merge-base --is-ancestor $branch refs/remotes/origin/dev *>$null
        if ($LASTEXITCODE -ne 0) { continue }

        if (-not $PSCmdlet.ShouldProcess($branch, 'Delete this local branch, already merged into origin/dev')) { continue }

        $output = & git -C $RepositoryRoot branch -D -- $branch 2>&1
        $status = $LASTEXITCODE
        if ($status -eq 0) {
            $result += [pscustomobject]@{ Branch = $branch; Status = 'Deleted'; Detail = $null }
        }
        else {
            $detail = (@($output | ForEach-Object { [string]$_ } | Where-Object { $_ })) -join '; '
            $result += [pscustomobject]@{ Branch = $branch; Status = 'Failed'; Detail = $detail }
        }
    }
    return $result
}

# The base branch a capture publishes against. `dev` is the only branch this
# repository's source promotion lets a feature branch enter, so it is stated
# once here rather than spelled into each of the four places below that
# depend on it.
$script:WinEnvPublishBase = 'dev'

# The escape sequences a Git hook colours its output with. A pull-request body
# renders those bytes rather than the colour, so the evidence block strips
# them; the terminal keeps them, because the operator's copy is never the one
# that goes through here.
$script:WinEnvAnsiPattern = ([char]27) + '\[[0-9;]*m'

# C0 controls other than tab (\x09) and newline (\x0A, \x0D), DEL, and the C1
# controls. A pull-request body is Markdown text, not a terminal, and a stray
# byte from a truncated escape sequence or a child process's own control
# traffic has no business surviving into it.
$script:WinEnvControlCharacterPattern = '[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\x80-\x9F]'

function Invoke-WinEnvTeeCommand {
    <#
        .SYNOPSIS
        Run a native command, echo its output to the console exactly as
        before, and return a UTF-8-correct copy for a pull-request body.

        .DESCRIPTION
        PowerShell decodes a captured native command's output with
        [Console]::OutputEncoding -- the console's own codepage, not the
        encoding the command actually wrote in. git and pwsh, the only
        commands this repository tees for evidence, both write UTF-8, and on
        a host whose codepage is not already UTF-8 (CP949, CP437, ...) that
        mismatch turns a glyph such as "->" into several wrongly-decoded
        characters (mojibake) by the time PowerShell hands the line over.

        Re-encoding a wrongly-decoded line with the same (wrong) encoding and
        decoding the result as UTF-8 recovers the original bytes for a
        single-byte codepage such as CP437, but a double-byte one such as
        CP949 can already have replaced an unmappable byte pair with '?'
        before PowerShell ever sees the string -- verified empirically against
        this repository's actual CP437 and CP949 encodings -- and no amount of
        re-decoding then recovers what was already lost.

        This function therefore never asks PowerShell to decode the child's
        bytes at all: it starts the process itself and declares its stdout
        and stderr as UTF-8 on the pipes that carry them, so the text this
        function returns is correct regardless of what codepage the console,
        or [Console]::OutputEncoding, happens to be set to -- which this
        function never reads and never changes, so the operator's own console
        keeps rendering everything else exactly as its codepage always has.
        Every line is still echoed to the console with Write-Host as it
        arrives, interleaved with the other stream in whatever order the
        child actually produced it -- the same order (and the same
        buffering-driven unevenness between a child's own stdout and stderr)
        an inline `2>&1` pipe already has today.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string] $FilePath,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]] $ArgumentList
    )

    $info = [System.Diagnostics.ProcessStartInfo]::new($FilePath)
    foreach ($item in $ArgumentList) { [void]$info.ArgumentList.Add($item) }
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $info.StandardErrorEncoding = [System.Text.Encoding]::UTF8
    $info.UseShellExecute = $false

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $info
    [void]$process.Start()

    $evidence = [System.Collections.Generic.List[string]]::new()
    $outTask = $process.StandardOutput.ReadLineAsync()
    $errTask = $process.StandardError.ReadLineAsync()

    while ($null -ne $outTask -or $null -ne $errTask) {
        $pending = @($outTask, $errTask) | Where-Object { $_ }
        $winner = $pending[[System.Threading.Tasks.Task]::WaitAny($pending)]
        $fromOutput = $winner -eq $outTask
        $line = $winner.Result

        if ($null -eq $line) {
            if ($fromOutput) { $outTask = $null } else { $errTask = $null }
            continue
        }

        Write-Host $line
        [void]$evidence.Add($line)
        if ($fromOutput) { $outTask = $process.StandardOutput.ReadLineAsync() }
        else { $errTask = $process.StandardError.ReadLineAsync() }
    }

    $process.WaitForExit()
    return [pscustomobject]@{ ExitCode = $process.ExitCode; Evidence = $evidence.ToArray() }
}

function ConvertTo-WinEnvCondensedPushEvidence {
    <#
        .SYNOPSIS
        Condense a pushed evidence transcript to what a reviewer needs.

        .DESCRIPTION
        A capture's push runs .githooks/pre-push, which -- when the Windows
        checks are selected -- runs windows/tools/test.ps1's whole Pester
        suite as one of its steps. Most of that run is scaffolding nobody
        reviewing a pull request needs: discovery banners, a pass mark per
        test or container, and (because this suite's own module-level
        publish fixtures push to throwaway remotes and simulate a rejected
        push) product output from tests that passed. What a reviewer does
        need survives regardless of source: the selected-checks header, each
        check's own header line and final verdict, every skip or unverified
        marker, the suite's own "Tests Passed: ..." tally, and every line of
        any test that failed.

        Condensing is scoped to the "Windows tests" check specifically --
        entered at its own header line and left at the tally line -- because
        that is the only check whose own output is a Pester transcript.
        Everything outside that span (another check's header and verdict,
        git's own push confirmation) is untouched: it was never part of "the
        passing Pester transcript" this elides, and this function does not
        try to tell a real git remote from a fixture's throwaway one by
        content -- New-WinEnvPullRequestBody prints a note above this block
        for exactly that residual case.

        A failed test's own lines are kept by finding where Pester prints
        them: every line Pester emits for a failing test, from its "[-]"
        line through its assertion detail, carries the same bright-red
        escape (ESC[91m); the "[-]" marker itself is also checked without
        colour, so a run with colour disabled still keeps the line that
        starts the failure even if none of its detail can be identified as
        part of the same test that way.

        No "-> " line is auto-kept once inside the span, unlike outside it:
        the only "-> " header that legitimately appears inside a Pester
        transcript is capture.ps1's and Publish-WinEnvCapture's own progress
        narration ("-> pushing ...", "-> opening a pull request against
        dev", "-> arming auto-merge") printed by this suite's own
        module-level publish fixtures under test -- exactly the confusing
        noise this function exists to remove, not preserve.
    #>
    param([AllowEmptyCollection()][string[]] $Line = @())

    $result = [System.Collections.Generic.List[string]]::new()
    $insideWindowsTests = $false
    $elided = 0

    function Add-ElisionMarker([ref] $Count, [System.Collections.Generic.List[string]] $Into) {
        if ($Count.Value -le 0) { return }
        $noun = if ($Count.Value -eq 1) { 'line' } else { 'lines' }
        [void]$Into.Add("… $($Count.Value) passing $noun of the Pester transcript elided …")
        $Count.Value = 0
    }

    foreach ($raw in @($Line)) {
        $text = [string]$raw
        $plain = ($text -replace $script:WinEnvAnsiPattern, '')

        if (-not $insideWindowsTests) {
            [void]$result.Add($text)
            if ($plain -eq '→ Windows tests') { $insideWindowsTests = $true }
            continue
        }

        $keep = $plain.StartsWith('· ') -or $plain.StartsWith('Tests Passed: ') -or
            ($text -match '^\x1b\[91m') -or ($plain -match '^\[-\] ')

        if (-not $keep) {
            $elided++
            continue
        }

        Add-ElisionMarker ([ref] $elided) $result
        [void]$result.Add($text)
        if ($plain.StartsWith('Tests Passed: ')) { $insideWindowsTests = $false }
    }

    Add-ElisionMarker ([ref] $elided) $result
    return $result.ToArray()
}

function Invoke-WinEnvGh {
    <#
        .SYNOPSIS
        Run `gh` inside this repository and return its output and exit status.

        .DESCRIPTION
        `gh` has no `-C`, and every call below depends on it resolving
        `{owner}/{repo}` from the repository it is standing in, so the working
        directory is set for the call and restored afterwards. The status is
        read explicitly instead of being turned into a terminating error:
        `gh auth status` answering "not logged in" is one of the questions
        asked here, not a failure of asking it.
    #>
    param(
        [Parameter(Mandatory)][string] $RepositoryRoot,
        [Parameter(Mandatory)][string[]] $Argument
    )

    $PSNativeCommandUseErrorActionPreference = $false
    Push-Location -LiteralPath $RepositoryRoot
    try {
        $output = & gh @Argument 2>&1
        $status = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
    return [pscustomobject]@{
        ExitCode = $status
        Output   = @($output | ForEach-Object { [string]$_ })
    }
}

function New-WinEnvPublishRefusal {
    param(
        [Parameter(Mandatory)][string] $Message,
        [Parameter(Mandatory)][string] $Detail
    )

    return [pscustomobject]@{
        Status      = 'Refused'
        PullRequest = $null
        Message     = $Message
        Detail      = $Detail
    }
}

function Get-WinEnvPublishPreflight {
    <#
        .SYNOPSIS
        Everything -Publish must know before anything is written: whether the
        tools and the remote can carry this capture the rest of the way, and
        whether a pull request from this branch already exists.

        .DESCRIPTION
        A copy of `tool/version-control/commit`'s publish preflight (#72),
        restated in PowerShell for the reason Get-WinEnvCaptureBranchPlan is:
        the Windows domain must stay authorable and deployable without a
        Unix-like host, so this domain calls no POSIX helper.

        Every question here is a read, and every one of them is asked before
        the capture writes a payload, makes a commit, or pushes. The ordering
        is the cheapest and most categorical first:

          1. `gh` is not installed, so -Publish has nothing to publish with;
          2. `gh` is installed but not authenticated for github.com;
          3. the repository does not allow auto-merge -- read here because
             arming it is the last thing a publish does, and finding out then
             would mean the push and the pull request had already happened;
          4. an open pull request from this head against a base other than
             `dev`, which -Publish will not retarget;
          5. a branch this run is about to create already existing on the
             remote, which could only be published onto by forcing or merging.

        One listing answers both halves of 4: a same-head pull request already
        open against `dev` is the one to arm rather than a second one to open,
        and it is returned instead of refused. `gh pr list --head` filters by
        branch name alone and cannot be scoped to an owner, so a fork's branch
        of the same name arrives in that listing too; those rows are dropped
        here, because such a pull request is neither this branch's nor this
        tool's to touch. The rows are read as JSON in PowerShell rather than
        through `--jq`, so the filter itself is fixtured rather than delegated
        to a jq program no fixture exercises.

        No `/`-leading literal is passed to `gh`: `repos/{owner}/{repo}` and
        `.allow_auto_merge` are both relative. That is a readability choice
        rather than a safety one -- PowerShell is not an MSYS shell and
        `gh.exe` is not an MSYS program, so the POSIX-path rewriting that
        `MSYS_NO_PATHCONV` exists to suppress under Git Bash never applies to
        these arguments.
    #>
    param(
        [Parameter(Mandatory)][string] $RepositoryRoot,
        [Parameter(Mandatory)][string] $Branch,
        # The run will create $Branch rather than commit on it, so the remote
        # must not already have one by that name.
        [switch] $BranchIsNew
    )

    $PSNativeCommandUseErrorActionPreference = $false

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        return New-WinEnvPublishRefusal -Message 'gh is unavailable and -Publish needs it.' `
            -Detail "Install the GitHub CLI with 'winget install GitHub.cli', or drop -Publish and open the pull request yourself."
    }

    $auth = Invoke-WinEnvGh -RepositoryRoot $RepositoryRoot -Argument @('auth', 'status', '--hostname', 'github.com')
    if ($auth.ExitCode -ne 0) {
        return New-WinEnvPublishRefusal -Message 'gh is not authenticated for github.com.' `
            -Detail "Run 'gh auth login' first. This tool opens the pull request as you and holds no credential of its own."
    }

    $setting = Invoke-WinEnvGh -RepositoryRoot $RepositoryRoot `
        -Argument @('api', 'repos/{owner}/{repo}', '--jq', '.allow_auto_merge')
    if ($setting.ExitCode -ne 0) {
        return New-WinEnvPublishRefusal -Message "This repository's auto-merge setting could not be read." `
            -Detail ("gh api 'repos/{owner}/{repo}' failed: " + (($setting.Output -join ' ').Trim()))
    }
    if (($setting.Output -join '').Trim() -cne 'true') {
        return New-WinEnvPublishRefusal -Message 'This repository does not allow auto-merge.' `
            -Detail "Turn on 'Allow auto-merge' in the repository settings, or drop -Publish. Arming a merge that waits for Required checks is what -Publish exists to do."
    }

    $listing = Invoke-WinEnvGh -RepositoryRoot $RepositoryRoot -Argument @(
        'pr', 'list', '--head', $Branch, '--state', 'open',
        '--json', 'baseRefName,isCrossRepository,url')
    if ($listing.ExitCode -ne 0) {
        return New-WinEnvPublishRefusal -Message 'The open pull requests for this branch could not be listed.' `
            -Detail ('gh pr list failed: ' + (($listing.Output -join ' ').Trim()))
    }

    $rows = @()
    $listingText = ($listing.Output -join [Environment]::NewLine).Trim()
    if ($listingText) { $rows = @($listingText | ConvertFrom-Json) }
    # A fork's branch of this name is not this branch.
    $sameRepository = @($rows | Where-Object { -not $_.isCrossRepository })
    $foreign = @($sameRepository |
            Where-Object { [string]$_.baseRefName -cne $script:WinEnvPublishBase } |
            ForEach-Object { [string]$_.url })
    if ($foreign.Count) {
        return New-WinEnvPublishRefusal -Message "$Branch already has an open pull request with a different base." `
            -Detail ('Close or retarget it first: ' + ($foreign -join ' '))
    }
    $existing = @($sameRepository |
            Where-Object { [string]$_.baseRefName -ceq $script:WinEnvPublishBase } |
            ForEach-Object { [string]$_.url })

    if ($BranchIsNew) {
        & git -C $RepositoryRoot ls-remote --exit-code --heads origin $Branch *>$null
        if ($LASTEXITCODE -eq 0) {
            return New-WinEnvPublishRefusal -Message "origin already has $Branch." `
                -Detail 'Finish or delete that branch first; this tool neither forces nor merges onto an existing one.'
        }
    }

    return [pscustomobject]@{
        Status      = 'Ready'
        PullRequest = if ($existing.Count) { $existing[0] } else { $null }
        Message     = $null
        Detail      = $null
    }
}

function Get-WinEnvPublishCarriedCommit {
    <#
        .SYNOPSIS
        The commits this branch already carries beyond origin/dev.

        .DESCRIPTION
        Git pushes a branch, not a commit. Anything already on the branch and
        not yet on `dev` is published by the same push and merged by the same
        auto-merge, so a publish names it in the plan the operator confirms
        rather than leaving it to be discovered in the pull request. A run
        that is about to create its branch from origin/dev carries nothing,
        and this returns an empty list there by construction.
    #>
    param([Parameter(Mandatory)][string] $RepositoryRoot)

    $PSNativeCommandUseErrorActionPreference = $false
    & git -C $RepositoryRoot rev-parse --verify --quiet refs/remotes/origin/dev *>$null
    if ($LASTEXITCODE -ne 0) { return @() }

    $lines = & git -C $RepositoryRoot log --oneline refs/remotes/origin/dev..HEAD 2>$null
    if ($LASTEXITCODE -ne 0) { return @() }
    return @($lines | ForEach-Object { [string]$_ } | Where-Object { $_ })
}

function Get-WinEnvPullRequestTitle {
    <#
        .SYNOPSIS
        The title one pull request carries for the commits a capture made.

        .DESCRIPTION
        A capture makes one commit per feature, and a run that captured one
        feature has a subject that already says everything the title can. A
        run that captured several has no such subject: naming only the first
        would describe part of the change, and joining them would spell a
        subject no commit has. That run gets the general title instead, and
        the body lists the commits.
    #>
    param([Parameter(Mandatory)][AllowEmptyCollection()][string[]] $Commit)

    if (@($Commit).Count -eq 1) { return [string]$Commit[0] }
    return 'feat(windows): capture settings from the host'
}

function New-WinEnvPullRequestBody {
    <#
        .SYNOPSIS
        The pull-request body a published capture carries.

        .DESCRIPTION
        What a reviewer cannot get from the diff: which scope owns the change,
        which features and managed files this host was asked about, which
        Windows build produced the payloads -- a build-conditional payload
        means something different depending on it -- what the operator typed,
        which commits the push carries, and what the local commit reported on
        the machine the capture was made on. Nothing here is re-derived; every
        value is passed in by the caller that already answered the question.

        The evidence block is a copy of the terminal's, not an interception of
        it: the run writes every line to the terminal as it arrives and keeps a
        second copy for this. Colour escapes are stripped, because a pull
        request renders those bytes instead of the colour.

        Two evidence blocks, because this repository's two local gates check
        different things and only one of them is the Windows one. A capture
        commit touches windows/desired/**, for which `tool/dispatch/select
        commit` names no unit at all, so the pre-commit hook contributes the
        repository-wide hygiene and secret scans and nothing more. The
        domain's own checks -- check-desired-state.ps1 and test.ps1, run
        natively through pwsh.exe -- belong to `.githooks/pre-push`, and that
        output is the evidence a reviewer of this pull request cannot get any
        other way. Publishing from a Windows host and then discarding it would
        throw away the one thing that host can prove.
    #>
    param(
        [Parameter(Mandatory)][string] $Branch,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]] $Feature,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]] $ManagedFile,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]] $Commit,
        [Parameter(Mandatory)][string] $Command,
        [Parameter(Mandatory)][AllowEmptyString()][string] $Build,
        [AllowEmptyCollection()][string[]] $Carried = @(),
        [AllowEmptyCollection()][string[]] $Evidence = @(),
        [AllowEmptyCollection()][string[]] $PushEvidence = @()
    )

    $lines = [System.Collections.Generic.List[string]]::new()
    [void]$lines.Add('Scope: windows')
    [void]$lines.Add("Branch: $Branch")
    [void]$lines.Add('Feature selection: ' + (@($Feature) -join ', '))
    [void]$lines.Add('Windows build: ' + $(if ($Build) { $Build } else { 'undetermined' }))
    [void]$lines.Add("Command: $Command")

    [void]$lines.Add('')
    [void]$lines.Add('Captured managed files:')
    [void]$lines.Add('')
    foreach ($entry in @($ManagedFile)) { [void]$lines.Add("- $entry") }

    [void]$lines.Add('')
    [void]$lines.Add('Commits:')
    [void]$lines.Add('')
    foreach ($subject in @($Commit)) { [void]$lines.Add("- $subject") }

    if (@($Carried).Count) {
        [void]$lines.Add('')
        [void]$lines.Add('This branch also carries, and this pull request merges:')
        [void]$lines.Add('')
        foreach ($entry in @($Carried)) { [void]$lines.Add("- $entry") }
    }

    [void]$lines.Add('')
    [void]$lines.Add('Local commit evidence:')
    [void]$lines.Add('')
    [void]$lines.Add('```text')
    if (@($Evidence).Count) {
        foreach ($line in @($Evidence)) {
            $clean = ($line -replace $script:WinEnvAnsiPattern, '') -replace $script:WinEnvControlCharacterPattern, ''
            [void]$lines.Add($clean)
        }
    }
    else {
        [void]$lines.Add('(the commit output, once the commit runs)')
    }
    [void]$lines.Add('```')

    [void]$lines.Add('')
    [void]$lines.Add('Local push evidence:')
    [void]$lines.Add('')
    # The pre-push hook runs this very suite, whose own module-level publish
    # fixtures push to throwaway remotes and simulate a rejected push. A
    # fixture's own line can survive condensing below -- it is not this
    # function's job to tell it apart from a real push by content -- so a
    # line naming a throwaway `Temp\…\remote.git` remote here is that
    # fixture's output, not a real push.
    [void]$lines.Add('Fixture output inside this suite may mention throwaway `Temp\…\remote.git` ' +
        'remotes; a line like that surviving condensing below is a fixture, not a real push.')
    [void]$lines.Add('')
    [void]$lines.Add('```text')
    if (@($PushEvidence).Count) {
        foreach ($line in (ConvertTo-WinEnvCondensedPushEvidence -Line @($PushEvidence))) {
            $clean = ($line -replace $script:WinEnvAnsiPattern, '') -replace $script:WinEnvControlCharacterPattern, ''
            [void]$lines.Add($clean)
        }
    }
    else {
        [void]$lines.Add('(the pre-push hook''s output, once the push runs)')
    }
    [void]$lines.Add('```')

    [void]$lines.Add('')
    [void]$lines.Add('Opened by windows/tools/capture.ps1 -Publish. Auto-merge is armed, so the')
    [void]$lines.Add('merge commit happens when `Required checks` pass and not before.')

    return ($lines -join [Environment]::NewLine) + [Environment]::NewLine
}

function Publish-WinEnvCapture {
    <#
        .SYNOPSIS
        Carry the commits a capture made the rest of the way: push, one pull
        request against dev, auto-merge armed.

        .DESCRIPTION
        The writing half of -Publish, called only after the operator's single
        [y/N] and only once every refusal in Get-WinEnvPublishPreflight has
        passed. Each step stops the run where it failed and says what is left
        behind, because the honest report of a half-finished publish is worth
        more than a retry: a rejected push leaves every commit local on the
        branch, and nothing here retries with --no-verify, --force, or any
        other bypass.

        The push is a plain `git push`, so .githooks/pre-push selects and runs
        the checks the pushed content owns -- on a Windows host, the domain's
        own check-desired-state.ps1 and test.ps1 through pwsh.exe. Its output
        is copied on the way past rather than intercepted: every line still
        reaches this terminal, in order, and a second copy becomes the pull
        request's push-evidence block, which is the only place a reviewer can
        read what that host's native run reported. `gh pr merge --auto
        --merge` arms the merge rather than performing it: the wait for
        `Required checks` is the whole gate the flag exists to keep, and
        `--admin` would remove it.

        The body is therefore built here rather than passed in finished: the
        push evidence does not exist until the push has run, and on the reuse
        arm no body is built at all, because that pull request's own is left
        exactly as it is.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string] $RepositoryRoot,
        [Parameter(Mandatory)][string] $Branch,
        [Parameter(Mandatory)][string] $Title,
        # Everything New-WinEnvPullRequestBody needs except -PushEvidence,
        # splatted into it below once the push has produced that evidence.
        [Parameter(Mandatory)][hashtable] $BodyParameter,
        # The pull request Get-WinEnvPublishPreflight found already open
        # against dev from this head, if there was one. Its title and body are
        # left exactly as they are: this tool did not write them and does not
        # rewrite them.
        [AllowNull()][AllowEmptyString()][string] $PullRequest
    )

    $PSNativeCommandUseErrorActionPreference = $false

    if (-not $PSCmdlet.ShouldProcess($Branch,
            'Push this branch, open a pull request against dev and arm auto-merge')) {
        return [pscustomobject]@{ Status = 'Skipped'; Url = $null; Message = $null; Detail = $null }
    }

    Write-Host ''
    Write-Host "→ pushing $Branch"
    # Copied the way the commit is copied in capture.ps1, and for the same
    # reason: nobody reviews a pull request by scrolling somebody else's
    # terminal. Every line is re-emitted as it arrives, so the operator reads
    # the hook exactly when it speaks. Invoke-WinEnvTeeCommand, not a
    # `2>&1 | ForEach-Object` pipe, for the same encoding reason the commit
    # tee gives: git and the pre-push hook's own pwsh.exe both write UTF-8,
    # and only the evidence copy needs decoding that PowerShell's own pipe
    # cannot be trusted to get right on a non-UTF-8 host.
    # The exit code is read from the returned object, not $LASTEXITCODE:
    # once anything assigns $LASTEXITCODE explicitly, a native command run by
    # a function called afterwards (Invoke-WinEnvGh, below) stops refreshing
    # it -- confirmed empirically -- so this function never writes that
    # variable at all.
    $teed = Invoke-WinEnvTeeCommand -FilePath 'git' -ArgumentList @(
        '-C', $RepositoryRoot, 'push', '--set-upstream', 'origin', $Branch)
    $pushEvidence = @($teed.Evidence)
    if ($teed.ExitCode -ne 0) {
        return [pscustomobject]@{
            Status  = 'Refused'
            Url     = $null
            Message = 'The push was rejected.'
            Detail  = ("Every commit this run made is still local on $Branch and nothing was published. " +
                'Fix what the hook or the remote reported and push again; nothing here retries with a bypass.')
        }
    }

    $url = [string]$PullRequest
    if ($url) {
        Write-Host '→ reusing the pull request already open against dev'
    }
    else {
        Write-Host '→ opening a pull request against dev'
        $bodyPath = Join-Path ([IO.Path]::GetTempPath()) `
        ('win-env-pull-request-' + [guid]::NewGuid().ToString('N') + '.md')
        try {
            $body = New-WinEnvPullRequestBody @BodyParameter -PushEvidence @($pushEvidence)
            Write-WinEnvAtomicText -Path $bodyPath -Content $body
            $created = Invoke-WinEnvGh -RepositoryRoot $RepositoryRoot -Argument @(
                'pr', 'create', '--base', $script:WinEnvPublishBase, '--head', $Branch,
                '--title', $Title, '--body-file', $bodyPath)
        }
        finally {
            if (Test-Path -LiteralPath $bodyPath) { Remove-Item -LiteralPath $bodyPath -Force }
        }
        foreach ($line in $created.Output) { Write-Host $line }
        if ($created.ExitCode -ne 0) {
            return [pscustomobject]@{
                Status  = 'Refused'
                Url     = $null
                Message = 'The pull request could not be opened.'
                Detail  = "The commits are pushed to $Branch. Open the pull request against dev yourself."
            }
        }
        $url = [string](@($created.Output | Where-Object { $_ -cmatch '^https://\S+$' }) | Select-Object -Last 1)
        if (-not $url) {
            return [pscustomobject]@{
                Status  = 'Refused'
                Url     = $null
                Message = 'No pull-request URL came back.'
                Detail  = "The commits are pushed to $Branch. Check the pull request on GitHub."
            }
        }
    }

    Write-Host '→ arming auto-merge'
    $merge = Invoke-WinEnvGh -RepositoryRoot $RepositoryRoot -Argument @('pr', 'merge', '--auto', '--merge', $url)
    foreach ($line in $merge.Output) { Write-Host $line }
    if ($merge.ExitCode -ne 0) {
        return [pscustomobject]@{
            Status  = 'Refused'
            Url     = $url
            Message = 'Auto-merge could not be armed.'
            Detail  = "The pull request is open: $url. Arm it there, or merge it once Required checks pass."
        }
    }

    return [pscustomobject]@{ Status = 'Published'; Url = $url; Message = $null; Detail = $null }
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
