# Contributing

This is the workflow for people and tools. `AGENTS.md` contains stable
judgement and safety rules, `docs/policy/architecture.md` defines domain ownership,
and `README.md` contains usage.

Repository text is English because the repository is public.

## Prepare a clone

`tool/configs help` lists repository operations intended for a person or an
agent acting for one. The command forwards to the implementation under
`tool/`; hooks and CI invoke those implementations directly. Windows host
commands remain under `windows/win-env.ps1`, and Unix-like host commands use
the `Justfile`.

```sh
tool/configs setup
tool/configs setup --fix
tool/configs doctor
```

`tool/configs setup` changes only the clone-local hooks setting and only with `--fix`.
`tool/configs doctor` is read-only. `tool/configs doctor` also prints a one-line
summary of the outcomes the hooks have recorded on this clone;
`tool/configs hook-evidence` prints the full count. Pass `unixlike`,
`windows`, `common`, or `repository` to check only that scope; omit the
scope for a complete host inventory. A missing foreign-platform capability
does not block scoped work.

## Classify the change

Every change belongs to one of these scopes:

- `unixlike`: Nix, Home Manager, NixOS, WSL guest, or nix-darwin behavior.
- `windows`: native Windows desired state and reconciliation.
- `common`: explicitly platform-neutral material with its own contract.
- `adopt`: an explicit copy or pinned import from one domain into another.
- `repository`: version-control policy, hooks, CI dispatch, or reusable agent
  workflow support with no configuration or deployment output.

`repository` is a governance scope, not a fourth configuration domain. It has
no release tag and must not contain platform behavior that belongs to
`unixlike`, `windows`, or `common`.

One scope per commit, and therefore per branch and pull request. A commit's
scope is the classifier's answer over the paths it touches, and the release
tag, the CI lanes and the right to change a path all follow from it. The
subject's scope is a different thing: it names the domain the change
describes, so `docs(windows)` over `docs/policy/architecture.md`, which classifies
`repository`, is correct. If a common change and its platform adoption are
both needed, land them separately so neither release is synchronously coupled
to the other.

## Branch and commit flow

Start from local dev and select the local master snapshot to incorporate.
If master adds history, merge it with `git merge --no-ff <master-SHA>` in a
dev-based linked topic worktree. The merge's first parent continues the dev
lane and its second parent is the selected master snapshot. Resolve and check
the result there before exact-SHA integration. Remote fetching is an explicit
synchronization operation, not task pickup.

Create a dedicated topic worktree from local dev:

```sh
tool/configs worktree new repository-example feature
```

The helper neither fetches nor authenticates. One source commit belongs to one
scope; a topic is one coherent same-scope result. Dev can accumulate multiple
scopes for later push and promotion. Primary is for inspection and integration;
source commits, including conflict resolution, are made in the topic worktree.
Do not author directly on master or rebase published work.

Keep dev and master on their own first-parent paths. Fast-forward integration
advances dev to a verified dev-based candidate; it never advances dev directly
to master or to a master promotion merge. After promotion, continue from dev
and reflect master at the next explicit work/promotion synchronization.

## Local integration and completion

1. One integrator handles local dev at a time. Confirm primary dev is clean and
   has no merge/rebase operation in progress.
2. In the candidate worktree, record current dev SHA and merge that dev when
   needed. Resolve any conflicts there. Do not refresh every worker whenever
   another task completes.
3. Run the relevant checks on the final combined result. Commit any remaining
   source change, then verify the exact final SHA and a clean candidate.
4. Return to primary. Confirm dev still equals the recorded base and remains
   clean; otherwise stop and return to the candidate for review/verification.
5. Advance dev with `git merge --ff-only <verified-full-SHA>`.
6. Record the result, SHA, verification, unavailable items and push status.
   Local completion requires the agreed scope's evidence, not a remote PR.

