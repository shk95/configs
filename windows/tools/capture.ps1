# ConvertTo-Json formats differently on Windows PowerShell 5 -- four-space
# indentation and HTML/Unicode escaping the pretty-printer below does not
# account for -- which would silently change what a captured JSON payload
# looks like depending on which PowerShell happened to be first on PATH.
# setup.ps1 already requires 7; this asks PowerShell itself to refuse to
# start rather than run under the one version this script was not verified
# against.
#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess)]
param(
    # Which managed files to consider. Neither switch is a deployment
    # selection: -Feature narrows this run to the files a feature owns and
    # -Id to named managed files, and the two intersect when both are given.
    # With neither, the run considers what this host recorded as applied, and
    # everything the manifest declares when it has applied nothing.
    [string[]] $Feature,
    [string[]] $Id,
    # Overrides the branch this run creates from origin/dev when invoked on
    # dev. Ignored on any other branch, where the commit stays where it is.
    [string] $Branch,
    # Carry the commits this run makes the rest of the way, under the same
    # single confirmation: push the branch with its hooks, open one pull
    # request against dev, arm auto-merge, print the URL and stop. It removes
    # ceremony, not a gate.
    [switch] $Publish
)

# Move a change made in an application's own UI into desired state.
#
# The reverse of Apply, and deliberately not a second implementation of it.
# Drift is decided by Test-WinEnvManagedFile, the same function bootstrap.ps1
# -Check uses; which payload a build-conditional entry has is decided by
# Resolve-WinEnvManagedFile; what a capture would write, and every refusal, is
# decided by Get-WinEnvCapturePlan in windows/src/WinEnv.psm1, where the rules
# have fixtures. This script owns the parts that need a terminal and a Git
# repository: selection, the diff, one confirmation, and the commit.
#
# It is a copy of the shape of tool/version-control/commit, not a caller of it.
# The Windows domain must stay authorable and deployable without a Unix-like
# host, and the maintainer's Windows clone is a separate checkout, so a POSIX
# shell helper is not available to it. The guards are therefore restated here:
# it refuses on master, refuses a dirty index, refuses to touch a payload that
# already has uncommitted changes, and never bypasses a hook. The branch rule
# is restated too, in Get-WinEnvCaptureBranchPlan and New-WinEnvCaptureBranch:
# on dev this run gets feature/windows-capture-<feature> of its own, cut from
# a freshly fetched origin/dev, so a commit here is never left stranded on
# dev's own protected branch. There is no unattended mode: no -Yes, no -Force,
# no environment override.
#
# -Publish is that copy carried one step further (#72's --publish): the same
# single confirmation also pushes the branch, opens one pull request against
# dev, and arms auto-merge. It removes ceremony rather than a gate. The
# pre-push hook still runs and its rejection leaves every commit local,
# branch protection still requires Required checks and an up-to-date base, and
# the merge still happens on GitHub's side once those pass. This script prints
# the pull-request URL and stops: it never waits on CI and never merges. Its
# refusals, the pull-request body and the writing half live in
# Get-WinEnvPublishPreflight, New-WinEnvPullRequestBody and
# Publish-WinEnvCapture, where they have fixtures.
#
# Nothing on the host is written. The managed targets are read and nothing
# else; every write goes to this repository's desired state, and only after
# the confirmation.
#
#   .\windows\tools\capture.ps1                     # every applied feature
#   .\windows\tools\capture.ps1 -Feature powertoys  # one feature
#   .\windows\tools\capture.ps1 -Id windowsTerminal # one managed file
#   .\windows\tools\capture.ps1 -Publish            # commit, push, pull request, auto-merge
#   .\windows\tools\capture.ps1 -WhatIf             # decide and diff, write nothing

$ErrorActionPreference = 'Stop'
# PowerShell 7.4 and newer turn a non-zero native exit status into a
# terminating error while $ErrorActionPreference is Stop. Several questions
# below are put to Git precisely because a non-zero status is one of their
# answers: an unset core.hooksPath, a detached HEAD, and a diff that found a
# difference all exit 1 and none of them is a failure. The status is read
# explicitly at every call site instead.
$PSNativeCommandUseErrorActionPreference = $false
$windowsRoot = Split-Path -Parent $PSScriptRoot
$repositoryRoot = Split-Path -Parent $windowsRoot
$desiredStateRoot = Join-Path $windowsRoot 'desired'
Import-Module (Join-Path $windowsRoot 'src\WinEnv.psm1') -Force

