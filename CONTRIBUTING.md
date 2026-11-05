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
Use setup for clone preparation and doctor before relying on an unverified
capability or after an environment change. These are not a startup sequence
to repeat for every task.

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

One scope per source commit and topic. Master may accumulate independently
scoped outcomes. A commit's
scope is the classifier's answer over the paths it touches; it determines
ownership and domain release scope. Check selection follows change effect:
domain documents may select no suite, while repository dispatch changes can
select several suites. Global scans still apply. The
subject's scope is a different thing: it names the domain the change
describes, so `docs(windows)` over `docs/policy/architecture.md`, which classifies
`repository`, is correct. If a common change and its platform adoption are
both needed, land them separately so neither release is synchronously coupled
to the other.

## Branch and commit flow

Master is the release and normal authoring branch. One logical commit normally
stays there; several commits for one coherent same-scope result use a
master-based topic and no-ff integration. A selected linked worktree also uses
a topic for a one-commit task. An issue or ordinary PR is optional.

For new work, ask current checkout versus linked worktree if the user has not
chosen. Keep that choice when continuing the same task; ask again only if it
must change. Parallel authors need isolation. An explicit tool argument is not
evidence of an unanswered preference.

```sh
tool/configs policy show
tool/configs workflow inspect
tool/configs workflow start --scope repository --commits one --workspace current
tool/configs workflow start --scope repository --commits many --topic example --workspace current
# If the user selected isolation instead:
tool/configs workflow start --scope repository --commits many --topic example --workspace linked
```

The start examples are alternatives. Policy show and inspect answer specific
questions; they are not mandatory preliminary commands. Use start for a clean
new task, and inspect existing Git state when resuming or continuing instead
of rerunning start. Start records the chosen scope, count, workspace and base in Git-local
operation data, visible through workflow inspect. The record is not approval
or evidence of process liveness. Start neither fetches nor changes master; topic bases use the selected local master snapshot. Inspect
and explicitly synchronize remote history when needed.
Topic names are `feature/<scope>-<topic>` or `fix/<scope>-<topic>`.

Use `workflow start --workspace linked` to create an isolated workspace;
there is one creation path. Primary and linked workspaces use identical hooks
and checks. Source commits remain single-scope.

If direct master work grows into several logical commits, use an authorized
in-place transition instead of rerunning clean-start initialization:

```sh
git switch -c feature/<scope>-<topic>
```

Run this on master at its current HEAD with no Git operation in progress.
The new topic keeps staged, unstaged and untracked work in the same checkout;
review `git status` before and after. If master already contains a completed
commit, keep it there and group the remaining work on the topic. Do not reset
master or rewrite accepted history to retroactively regroup it. The start
record, if present, remains the original estimate rather than new approval.

## Local verification and integration

Record the reviewed full master/base and candidate SHA. Commit only when
authorized. On the exact clean topic checkout, run:

```sh
# Verify only, without integration:
tool/configs workflow check --base <full-master-SHA> --head <full-candidate-SHA>
# Or, when integration is authorized, verify and merge in one operation:
tool/configs workflow merge --base <full-master-SHA> --head <full-candidate-SHA>
```

These are alternatives; running check before merge repeats verification.
Merge requires authorization covering the commit-producing integration. Existing
authorization for that operation remains valid within the agreed task. It runs the
checks itself, requires the candidate to contain the selected current master,
and creates a no-ff merge with those exact first and second parents. It uses
an existing master checkout or switches the chosen checkout back to master.
A dirty checkout, missing evidence, conflict or changed base stops integration;
reflect the new master in the topic, resolve there and verify again. No helper
resets, force-pushes or discards work. An interrupted Git merge is preserved
for inspection and normal explicit recovery.

For direct master work, run the same check command against the pre-change
master SHA and exact committed HEAD before publication. Pre-commit supplies
quick staged checks; full suites are selected by tracked dispatch. `workflow
check` refuses unavailable selected checks instead of calling them passed.
Foreign native evidence may require the native Windows clone or hosted CI;
record that boundary and do not claim a successful local integration check.