The command in step 5 does not prove verification or cleanliness on its own.
Its input is the exact candidate reviewed above. Push later when requested;
ordinary push rejection stops without changing completed local work. Never
retry an ordinary push with force. Domain release/activation remains separate.

Routine desired-state edits use `tool/configs commit` in a dedicated topic
worktree. It confirms an edit and commits locally with hooks. `--dry-run`
writes nothing; `--publish` and `prune` are retired and refuse. The helper
does not fetch, branch, push, open a PR or request auto-merge.

Domain releases use immutable annotated tags. The target commit must be
reachable from `master`. The annotation records the domain and reports
evaluation, build, and native-runtime evidence separately, including explicit
`unavailable` or `not applicable` values. A Windows annotation reports them
once for each host the release speaks for, in a block opened by
`Host: <label>`. Unix-like provider and `common` annotations report them
once at domain level; neither certifies a private Unix-like host.
`tool/configs plan-release` prints the template, and
`tool/configs audit` refuses a tag that departs from it. A Windows
label is lowercase letters, digits and hyphens and names a kind of host,
never a machine; keep machine names, account names
and machine identifiers out of the references too, because a pushed tag
cannot be edited. A host whose check failed is not released around. Create
and push a tag only when the user explicitly requests those mutations. Create
no GitHub Release: the annotation is the whole record. Activation and Windows
Apply happen after release and are not implied by a tag.

For agent-assisted work, invoke `run-version-control-workflow`. Its canonical
Agent Skills implementation is under `.agents/skills/`; model-specific
discovery files are adapters only. Audit and release planning are read-only by
default. This document remains the human fallback and the contract the skill
executes.

### zellij overlay

This subsection is disposable and carries the tag
`PROV unixlike/zellij-combining-marks`, so it is deleted with the measure it
describes.

`unixlike/modules/programs/zellij/module.nix` carries upstream zellij-org/zellij#5500
for Darwin until nixpkgs ships a zellij whose source already has the fix;
`docs/provisional/unixlike/zellij-combining-marks.md` registers the measure and
names the condition that ends it. The overlay names no zellij version: it
applies the range with no fuzz to whatever zellij the lock brings in, so a
`unixlike/flake.lock` refresh that moves zellij is the ordinary one commit,
`tool/configs commit flake refresh`.

The flake checks `zellij-combining-marks`,
`zellij-combining-marks-refuses-a-patched-tree` and
`zellij-combining-marks-refuses-a-stale-vendor`, declared beside the overlay,
are what judge that refresh. `unixlike/tool/checks/test` builds them on every
system, so the refresh's pre-push and the merge gate refuse a lock whose
zellij the range no longer applies to; `just zellij-patch-check` builds the
first alone, and `just zellij-patch-check v<ver>` applies the range to an
upstream tag before a refresh brings it in. When they refuse:

1. Rebase the range in a fork and repoint the overlay's `url` and `hash` in a
   `fix(unixlike):` commit made before the refresh. The pin is the pull
   request's commit range `base...head` in the overlay's compare URL; a
   re-pin to a branch that gained commits moves the head, and a rebase moves
   both.
2. Refresh the lock again after it.

After a refresh that moves zellij, `just darwin-build` on the Mac and the
reproduction in `docs/policy/decisions/unixlike/zellij-patched-on-darwin-until-upstream.md`
are the build and runtime evidence; the checks prove only that the range
applies.

`.github/workflows/zellij-upstream-5500.yml` watches the pull request and
reports a bump or a merge as an issue. GitHub runs a `schedule` only from the
default branch, so the watcher does nothing until this file reaches `master`
through the next promotion; before that its shell body is run by hand with
`DRY_RUN=1`.

## Agent roles and handoff

Use project-local skills. plan-work inspects existing plans and defines
acceptance when needed. execute-work pins local dev and the reviewed plan,
works in its dedicated worktree and records actual evidence. integrate-work
reviews a local candidate and integrates its verified SHA sequentially.
Explicit user Git authorization carries through the agreed task.