function Write-Refusal {
    param(
        [Parameter(Mandatory)][string] $Message,
        [Parameter(Mandatory)][string] $Detail
    )

    Write-Host "✗ $Message" -ForegroundColor Red
    Write-Host "  $Detail"
}

function Stop-Capture {
    param(
        [Parameter(Mandatory)][string] $Message,
        [Parameter(Mandatory)][string] $Detail
    )

    Write-Refusal -Message $Message -Detail $Detail
    exit 1
}

function Invoke-GitCommand {
    # Captured output, for the questions this script asks Git. The commit
    # itself deliberately does not go through here: a hook's evidence lines and
    # its closing unverified summary are the operator's to read, and capturing
    # them would decide for the operator that they do not matter.
    param(
        [Parameter(Mandatory)][string[]] $Argument,
        [switch] $AllowFailure
    )

    $output = & git -C $repositoryRoot @Argument 2>&1
    $status = $LASTEXITCODE
    if ($status -ne 0 -and -not $AllowFailure) {
        throw "git $($Argument -join ' ') failed: $($output -join [Environment]::NewLine)"
    }
    if ($status -ne 0) { return @() }
    return @($output | ForEach-Object { [string]$_ } | Where-Object { $_ })
}

function Get-RepositoryRelativePath {
    param([Parameter(Mandatory)][string] $Source)

    return 'windows/desired/' + $Source.Replace('\', '/')
}

$manifest = Get-WinEnvManifest -Path (Join-Path $desiredStateRoot 'manifest.json')
$hostPath = Get-WinEnvHostPath
$hostBuild = Get-WinEnvWindowsBuild
# A host with no LOCALAPPDATA has no recorded selection to read, and asking
# for one would fail on the path join rather than on the question.
$state = if ([string]::IsNullOrWhiteSpace([string]$hostPath.LocalAppData)) {
    $null
}
else {
    Get-WinEnvState -Path (Join-Path ([string]$hostPath.LocalAppData) 'win-env\state.json')
}
$appliedFeature = Get-WinEnvAppliedFeature -Manifest $manifest -State $state

$declaredFeature = Get-WinEnvFeatureId -Manifest $manifest
$requestedFeature = @(Expand-WinEnvFeatureArgument -Value $Feature)
$requestedId = @(Expand-WinEnvFeatureArgument -Value $Id)

foreach ($name in $requestedFeature) {
    if ($declaredFeature -notcontains $name) {
        Stop-Capture -Message "Unknown feature '$name'." -Detail "The manifest declares: $($declaredFeature -join ', ')."
    }
}
$declaredId = @($manifest.ManagedFiles | ForEach-Object { [string]$_.Id })
foreach ($name in $requestedId) {
    if ($declaredId -notcontains $name) {
        Stop-Capture -Message "Unknown managed file '$name'." -Detail "The manifest declares: $($declaredId -join ', ')."
    }
}

# Feature dependencies are not resolved here, and that is the difference
# between a selection and a filter. terminal requires font and zellij so that a
# deployment of it is coherent; capturing the files terminal owns needs neither
# of the other two, and widening the filter would put a file the operator did
# not ask about into the diff.
if ($requestedFeature.Count -or $requestedId.Count) {
    $considered = @($manifest.ManagedFiles | Where-Object {
            ($requestedFeature.Count -eq 0 -or $requestedFeature -contains [string]$_.Feature) -and
            ($requestedId.Count -eq 0 -or $requestedId -contains [string]$_.Id)
        })
    $consideredFeature = @($considered | ForEach-Object { [string]$_.Feature })
    $selected = @($declaredFeature | Where-Object { $consideredFeature -contains $_ })
}
else {
    $selected = if ($state) { @($appliedFeature) } else { $declaredFeature }
    $considered = @($manifest.ManagedFiles | Where-Object { $selected -contains [string]$_.Feature })
}

Write-Host 'win-env capture summary'
Write-Host ('  selected: ' + (@($selected) -join ', '))
$buildText = if ($null -ne $hostBuild) { [string]$hostBuild } else { 'undetermined' }
Write-Host "  Windows build: $buildText"

$plans = @($considered | ForEach-Object {
        Get-WinEnvCapturePlan -Definition $_ -RepositoryRoot $desiredStateRoot -Build $hostBuild -HostPath $hostPath
    })

$planned = @($plans | Where-Object Status -eq 'Captured')
$unchanged = @($plans | Where-Object Status -eq 'Unchanged')
$refused = @($plans | Where-Object Status -eq 'Refused')

# The payload text each captured plan would produce, rendered once and reused
# for the diff and for the write. A plan whose text equals the payload already
# on disk is not a commit: the file drifted under its comparison mode but the
# difference is one desired state does not express -- a directory spelled in
# another case, most plainly -- so there is nothing to stage. Saying so here is
# what keeps the run out of the commit path, where an empty `git add` makes
# `git commit` exit 1 and the failure reads as a hook rejecting the change.
$rendered = @{}
$captured = @()
$inexpressible = @()
foreach ($plan in $planned) {
    $payloadPath = Join-Path $desiredStateRoot $plan.Source
    $text = ConvertTo-WinEnvPayloadText -Content ([string]$plan.Content) -PayloadPath $payloadPath -Parser ([string]$plan.Parser)
    $current = if (Test-Path -LiteralPath $payloadPath -PathType Leaf) {
        Get-Content -LiteralPath $payloadPath -Raw -Encoding utf8
    }
    else {
        $null
    }
    if ($null -ne $current -and $current -ceq $text) {
        $inexpressible += $plan
        continue
    }
    $rendered[[string]$plan.Id] = $text
    $captured += $plan
}

foreach ($plan in $captured) { Write-Host "  captured: $($plan.Id) -> $($plan.Source)" }
if ($unchanged.Count) { Write-Host ('  unchanged: ' + (@($unchanged | ForEach-Object { $_.Id }) -join ', ')) }
foreach ($plan in $inexpressible) {
    Write-Refusal -Message "no change to commit: $($plan.Id)" `
        -Detail ('the host file drifted, but the payload this capture produces is the one already ' +
            'committed, so desired state cannot express the difference; reconcile it in the application or by hand')
}
foreach ($plan in $refused) { Write-Refusal -Message "refused: $($plan.Id)" -Detail $plan.Reason }

if (-not $captured.Count) {
    Write-Host ''
    Write-Host 'Nothing to capture. No payload was written and no commit was made.'
    exit 0
}

# One commit per feature: a feature is the unit this manifest already owns
# packages, payloads and selection by, and a capture of two of them is two
# reviewable changes rather than one. Computed here, ahead of the Git
# refusals below, because the default branch name is derived from it.
$capturedFeature = @($captured | ForEach-Object { [string]$_.Feature })
$features = @($declaredFeature | Where-Object { $capturedFeature -contains $_ })

# Git refusals, all of them before anything is written, so a refused run leaves
# the clone exactly as it was found. The branch rule is Get-WinEnvCaptureBranchPlan
# (#72's copy): master refuses outright, dev gets a branch of its own cut from
# origin/dev, and any other branch commits where it is. Every check it makes is
# a read, so this is safe here, before the diff and the confirmation.
$defaultBranchName = 'feature/windows-capture-' + ($features -join '-')
$candidateBranchName = if ($Branch) { $Branch } else { $defaultBranchName }
$branchPlan = Get-WinEnvCaptureBranchPlan -RepositoryRoot $repositoryRoot -BranchName $candidateBranchName
if ($branchPlan.Status -eq 'Refused') {
    Stop-Capture -Message $branchPlan.Message -Detail $branchPlan.Detail
}

# A detached HEAD is a place to commit but not a branch to publish, and the
# push below would have nothing to name. Refused here rather than left to git,
# which would only say so after the commits existed.
if ($Publish -and $branchPlan.Branch -ceq 'detached') {
    Stop-Capture -Message 'HEAD is detached, so there is no branch to publish.' `
        -Detail 'Switch to dev or to the feature branch this capture belongs on.'
}

if (@(Invoke-GitCommand -Argument @('diff', '--cached', '--name-only')).Count) {
    Stop-Capture -Message 'The index already holds staged changes.' `
        -Detail 'This tool commits only the payloads it captures. Commit or unstage the rest first.'
}

$relativePath = @{}
foreach ($plan in $captured) {
    $relative = Get-RepositoryRelativePath -Source $plan.Source
    $relativePath[[string]$plan.Id] = $relative
    if (@(Invoke-GitCommand -Argument @('status', '--porcelain', '--', $relative)).Count) {
        Stop-Capture -Message "$relative already has uncommitted changes." `
            -Detail 'This tool commits only the payloads it captures. Commit or restore that file first.'
    }
}