Source preparation may stop staged when requested. Commit, topic merge, push,
publication and activation are distinct operations: obtain authorization for
those requested, and reuse it within the agreed scope rather than asking again
at every step. Workspace selection supplies none of those authorizations.
Ordinary push
rejection preserves local work; inspect and reconcile, never retry with force.
`tool/configs commit` supports master and topics, commits only after confirmation,
and never publishes or prunes. Its `--dry-run` writes nothing; retired
`--publish`, `prune` and dev promotion invocations refuse.

Domain releases retain immutable annotated tags reachable from master.
`tool/configs plan-release` prints an evidence template and `tool/configs audit`
validates it. Report evaluation, build and native runtime separately, per host
for Windows and at provider/domain level for Unix-like/common. Review labels
and references for private machine/account identity before tag creation.
Tags and tag pushes require explicit requests. No GitHub Release or host
activation/Apply is implied.


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

After a refresh that moves zellij, a native build from the reviewed consumer
flake on the Mac and the
reproduction in `docs/policy/decisions/unixlike/zellij-patched-on-darwin-until-upstream.md`
are the build and runtime evidence; the checks prove only that the range
applies.

`.github/workflows/zellij-upstream-5500.yml` watches the branch tracked by
the nixpkgs input and opens one issue, then disables itself, when its Zellij
source contains the replacement fix merged in upstream #5714. The original
#5500 was closed in favour of that fix. The watch does not update the lock
or retire the overlay; its manual dry-run mode performs no remote writes. GitHub runs a `schedule` only from the
default branch, so the watcher does nothing until this file reaches `master`
through its next master adoption; before that its shell body is run by hand with
`DRY_RUN=1`.

## Local work and handoff

When continuing planned work, read its relevant record; use
`tool/configs records --table work` only when discovery is needed. Small clear
tasks need no work inventory or role handoff. Define acceptance using "Plan
and verify work" when a durable plan is useful. Record exact base/head at
verification, integration or handoff rather than requiring a separate planning
ritual before every edit. Use the agreed workspace and applicable checks.

Before interruption, leave the goal, exact base/head, evidence, unfinished
work and next step as plain handoff text. Optionally save it with
`tool/configs session save < handoff.md` and read notes from registered
workspaces with `tool/configs session inspect`. Save atomically replaces the
ignored `.work-session.md` only on explicit invocation, refuses empty or unsafe
writes, and preserves old-format notes until explicitly replaced. No lifecycle
state, agent identity or model-specific resume command is maintained.
Tracked policy and work documents remain the source of project context;
local notes supply no policy, approval, heartbeat or delivery proof.
Amend changed acceptance before relying on it; no separate planner role is
required. Uncertain liveness does not authorize cleanup.

Use session inspection and read-only Git state for requested local
handoffs. Remote status is optional and must be relevant to an explicit remote
operation or preservation review. Review unpushed/unique commits and tracked,
untracked and ignored data before any requested non-force removal. Do not read
notes/ content. Keep useful old worktrees; a clean diff is not preservation
evidence. No automatic pruning.

## Workspace preservation

`tool/configs worktree review <path-or-topic-name>` reports the exact head,
commits absent from master, tracked/untracked/ignored data and Git operations.
The exact topic ref retained in this clone preserves source when only the
worktree is removed; the tool checks it against registered metadata and HEAD
before removal and confirms the ref remains afterward. Unique commits are
reported without requiring an extra archive. Branch or clone deletion is a
separate preservation decision and is never part of worktree removal.
For additional external preservation, supply `--preserved-bundle <path>`.
The bundle must be outside the workspace and have no missing prerequisites.
The tool restores it into an independent disposable Git store and verifies
object integrity before accepting it as preservation evidence.
Ignored and untracked data still require separate preservation.
It never reads notes content or queries remote status. Primary checkout and
unsafe workspaces cannot be removed. Preserve reported data and source first;
then explicitly request removal with `tool/configs worktree done <path-or-name>
--expect-head <full-reviewed-SHA>`. Removal rechecks all blockers and retains
the branch. No force/remove-ignored override exists. This is not a liveness test.

## Candidate CI without a PR

Push a named topic only when requested, then explicitly dispatch CI on master
with the reviewed full `base` and `head` inputs. The head must already be
available in this repository; the base must still be current master and an
ancestor of the candidate. The CI workflow explicitly limits its token to
Contents read, grants PR read only to the topic metadata job, and disables
checkout credential persistence. Candidate code receives no write capability.