Use `tool/configs session start <spec-path-or-> <lane>` for a useful local
checkpoint. Before interruption, `session checkpoint suspended` records the
goal, exact state, evidence, unfinished work and next step. A checkpoint is
neither a heartbeat nor proof of delivery. Changed acceptance returns to
planning; uncertain liveness does not authorize cleanup.

inspect-work reads requested local handoffs. Remote status is optional and
must be relevant to an explicit remote operation. reclaim-workspaces reviews
unpushed/unique commits and tracked, untracked and ignored data before any
requested non-force removal. Do not read notes/ content. Keep useful old
worktrees; a clean diff is not preservation evidence. No automatic pruning.

## GitHub integration

Dev is local integration followed by ordinary remote synchronization. It has
no PR, required-check or conversation-resolution admission gate. Administrator
enforcement and force-push/deletion prohibitions remain enabled.

Master retains PR admission, strict Required checks, resolved conversations,
administrator enforcement and force-push/deletion prohibitions. Required
approvals remain zero; merge commits are the only enabled merge method.
General development uses same-repository dev to master. The bounded input
patch is its independent exception. No operational protection bypass.

## Promote dev to master

Promotion is a deliberate source-acceptance operation, not a release. The only
valid promotion pull request has base `master` and head `dev` in this
repository. Keep at most one such pull request open. The repository maintainer
owns the promotion decision. There is no operational bypass; a different flow
requires an accepted policy change first.

1. Explicitly fetch current remote master/dev and inspect differences against
   completed local work. Do not replace local dev with origin/dev implicitly.
2. If current master adds history, reflect it with `--no-ff` in the dev-based
   candidate worktree, retaining the dev lane as the first parent. Resolve and
   verify, then integrate into dev using the local procedure. Push dev normally.
3. Run `tool/configs plan-promotion` on the selected local snapshots and
   review every included commit/scope. Check for another open master PR.
4. Create the same-repository dev to master PR. Required checks and resolved
   conversations must pass against the current base/head before an explicitly
   requested merge commit. If master moves or checks fail, stop and repair
   manually through dev; no automatic base repair or retry controller.
5. Confirm actual merged state and keep dev on its own lane. Domain publication
   is a separate decision. Reflect accepted master history with the procedure
   above at the next explicit work/promotion synchronization.

The one-time reset-based cutover is recorded separately from routine promotion.
It never becomes an everyday force option. Existing annotated tags stay fixed.

## Add or change governance

Before adding a rule, write a small governance decomposition:

1. Name the failure being prevented, owning scope, and decision owner.
2. State rationale and tool-independent invariants.
3. Define human prerequisites, ordered steps, recovery, and authorization
   boundaries without adding obligations absent from the policy.
4. Assign repeatable orchestration to a canonical skill and deterministic
   decisions to tools, hooks, CI, or remote settings.
5. Define evidence, positive and negative fixtures, current migration state,
   and the condition for removing superseded implementation.

Use `design-project-governance` from the sibling `skills` project to perform
this decomposition. The skill owns only the generic method; this repository
owns the result. A product-specific adapter must not own any part of either.

## Add or change an invariant

An invariant is a statement that must remain true of committed desired state
or repository tooling. `docs/policy/invariants/README.md` is the format; this is the
procedure.

1. Classify the invariant's scope. Its file goes under
   `docs/policy/invariants/<scope>/<slug>.md` and the change classifies as that scope.
2. Write the statement as one sentence naming no command, product, or model.
3. Point `rationale` at the section of `docs/policy/architecture.md` or `AGENTS.md`
   that justifies it. If none does, write that section first; a rule with no
   rationale is not ready to register.