# gh and the remote are consulted only when -Publish asks for them, and only
# ever read here: nothing in the preflight writes, so a refusal from it leaves
# the clone exactly as every refusal above does. It runs before the diff and
# the confirmation so that "the commits were made and then the last step
# failed" is a refusal that costs nothing.
$publishBranch = [string]$branchPlan.Branch
$existingPullRequest = $null
if ($Publish) {
    $preflight = Get-WinEnvPublishPreflight -RepositoryRoot $repositoryRoot -Branch $publishBranch `
        -BranchIsNew:($branchPlan.Status -eq 'Create')
    if ($preflight.Status -eq 'Refused') {
        Stop-Capture -Message $preflight.Message -Detail $preflight.Detail
    }
    $existingPullRequest = [string]$preflight.PullRequest
}

# One commit subject per feature, in the order the commits below are made, so
# the plan, the pull-request title and the pull-request body all name the same
# commits rather than each deriving them again.
$commitSubject = @{}
foreach ($featureId in $features) {
    $commitSubject[$featureId] = "feat(windows): capture $featureId settings from the host"
}
$commitSubjectLine = @($features | ForEach-Object { $commitSubject[$_] })

# What the operator typed, rebuilt from the bound parameters rather than from
# the raw command line: every value here has already been validated against
# the manifest or the branch-naming policy.
$invocationPart = @('windows/tools/capture.ps1')
if ($requestedFeature.Count) { $invocationPart += '-Feature ' + ($requestedFeature -join ',') }
if ($requestedId.Count) { $invocationPart += '-Id ' + ($requestedId -join ',') }
if ($Branch) { $invocationPart += "-Branch $Branch" }
if ($Publish) { $invocationPart += '-Publish' }
$invocation = $invocationPart -join ' '

$carriedCommit = @()
$pullRequestTitle = $null
$pullRequestPreview = $null
$bodyParameter = @{}
if ($Publish) {
    # Read before the branch is created and before any commit, so this lists
    # what the branch already carried and nothing this run adds. A run that is
    # about to cut its branch from origin/dev carries nothing.
    $carriedCommit = @(Get-WinEnvPublishCarriedCommit -RepositoryRoot $repositoryRoot)
    $pullRequestTitle = Get-WinEnvPullRequestTitle -Commit $commitSubjectLine
    # Everything the body says that is already known before the run writes
    # anything. The plan renders it with both evidence blocks still empty;
    # Publish-WinEnvCapture renders it again after the push, which is the only
    # moment the pre-push hook's output exists.
    $bodyParameter = @{
        Branch      = $publishBranch
        Feature     = $features
        ManagedFile = @($captured | ForEach-Object { "$($_.Id) ($($relativePath[[string]$_.Id]))" })
        Commit      = $commitSubjectLine
        Command     = $invocation
        Build       = $buildText
        Carried     = $carriedCommit
    }
    $pullRequestPreview = New-WinEnvPullRequestBody @bodyParameter
}

# The branch this run will land on, reported before the diff so the operator
# reads it as part of the plan rather than discovering it from `git branch`
# afterwards.
Write-Host ''
if ($branchPlan.Status -eq 'Create') {
    Write-Host "  branch: $($branchPlan.Branch) (new, from origin/dev)"
}
else {
    Write-Host "  branch: $($branchPlan.Branch) (current)"
}

# What will and will not gate the commit, said plainly. The repository's hooks
# are POSIX shell scripts and Git for Windows runs them natively on the
# maintainer's host, but a clone with core.hooksPath unset runs none of them
# and a host without sh runs none either, so this reports what it can decide
# rather than claiming a gate ran.
$hooksPath = @(Invoke-GitCommand -Argument @('config', '--get', 'core.hooksPath') -AllowFailure)
$hooksConfigured = $hooksPath.Count -and $hooksPath[0] -eq '.githooks'
Write-Host ''
if ($hooksConfigured) {
    Write-Host '  pre-commit checks: core.hooksPath is .githooks, so Git will try to run them.'
    Write-Host '    They are POSIX shell scripts. Read the hook output under the commit below'
    Write-Host '    rather than assuming it ran; a host with no sh runs no check.'
}
else {
    $current = if ($hooksPath.Count) { $hooksPath[0] } else { 'unset' }
    Write-Host "  pre-commit checks: none. core.hooksPath is $current, not .githooks."
    Write-Host '    Nothing will check this commit locally. Set the hooks up first if you want that gate.'
}

# The diff comes from a candidate outside the working tree, so refusing at the
# confirmation leaves nothing behind to clean up.
#
# Created and removed through .NET rather than New-Item and Remove-Item: those
# two honour -WhatIf, so under -WhatIf the run would announce a temporary
# directory as if it were part of the change, then fail to make one, then leave
# what it did make behind. The staging directory is this script's own
# scaffolding and is never the operation the operator is being asked about.
$stagingRoot = Join-Path ([IO.Path]::GetTempPath()) ('win-env-capture-' + [guid]::NewGuid().ToString('N'))
try {
    [void][IO.Directory]::CreateDirectory($stagingRoot)
    foreach ($plan in $captured) {
        $payloadPath = Join-Path $desiredStateRoot $plan.Source
        $candidate = Join-Path $stagingRoot ([string]$plan.Id)
        Write-WinEnvAtomicText -Path $candidate -Content $rendered[[string]$plan.Id]
        Write-Host ''
        Write-Host "--- $($relativePath[[string]$plan.Id])"
        & git -C $repositoryRoot --no-pager diff --no-index --no-color -- $payloadPath $candidate
    }

    if ($Publish) {
        Write-Host ''
        Write-Host '  publish: one pull request against dev, auto-merge armed'
        if ($carriedCommit.Count) {
            Write-Host '  this branch also carries, and will publish and merge:'
            foreach ($line in $carriedCommit) { Write-Host "    $line" }
        }
        if ($existingPullRequest) {
            # The pull request already exists and this run does not rewrite it.
            # Printing the body it would have written would promise a reviewer
            # something nobody is going to read.
            Write-Host "  pull request: $existingPullRequest (existing; title and body unchanged)"
        }
        else {
            Write-Host "  pull request title: $pullRequestTitle"
            Write-Host '  pull request body:'
            foreach ($line in ($pullRequestPreview.TrimEnd() -split "`r?`n")) { Write-Host "    $line" }
        }
        Write-Host '  commands:'
        if ($branchPlan.Status -eq 'Create') {
            Write-Host "    git switch --create $publishBranch origin/dev"
        }
        Write-Host "    git push --set-upstream origin $publishBranch"
        if ($existingPullRequest) {
            Write-Host "    gh pr merge --auto --merge $existingPullRequest"
            Write-Host '    (that pull request is already open against dev; no second one is opened)'
        }
        else {
            Write-Host ("    gh pr create --base dev --head $publishBranch --title '$pullRequestTitle' --body-file <body>")
            Write-Host '    gh pr merge --auto --merge <the pull request that opens>'
        }
    }

    if ($WhatIfPreference) {
        Write-Host ''
        Write-Host 'What if: nothing was written and no commit was made.'
        exit 0
    }

    Write-Host ''
    $question = if ($Publish) {
        'Write these payloads, commit and publish? [y/N]'
    }
    else {
        'Write these payloads and commit? [y/N]'
    }
    $answer = Read-Host $question
    if ($answer -cne 'y' -and $answer -cne 'Y') {
        Write-Host 'Aborted. Nothing was written.'
        exit 1
    }
}
finally {
    if ([IO.Directory]::Exists($stagingRoot)) { [IO.Directory]::Delete($stagingRoot, $true) }
}

# The branch comes first, while the tree still matches HEAD, so switching
# cannot disturb a payload that has not been written yet. Local dev is
# already known to equal origin/dev (Get-WinEnvCaptureBranchPlan refused
# otherwise), so this switch changes no file the checks above already read.
if ($branchPlan.Status -eq 'Create') {
    $created = New-WinEnvCaptureBranch -RepositoryRoot $repositoryRoot -Branch $branchPlan.Branch
    if ($created.Status -ne 'Created') {
        Stop-Capture -Message $created.Message -Detail $created.Detail
    }
}

# A second reader for the commit output when -Publish will put it in a pull
# request. It is a copy and never an interception: every line still reaches
# this terminal, in order, exactly as the unpublished path prints it, because
# nobody reviews a pull request by scrolling somebody else's terminal.
$commitEvidence = [System.Collections.Generic.List[string]]::new()

# The features whose commit this run has already made, so a rejection part way
# through a multi-feature capture can name what it left behind.
$committedFeature = @()

foreach ($featureId in $features) {
    $group = @($captured | Where-Object { [string]$_.Feature -eq $featureId })
    $paths = @()
    foreach ($plan in $group) {
        [void](Save-WinEnvCapturedPayload -Plan $plan -RepositoryRoot $desiredStateRoot)
        $paths += $relativePath[[string]$plan.Id]
    }

    [void](Invoke-GitCommand -Argument (@('add', '--') + $paths))

    $subject = $commitSubject[$featureId]
    $body = @(
        'Captured from this host''s managed targets by windows/tools/capture.ps1,',
        'with placeholders restored. Managed files:',
        ''
    ) + @($group | ForEach-Object { "- $($_.Id) ($($_.Source))" })

    Write-Host ''
    if ($Publish) {
        # Invoke-WinEnvTeeCommand, not a `2>&1 | ForEach-Object` pipe: git
        # writes UTF-8, and PowerShell's own pipe would decode it with the
        # console's codepage instead, mislabelling every non-ASCII glyph the
        # commit's hooks print. The console itself is untouched -- only the
        # copy that becomes this pull request's evidence is decoded correctly.
        #
        # The exit code is read from the returned object, not $LASTEXITCODE:
        # once anything assigns $LASTEXITCODE explicitly, a native command run
        # by a function called afterwards (Invoke-WinEnvGh, later, inside
        # Publish-WinEnvCapture) stops refreshing it -- confirmed empirically
        # -- so this script never writes that variable at all.
        $teed = Invoke-WinEnvTeeCommand -FilePath 'git' -ArgumentList @(
            '-C', $repositoryRoot, 'commit', '-m', $subject, '-m', ($body -join [Environment]::NewLine))
        $commitEvidence.AddRange([string[]]$teed.Evidence)
        $commitExitCode = $teed.ExitCode
    }
    else {
        # No capture, no pipe, no redirection: a hook's evidence lines and its
        # closing unverified summary are the operator's to read.
        & git -C $repositoryRoot commit -m $subject -m ($body -join [Environment]::NewLine)
        $commitExitCode = $LASTEXITCODE
    }
    if ($commitExitCode -ne 0) {
        Write-Refusal -Message 'The commit was rejected.' `
            -Detail 'The captured payloads are left staged. Fix what the hook reported, or discard them with:'
        Write-Host ("    git restore --staged --worktree -- " + ($paths -join ' '))
        # One commit per feature means a rejection can arrive with earlier
        # features already committed. An operator who followed the recovery
        # above without being told would be left holding commits this run made
        # and never named.
        if ($committedFeature.Count) {
            Write-Host '  This run already committed, and these commits remain on the branch:'
            foreach ($done in $committedFeature) { Write-Host "    $($commitSubject[$done])" }
        }
        if ($branchPlan.Status -eq 'Create') {
            Write-Host "  You are now on $publishBranch, which this run created."
        }
        exit 1
    }
    $committedFeature += $featureId
}

if ($Publish) {
    $bodyParameter['Evidence'] = @($commitEvidence)
    $published = Publish-WinEnvCapture -RepositoryRoot $repositoryRoot -Branch $publishBranch `
        -Title $pullRequestTitle -PullRequest $existingPullRequest -BodyParameter $bodyParameter
    if ($published.Status -ne 'Published') {
        Write-Refusal -Message $published.Message -Detail $published.Detail
        exit 1
    }

    Write-Host ''
    Write-Host $published.Url
    exit 0
}

Write-Host ''
Write-Host ("Captured $($captured.Count) managed file(s) in $($features.Count) commit(s). " +
    'Nothing was pushed.')
exit 0