```sh
gh workflow run ci.yml --ref master -f base=<full-master-SHA> -f head=<full-candidate-SHA>
# Verify only:
tool/configs workflow check --base <full-master-SHA> --head <full-candidate-SHA> --ci-run <run-id>
# Or verify and integrate when authorized:
tool/configs workflow merge --base <full-master-SHA> --head <full-candidate-SHA> --ci-run <run-id>
```

The reader queries live same-repository successful CI, stable gate and exact
base/head/tree/event artifact. It rejects stale, failed, expired, missing,
wrong-workflow and wrong-source evidence. Local global scans still run; only
selected suites use the external proof. Verification prints the run ID and
source identities; put relevant evidence in the work report or handoff instead
of maintaining another Git-local verification cache. Workflow inspect shows
actual Git state and the start record. A changed master
requires new combined-result verification. No PR is required for this path.
Known Windows runtime-governance inputs additionally select `windows:runtime`,
a proof-only unit: local validate/test cannot certify CI runtime acquisition
and controller wiring, even on Windows. Those changes require exact hosted
CI proof; ordinary Windows domain validate/test remain locally available.

## GitHub integration

Master accepts direct commits and topic no-ff merges. CI runs on master push
and optional same-repository topic PRs. The stable `Required checks` result
validates selected jobs and global scans; it remains required evidence for
the bounded automated patch writer, not PR-only admission for ordinary work.
Master protection applies to administrators and disallows deletion. Ordinary
credentials cannot force push; the optional reviewed maintenance App is the
sole force exception. Master has no mandatory PR, status-check or conversation admission. Hosted PRs
use merge commits only; squash and rebase merging remain disabled.

Prepare policy and tools locally before explicitly migrating remote protection.
`tool/configs audit-remote` reads actual settings when remote inspection is
requested. It never repairs them. Changing source does not change GitHub
settings. Retired dev may be retained; review preservation before separately
authorized deletion. There is no dev-to-master promotion or automatic cutover.


## Explicitly approved history maintenance

Ordinary pre-push rejects non-fast-forward branch updates even when the Git
command includes a force flag. No local `--approved` switch bypasses it.
Read-only preparation is `tool/configs history-rewrite plan --old <full-SHA>
--new <full-SHA> --reason <reason>`. Planning is not execution permission.

For an authorized exception, dispatch `history-rewrite.yml` on master with
immutable old/new/reason inputs. Review the displayed plan and uploaded
`history-recovery` bundle before a human approves the `history-rewrite`
environment. The protected job mints the dedicated App token and the executor
checks the live approval, first run attempt, accepted tooling, declared App,
unchanged remote old SHA and bundle hash. It pushes only the specified master
ref with an explicit expected-old lease and confirms actual remote state.
Protection is never disabled or edited. Published domain tag ancestry stays.
A failed/ambiguous result preserves recovery and does not authorize another
operation. A new target or retry requires a new reviewed dispatch.

Adoption is separate and requires explicit authorization to change remote
settings. The supported personal/public repository path combines classic
protection with a branch ruleset:

1. Keep classic force disabled while preparing the dedicated App and reviewed
   environment. Declare its public IDs through policy.json's variable names;
   keep its private key only in that environment. Require individual human
   reviewers without administrator bypass and admit only the exact master
   branch, with no wildcard branches or tags.
2. Install the named active branch ruleset from policy.json for exactly
   `refs/heads/master`, with only `non_fast_forward`, no extra conditions and
   one bypass actor: the declared App's numeric ID as `Integration`, mode
   `always`. No other effective or inherited ruleset is admitted by this
   contract. Verify this restriction before enabling classic force; retain
   classic administrator enforcement and deletion denial.
3. Grant the App only Contents write, Actions read, Administration read and
   Variables read. The protected workflow requests that same limited token.
   GitHub's implicit Metadata read permission is also allowed.
   These grants support source writes and the live run/approval, protection,
   ruleset and variable reads. Do not increase write privileges merely to
   bypass a failed preflight.
4. Run `tool/configs history-rewrite preflight --app-slug <declared-app-slug>`
   and `tool/configs audit-remote` with the intended
   credentials. They require visible bypass actors and exact effective rules;
   missing metadata or permissions refuse. Qualify the approved live path
   separately before claiming operation. To retire the exception, disable
   classic force first, then remove the ruleset or App capability.