4. Declare the enforcement. A `schema` or `tool` entry also declares a
   `fixture`; add the fixture in the same change and tag it with
   `INV <scope>/<slug>`. A `manual` entry names its evidence and is listed by
   id in its scope's `docs/policy/definition-of-done/<scope>.md`; because the checker requires that
   listing and refuses an unregistered tag in the same run, the entry and the
   evidence item land in one commit, which classifies as the entry's scope
   because both files sit under it.
   If nothing enforces it yet, open an
   issue and declare `pending #<n>` with an owner. Tag the fixture *unit* —
   the `Describe` or the banner section — or the pre-commit hook refuses the
   commit; `tool/configs invariants --untagged` names the unit.
5. Put the tag `INV <scope>/<slug>` in every declared locator: a header
   comment in a script, the test name or a comment above a fixture, the
   loader's refusal message.
6. Run `tool/configs invariants`. It runs again on every commit.

Removing an invariant removes its file and every tag that named it; the check
refuses an orphan tag. Weakening a statement is a governance change and is
reviewed as one.

## Register a provisional measure

A provisional measure is an experiment, a workaround, or a patch carried until
upstream ships a fix — anything the tree is meant to stop carrying.
`docs/provisional/README.md` is the format; this is the procedure. Register it in
the same change that adds it, not afterwards.

1. Classify the measure's scope. Its file goes under
   `docs/provisional/<scope>/<slug>.md` and the change classifies as that scope.
   Create the scope directory only if the measure needs it.
2. Write `statement` and `exit-when` as one sentence each: what the measure is,
   and the condition that ends it.
3. Set `watch` to the tracked path whose change is the signal, or to `manual`
   when only a person can tell. Leave the key out when neither applies.
4. Set `since` to the date the measure enters the tree and `review-by` to a
   date after it and at most 180 days later. Pick the date by which someone
   could tell whether `exit-when` came true, not the longest one allowed.
5. Open or name the issue where the measure and its exit are tracked, and
   point `decision` at the record that accepted it, `<path> § <heading>`. If
   no record accepted it, write one first through "Record a decision" below;
   a measure nothing decided is not ready to register. Name the `owner` who decides
   whether it is retired, extended or promoted.
6. Put the tag `PROV <scope>/<slug>` on every disposable line: the header
   comment above the block in a script or a Nix file, the comment above the
   PowerShell block, the running text of a document. A document explaining the
   registry writes the placeholder form and never a literal id.
7. Stage the entry and the tagged lines, then run
   `tool/configs provisional`. It reads the index, so an unstaged
   entry is invisible to it. It runs again on every commit and in CI.

## Retire, extend or promote a provisional measure

Every entry ends one of three ways, and `review-by` is the date the choice is
made rather than deferred. `tool/configs provisional --table` prints
what is registered and when each entry is next due.

Retire it when `exit-when` came true:

1. Delete the measure itself and every line tagged `PROV <scope>/<slug>`.
2. Delete `docs/provisional/<scope>/<slug>.md`, and the scope directory if that was
   its last entry.
3. Do both in one commit, classified as the entry's scope, with `repository`
   alongside for the supporting documents it deletes. The check refuses an
   entry no tag names and a tag no entry names, so half of this fails.

Extend it when `exit-when` has not come true and the measure is still the best
option:

1. Add a `reviewed: <YYYY-MM-DD> <why the horizon moved>` line to the prose,
   dated the day the review happened.
2. Move `review-by` to a date at most 180 days after that `reviewed:` date.
   The check measures the horizon from the later of `since` and the last
   `reviewed:` line, so an extension buys 180 days from the review, not from
   the original registration.
3. Say what changed since the last review. The `reviewed:` lines are the
   record of how long the measure has been about to end.

Promote it when the measure turned out to be the answer and is no longer
temporary:

1. Write a decision record through "Record a decision" below, saying what was
   learned and why the measure stays.
2. Delete the entry and every tag, as retirement does, and keep the code.
3. Whatever must now remain true of that code is an invariant, not a
   provisional entry; register it through "Add or change an invariant".

An overdue entry fails the check for a change in its own scope only, so a
change in another domain is never blocked by it. That is not a reprieve: the
next change to the owning scope stops until the entry is retired, extended or
promoted.

## Plan and verify work

Use a spec/report pair when planning, decisions or sustained verification
need a durable record. A small unambiguous change may use its commit body and
concise result instead. An issue and roadmap entry are optional.

1. Classify the outcome and read relevant current work. Create the owning
   `docs/work/<scope>/<slug>/spec.md` and pending `report.md` together in a
   dedicated worktree. State acceptance, evidence lanes and dependencies.
2. Run `tool/configs work --working-tree docs/work/<scope>/<slug>` before
   relying on the pair. Once staging is authorized, use `work --staged`.
3. Work and record evidence with the source change that produced it. Keep
   unavailable/failed evidence distinct. Change existing criteria only through
   dated amendments. Remote Actions evidence stays in Actions/PR records.
4. Mark implementation done when its criteria are verified. A later push or
   operational cutover can have its own pending record without undoing local
   completion. Issues are handled explicitly; use Refs links in source.
5. Retire obsolete active references with the adopted replacement. Do not
   rewrite historical failures as success or make all old report cleanup a
   prerequisite for current development. Archive paired records when their
   relevant preservation and reference review is complete.

The format remains `docs/work/README.md`; a work document is not policy.

## Record a decision

Write a record when a choice is expensive to reverse or a reviewer will ask
why it was made. Add a file under `docs/policy/decisions/<scope>/` with the
header and format `docs/policy/decisions/README.md` defines; nothing lists it
by hand, `tool/configs records --table decisions` does.
Reversing a decision creates a new record, sets the old one to
`status: superseded` with `superseded-by`, and moves every pointer to it in
the same commit — the checker cannot tell a superseded record from a live
one. Prose and code cite a record by path only; a quoted heading is checked
by nothing and rots. Cite it from a registry entry with `decision:` when an
invariant rests on it.

## Observe before adding or removing

A sentence added to a policy document without a check behind it rots, and a
deletion is as easy to get wrong as an addition. Both pass through
`docs/policy/candidates/` first. `docs/policy/candidates/README.md` is the format; this is
the procedure.

1. Record what was met and where, not the rule you would like to exist.
2. Add a dated line under `Occurrences` each time the same thing is met
   again, with the evidence.
3. Promote when the criterion is met: make the change in its owning scope
   through the flows above and delete the candidate in the same pull
   request. The commit message names the candidate it promotes.
4. Drop when the date passes or the event occurs without promotion: delete
   the file. History is the record either way.

Two things do not wait: a change that is fatal on a host and invisible to
every gate, and the correction of tracked text that is false today. A
candidate is an observation. Nothing cites it as authority, and an agent
does not follow one as a rule.

## Unix-like changes

1. Put feature-oriented declarations under the appropriate navigation group
   in `unixlike/modules/`; the file declares its class.
2. Put Unix-like source payloads in their owning Unix-like asset location.
3. Keep host composition in `unixlike/modules/flake/configurations.nix`.
4. Run narrow formatting, lint, evaluation, and native build checks.
5. Treat this flake's exported `fixture-*` and `example` outputs as synthetic
   test coverage. A Unix-like provider release certifies these checks and the
   constructor API, not any private host's final output.
6. Build and activate a real host only from its reviewed flake under the
   private `configs-hosts/hosts/<host>/` repository and only on explicit
   request. That consumer owns its independent evaluation, build and runtime
   evidence.

Do not add Windows desired state to a Nix module merely because the same tool
also runs on Windows.

Earlier in-repository host procedures remain in Git history. Provider-checkout
Justfile entry points now refuse real host selection; use the private
consumer's current procedure and reviewed host facts.

### Validate a private Unix-like host

Use the reviewed flake under `configs-hosts/hosts/<host>/` for a real host.
That repository owns the final output, identity, pinned provider revision,
installation procedure and deployment target. Run its `tool/check-hosts`
for final evaluation, then build on the target architecture and record native
runtime separately. Review the selected source, disk and host before any
installation, test activation, switch, reboot or rollback; those actions need
an explicit request. A `configs` provider check, synthetic install plan or
release tag does not supply private host evidence.