Ordinary tools must have no access to the App key. Neither planning nor
preflight performs a write or grants execution approval. The executor never
edits protection. Administrators able to change server settings remain a trust
boundary; the rule is not an OS or credential sandbox.

GitHub's [ruleset creation contract](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)
supports the App bypass on a public personal repository. The
[ruleset read API](https://docs.github.com/en/rest/repos/rules#get-a-repository-ruleset)
can hide bypass actors from callers without sufficient access; a hidden list
is unavailable evidence. Source preparation and simulated API fixtures do not
qualify the actual installed App or hosted execution.

## Add or change governance

When changing a rule, identify these concerns in the relevant decision,
invariant or work record; no additional decomposition document is required:

1. Name the failure being prevented, owning scope, and decision owner.
2. State rationale and tool-independent invariants.
3. Define human prerequisites, ordered steps, recovery, and authorization
   boundaries without adding obligations absent from the policy.
4. Assign reusable orchestration to its owning external plugin and
   deterministic decisions to tools, hooks, CI, or remote settings.
5. Define evidence, positive and negative fixtures, current migration state,
   and the condition for removing superseded implementation.

Project decisions and procedure stay here; optional orchestration reads them.

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
   user-selected workspace. State acceptance, evidence lanes and dependencies.
2. Use `tool/configs work --working-tree docs/work/<scope>/<slug>` for feedback
   before staging, or `work --staged` for the index. These are alternatives
   for the state being checked.
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

Use `docs/policy/candidates/` for an unaccepted observation that needs more
evidence before adoption or removal. Explicit maintainer-directed changes,
corrections and already accepted work proceed directly through their owning
scope; they do not wait for recurrence. The candidate format is
`docs/policy/candidates/README.md`.

1. Record what was met and where, not the rule you would like to exist.
2. Add a dated line under `Occurrences` each time the same thing is met
   again, with the evidence.
3. Promote when the criterion is met: make the change in its owning scope
   through the flows above and delete the candidate with the adopted change.
   Reference the observation where it explains the decision; a PR is optional.
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
provider source edits through ordinary master commits or checked topic integration.

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
unixlike/tool/checks/test
```

`unixlike/tool/checks/test` is the complete provider suite used by local
verification and CI. It checks the public constructor contract, native-module
extensions, an independently locked synthetic consumer, payloads, provider
scripts, evaluation coverage and import-order independence. Run an individual
fixture while working on its implementation; run the suite on the final result.

Every synthetic configuration is evaluated to its toplevel derivation. Host
closures and VM sessions are not built by default. Flake checks realize focused
provider-owned source transformations such as carried patches, plus native parser validation of generated
Niri and Noctalia configuration files. Host reproductions run in the consumer and are not provider release
qualification. Real host builds and runtime belong to the
consumer. The public configs-host-template is checked on its own source and pin;
provider verification does not fetch a moving template or private consumer.

Payload parsers use the provider's locked Nix input. Evaluation does not cover
payload syntax because Nix copies these files without reading them.

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
integration; master-push, optional PR and candidate-dispatch CI report their
actual tested source independently.

The full audit and `audit --history` remain explicit diagnostics for clone
and integration history. The history diagnostic uses fetched remote snapshots
when available; it is not proof of the current local candidate. Release
planning uses selected local master. Refresh snapshots explicitly for remote
operations. An unrelated local tag is not part of a branch push check.

## Bounded scheduled release

`.github/workflows/release.yml` is the shared Unix-like input patch workflow.
`CONFIGS_RELEASE_ENABLED=1` enables operation; `CONFIGS_RELEASE_SCHEDULE_ENABLED=1`
also enables its daily 01:17 Asia/Seoul schedule. Keep schedules off while rolling
out changed policy and tooling through ordinary master commits or topic integration.
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

The automated writer defers while any master PR is open and refuses ambiguous
multiple PR state. Ordinary development commits directly to master or merges
a checked topic. A moved master makes an existing patch stale; preserve it for
inspection and restart explicitly. There is no dev adoption or promotion step.
Development release versions and tags remain the maintainer's responsibility.

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