For reusable storage-class development, `unixlike/tool/install-plan` and
`install-vm-test` use synthetic provider fixtures. Their disposable VM proof
validates the provider layout and installer wiring, not a private disk.

### Capture Darwin host documents

Pin one reviewed full provider commit for preview and Save. On the target Mac,
use the delivered app with explicit host-owned documents and existing destination
parents. Paths must be absolute and canonical, outside provider source/store,
application directories and observed originals; the proposal must be a new file.

```sh
nix run 'github:shk95/configs/<full-commit>?dir=unixlike#darwin-capture' -- \
  preview --unit karabiner --document /host-repository/settings/karabiner.json \
  --unit symbolic-hotkeys --document /host-repository/settings/hotkeys.json \
  --output /private-preview-directory/proposal.json
nix run 'github:shk95/configs/<same-full-commit>?dir=unixlike#darwin-capture' -- \
  save --preview /private-preview-directory/proposal.json
```

Review the mode-600 private proposal's readers, destinations, complete settings
and source transitions before explicitly requesting Save. Save validates the
bound tool/schema, rereads inputs and targets, and recomputes the proposal; stale
or inconsistent state refuses. Each replacement is atomic, but multiple documents
are not one transaction. After refusal or partial Save, preserve completed
results and preview the actual current state again before another review/Save.
See `unixlike/tool/darwin-capture/README.md` for the delivered document contract.

Saving documents does not connect them to a consumer, publish provider changes,
apply application settings or activate a host. Consumer connection is separately
reviewed, and activation requires an explicit request. The retired repository
`capture karabiner` publication invocation refuses without observing the host or
changing Git; it never redirects to Save. The historical domain projection tool,
`just karabiner-check` and `just karabiner-test` remain independently available.

## Windows changes

Windows declarations, payloads, checks, and Apply logic live inside `windows/`
and are validated on native Windows.

1. Edit `windows/desired/manifest.json` for features, packages, and
   managed-file policy. Every package, managed file, the font, and the terminal
   delegation names exactly one declared feature; a new payload without one is
   rejected when the manifest loads.
2. Edit owned payloads below `windows/desired/files/`.
3. Update PowerShell under `windows/src/` when reconciliation semantics change.
4. Run native Windows tests and read-only host verification.
5. Create a Windows release tag only after the required native evidence exists.

Native read-only verification is:

```powershell
.\windows\win-env.ps1 setup-dev
.\windows\win-env.ps1 validate
.\windows\win-env.ps1 test
.\windows\win-env.ps1 check
```

`win-env.ps1` is the domain's one entry point: each verb runs its target script
and returns that script's exit status unchanged, so
the evidence a verb produces is the script's; a command the script refuses
ends the run at 1. CI and the hooks use the same public verbs.

A branch that has not been pushed yet can still reach a native Windows
clone of this repository through the filesystem: in that clone, fetch the
branch from the Unix-like session's main checkout — never from a linked
worktree, whose `gitdir` file names a path Git for Windows cannot resolve —
check it out, run the commands above under that host's own `pwsh`, and
switch the clone back to its previous branch afterwards. Once the branch is
pushed, `origin` is the transport and no path across the boundary is needed.

`setup-dev.ps1` installs the contributor toolchain declared in
`windows/toolchain.json`, which is also what CI installs from, so local Windows
and CI use the same Pester discovery, scope, and assertion semantics and the
same Lua compiler. Without it the checks still run: a source whose parser is
absent is reported as unverified and the command exits 69, so Windows work
remains pushable from a clone that has not installed anything.

Apply is a deployment, not verification, and requires an explicit request:

```powershell
.\windows\win-env.ps1 apply
```

A host may deploy part of the manifest with `-Minimal`, `-Feature`, `-Add`, or
`-All`; `README.md` describes the selection model. Selection is host state and
is recorded in `state.json`, so a change to the feature model is a Windows
desired-state change while a host's chosen set is not. Report which selection
produced any `-Check` or Apply evidence, because a check that passed under a
minimal selection says nothing about the features it excluded.

A change made in an application's UI can be previewed through
`windows/win-env.ps1 capture -SourceRoot <provider-checkout> -Environment <environment-file> -Unit <id>`.
First capture requires `-Document <relative-file>`; later capture uses its
existing connection. SourceRoot is a clean provider checkout, while Environment
is the host declaration path. Adding `-Save` explicitly writes complete host-owned
originals. Regenerate the selected environment before Check or Apply.
See `windows/examples/README.md` for the declaration format and examples.
Capture does not modify provider source or perform Git publication. Publish
provider source edits through the ordinary topic-branch and pull-request flow.

The native Windows suite exercises host-original generation and capture in
disposable fixtures. Foreign-host PowerShell results are fixture evidence;
hosted native Windows checks remain the management-runtime gate.

## Common changes

Do not create common material by default. First show that independently owned
Unix-like and Windows implementations have stable, genuinely platform-neutral
semantics.

When common ownership is justified:

Until the domain exists, no path under `common/` classifies; the change that
creates it restores classification, dispatch and the gate job first, or the
first commit is refused as having no owning scope.

1. Put it under `common/`, not under either platform domain.
2. Document its contract, supported consumers, and exclusions.
3. Give it consumer-independent checks.
4. Release it with a `common-v...` tag. It deploys nowhere.
5. Adopt it later through a separate Unix-like or Windows change.

Copying is the default adoption mechanism. Record provenance when useful, but
the destination owns the copy and does not owe future byte equality. A direct
import requires a pinned common version and an explicit decision explaining
why the coupling is acceptable.

## Verify

Run checks in proportion to the affected domain.

For Unix-like changes:

```sh
unixlike/tool/checks/format
unixlike/tool/checks/lint
unixlike/tool/checks/payloads
unixlike/tool/checks/test
```

The fixtures that prove the Unix-like checks refuse what they must —
`unixlike/tool/checks/payloads-test`, `flake-test`, `composition-test`,
`eval-coverage-test`, `prerequisite-test` and `import-order-test` — run in
the CI unix job. Run one by hand when its check or its fixtures change.
`import-order-test` composes every host twice and is merge-gate only by
design (`INV unixlike/import-order-independence`).

`unixlike/tool/checks/payloads` parses every source payload declared in
`unixlike/payloads.json` with the tool that consumes it. Evaluation does not
cover them: Nix copies a payload into the store without reading it.

`unixlike/tool/checks/test` evaluates every declared Unix-like configuration
and builds configurations native to the current host when appropriate. Foreign
evaluation is not native build or activation evidence.

For Windows changes, run the native Windows commands above. Unix-like Nix
evaluation is not part of Windows verification.

For common changes, run the checks owned by that common component. Do not make
Unix-like and Windows deployments prerequisites for a common release. Consumer
adoption validates integration later in the consuming domain.

For repository-governance changes, run the version-control fixture tests and
only the domain checks whose dispatch or enforcement behavior changed. Secret
scanning remains repository-wide. A governance change does not receive a
domain tag.

`tool/version-control/invariants` checks the invariant registry in both
directions and runs on every commit beside the hygiene scan, whatever the
scope of the change, because a renamed fixture in any scope can orphan the tag
an entry depends on.

```sh
tool/configs test
tool/configs invariants
tool/configs provisional
tool/configs domain-reads
tool/configs design-citations
tool/configs records
tool/configs audit
tool/configs audit-remote  # when gh is authenticated
tool/configs hook-evidence
```

Push runs bounded `audit --range <base> <tip>` for transmitted commits and
`audit --tag <name>` for a transmitted release tag. It does not rerun native
suites from the current checkout. Final candidate verification precedes local
integration; master CI verifies its actual PR result.

The full audit and `audit --history` remain explicit diagnostics for clone
and integration history. The history diagnostic uses fetched remote snapshots
when available; it is not proof of the current local candidate. Release
planning uses selected local master. Refresh snapshots explicitly for remote
operations. An unrelated local tag is not part of a branch push check.

## Bounded scheduled release

`.github/workflows/release.yml` is the shared Unix-like input patch workflow.
`CONFIGS_RELEASE_ENABLED=1` enables operation; `CONFIGS_RELEASE_SCHEDULE_ENABLED=1`
also enables its daily 05:00 Asia/Seoul schedule. Keep schedules off while rolling
out changed policy and tooling through ordinary dev-to-master promotion.
Configure release-control for accepted master writers and either the existing
CONFIGS_RELEASE_TOKEN or CONFIGS_RELEASE_APP_ID and CONFIGS_RELEASE_APP_PRIVATE_KEY.
The writer needs Contents/PR write and Actions/Checks read with protected merge
permission; no bypass. Candidate execution has no writer credentials. No general
release approval or Windows operation belongs to this path.

### Input patch operation

The workflow selects current master and refreshes nixpkgs, home-manager,
nix-darwin and nixos-wsl. Unchanged inputs produce no PR or tag. Changed inputs
produce one single-commit branch feature/unixlike-input-patch-<base SHA prefix>
with only the lock and the next patch release declaration. It opens a master PR,
requires exact-base/head/tree CI proof, merges through protection, confirms actual
merge identity and publishes an immutable Unix-like tag. CI completion events
resume scheduled operation; no 06/07 development-promotion stages or daily
promotion limit remain. Delayed/missing schedules have no guaranteed catch-up.

Master Unix-like configuration source must match its published release before
input patching; finish any unpublished development release first.

At most one master PR may be open. Finish an existing development promotion before
starting input patching. Development remains local topic-to-dev followed by protected master promotion.
Incorporate accepted master patch history in a candidate worktree, preserving
intended inputs/version, verify and fast-forward local dev. No patch adoption
PR against dev or report-only delivery is required. Development release
versions and tags remain the maintainer's responsibility.

### Manual operation and recovery

Choose Actions → Manual Unix-like input patch → Run workflow → master or run:

```sh
gh workflow run manual-release.yml --ref master
```

REST clients POST to /repos/shk95/configs/actions/workflows/manual-release.yml/dispatches
with ref=master and Actions write permission. The thin manual entry calls the same
shared workflow and waits in its writer job up to 60 minutes, polling every
30 seconds. Failure/cancellation of checks, stale candidates and expired waits
stop visibly while preserving the PR. Scheduled inspection defers to active manual
runs; cancel unwanted runs rather than leaving them pending. Both entry points
serialize writer jobs and preserve already completed remote work.

On failure inspect current PR/check state, repair the source or rerun transient
CI failure, then rerun the whole workflow or dispatch again. If master moved
before patch merge, close the stale patch PR and restart from current master;
the automation never rebases or merges a stale patch. If an orphan branch at the
same base conflicts with the intended lock, inspect and explicitly retire it
before retrying. Existing matching branches/PRs are reused after ambiguous writes.

A known missing patch tag is completed before a new refresh. Reruns verify existing
targets and annotations and create only missing tags; they never overwrite tags.
If the original patch merge is no longer current master, dispatch Unix-like input
patch with source=<original full merge SHA>. Only an input patch merge reachable
from master and backed by its exact PR CI proof can recover. General promotion
and Windows release sources are refused. Read-only diagnosis is tool/configs
release inspect; supported explicit publication recovery is tool/configs release
publish --source <SHA>. No GitHub Release or host activation/Apply is performed.

Current PRs/Actions/tags are the execution record, with no state database or result
copy commit. Report manual qualification separately from actual schedule events.
