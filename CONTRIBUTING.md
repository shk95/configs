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

Start a source change in its own linked worktree, with one topic branch for the
reviewable increment. Keep the primary checkout available for read-only
inspection and integration. `tool/configs worktree new <scope>-<topic> [feature|fix]`
fetches `origin/dev`, creates the branch and its sibling worktree, and prepares
its local dependencies. For a requested fixed base commit, create the linked
worktree at that exact commit and attach a topic branch there before editing;
verify that the commit is the intended `origin/dev` base before publishing.
The remote feature branch and PR preserve delivery. A local worktree may be
reclaimed after the handoff and data review below, even before merge; recreate
it from the remote branch when feedback requires changes.

`tool/version-control/require-linked-worktree` is a preflight for scripts that
write source. The pre-commit hook also refuses commits from the primary
checkout, including direct `git commit`; the routine commit helper refuses
there before it edits. Git cannot intercept an editor writing a file, so the
agent workflow and this start procedure keep editing in the linked worktree,
while the commit guard catches a misplaced change before it enters history.
Read-only checks, integration, promotion and release operations may use the
primary checkout. A native Windows clone may check an unpublished branch as
described below; it does not author that branch's source change.

```text
master <- dev <- feature/<domain>-<topic> or fix/<domain>-<topic>
```

Examples are `feature/unixlike-shell`, `fix/windows-zellij`, and
`feature/common-terminal-colors`. Governance examples are
`feature/repository-vcs-audit` and `fix/repository-ci-dispatch`.

A branch is one reviewable increment: one issue, or what one judgement
covers. Cut it from `origin/dev`, and merge it through one pull request when
it is complete and green
(`docs/policy/decisions/repository/work-planned-and-verified-in-documents.md`). A spec's increments are coherent same-scope outcomes, not individual steps or
evidence environments. Keep the report rows and status produced by the change
in that PR (INV repository/pull-request-spans-an-evidence-lane). The original
invariant identifier remains stable; its statement now covers multiple lanes.
"Plan and verify work" below explains the plan boundary.

A commit marks a judgement point. It carries the change one decision
produced, however many files that is, and is not split further merely because
it has parts (`docs/policy/decisions/repository/commit-marks-a-judgement-point.md`). Scope the
subject, for example `feat(unixlike):`, `fix(windows):`, `chore(common):` or
`refactor(repository):`. A document classifies as the scope directory that
holds it, or the scope a file under `docs/status/` or
`docs/policy/definition-of-done/` is named for, so a domain's decision,
invariant, evidence item and status land in that domain's commit
(`docs/policy/decisions/repository/documents-classified-by-scope.md`).
Anything that still touches two scopes is two commits.

Branches interleave where one blocks another, and no rule is needed to make
them: the pre-commit hook refuses a staged path with no owning scope, so a
move cannot be committed before the classifier accepts its new paths, and the
old paths cannot be deleted before the move has merged. Where that happens
each half merges when it is ready.

Use merge commits for completed work; do not squash or rebase published work.
Do not commit directly to `master`.

`dev` requires an up-to-date branch, so one whose base has moved catches up
before it can merge and GitHub's auto-merge will not do it. Merge `dev` into
the branch locally and push: the pre-push hook and the native lanes then run
against the tree that will actually land, which is where this repository's
native evidence comes from. Do not use `gh pr update-branch`, which has
GitHub author that merge outside both. `git merge-tree --write-tree HEAD
origin/dev` shows the conflicts read-only first.

`dev` means the affected domain's repository checks pass. `master` means the
source change has been accepted; it no longer means every platform at that
commit has been exercised. Native readiness is represented by domain tags and
the evidence in `docs/policy/definition-of-done/`.

Use independent release tags:

- `unixlike-vYYYY.MM.DD`, with `.N` for another release that day;
- `windows-vYYYY.MM.DD`, with `.N` for another release that day;
- `common-vYYYY.MM.DD`, with `.N` for another release that day.

Keep `unixlike/flake.lock` refreshes in dedicated `chore(unixlike-deps)`
commits. A domain tag certifies only the named domain even though the commit
may contain accepted history from the others.

For a routine desired-state edit whose message is a template — a Homebrew
formula or cask, a `unixlike/flake.lock` refresh —
`tool/configs commit` shows the edit, the classification, the selected
checks, and the message, then applies it and commits on your confirmation. It
refuses on `master` and never bypasses a hook.

Run it from a linked worktree on a branch dedicated to that edit. On a topic
branch it commits where it stands, and with `--publish` it arms auto-merge on
the pull request already open from that head, which on a branch carrying
other work would merge that work unfinished. Every edit it templates is
`unixlike`, so on a `repository` branch it would also produce a two-scope
commit. The primary `dev` checkout is refused before the helper edits.

Add `--publish` and that one confirmation carries the change the rest of the
way. If `dev` is checked out in a linked worktree, the helper branches to `feature/<scope>-<topic>` from
`origin/dev`; on any other branch it commits where it is. It then pushes,
opens a pull request against `dev`, arms auto-merge, and prints the
pull-request URL. It never waits on CI and never merges: `Required checks` and
an up-to-date base still decide that, and a push the pre-push hook or the
remote rejects leaves the commit local. `--dry-run --publish` prints the
branch, the pull-request title and body, and every command, and writes
nothing.

`--publish` requires `Allow auto-merge` to be on in the repository settings and
`gh` to be authenticated for github.com; it refuses before writing anything if
either is missing. It pushes the branch rather than the one commit, so it lists
everything on the branch that is not yet on `dev` before you confirm. Where a
pull request from the branch is already open against `dev` it arms that one and
leaves its title and body alone.

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

### Offline release preview

`tool/configs release-preview` is an optional read-only qualification tool,
separate from calendar `plan-release`, source promotion and release mutation.
It does not adopt production semantic versions or implement a release controller.
Run `tool/configs doctor repository`; the preview additionally needs Git 2.38 or
newer, a POSIX shell and awk. On Windows use native Git for Windows bash.

Choose trusted full master/candidate/rules commit identities, then prepare UTF-8
TSV baseline and evidence files with LF endings. Each starts with `format<TAB>1`;
empty, duplicate, unknown, malformed or control-bearing records refuse.
The pinned rules commit supplies `tool/version-control/release-preview.rules` as
data: seven-field `check` rows name ID/domain/lane/requiredness/dependencies/exact
tool identity; four-field `map` rows name exact-or-prefix/path/check IDs.
Unknown ownership, common-domain inputs and unmapped contract paths refuse.
The current table is bounded; add reviewed mappings rather than claiming blanket
production coverage.

Use one five-field baseline row per affected configuration domain:

```text
semantic<TAB>DOMAIN<TAB>VERSION<TAB>TAG<TAB>ANNOTATION_SHA
bootstrap<TAB>DOMAIN<TAB>SOURCE_SHA<TAB>RECORD_COMMIT<TAB>RECORD_PATH
```

A semantic row pins an annotated `DOMAIN-vMAJOR.MINOR.PATCH` object whose intrinsic
domain/version/source matches; moving a tag ref does not alter that replay input.
A bootstrap row requires `SOURCE_SHA` to equal candidate, plus a separately
reviewed source-bound record containing two-field `format`, `domain`, `source`,
`version` and `contracts` TSV rows (format 1, version 1.0.0 and matching identities).
The record can live in separate reviewed history to avoid a self-referential SHA.
No production bootstrap record is supplied by
the tool; choosing one requires the maintainer's decision. Legacy calendar tags
stay immutable and do not become semantic baselines by omission.

Nine-field evidence rows bind each check to the exact proposed comparison:

```text
evidence<TAB>CHECK_ID<TAB>CANDIDATE<TAB>MASTER<TAB>MERGE_TREE<TAB>RULES<TAB>TOOL_IDENTITY<TAB>STATE<TAB>REFERENCE
defect<TAB>CHECK_ID<TAB>REFERENCE
```

The tree is the isolated Git merge-tree result; tool identity must equal its
pinned rule. Required selected checks need `verified` evidence. A declared defect
refuses; advisory failures remain visible. The preview checks binding and grammar,
not the authenticity or real-world truth of supplied references. Gather genuine
evidence independently; never relabel a synthetic fixture as production proof.
With valid baseline and declaration inputs, an evidence file containing only its
format header yields missing-evidence refusal and JSON comparison/check identities;
use that diagnostic to bind subsequently gathered evidence, then rerun qualification.

```sh
tool/configs release-preview --master "$master_sha" --candidate "$candidate_sha" \
  --rules "$rules_sha" --baselines baselines.tsv --evidence evidence.tsv --json
```

Domain-changing source commits require strict `Release-Format`, `Release-Domain`,
`Release-Impact`, `Release-Contracts`, `Release-Compatibility`, `Release-Rationale`
and `Release-Migration` trailers. Unknown or incomplete declarations refuse;
breaking changes require major impact and a public migration blob. Exact inverse
unreleased `Release-Reverts` pairs cancel; a released target is a new declared
change. Repository-only changes need no domain impact declaration. These are this
optional preview's input requirements, not new repository-wide commit gates.

Candidate/no-op exits 0; invalid or ineligible input exits 1. Missing capabilities
report unverified and exit 69 locally, or fail under `REQUIRE_NATIVE=1`. Preserve
the JSON identities/digests and input files to replay a result. Resolve the named
refusal by correcting reviewed declarations/mappings/inputs or obtaining missing
evidence, then run again; do not weaken a check to turn refusal into success.
Run `tool/configs test` for the full repository fixtures. CI also runs the narrow
preview fixture natively on Git for Windows; local POSIX proof does not establish
that native result. Promotion, tag/release approval and host activation remain
separate operations with their existing authorization boundaries.

### Inert controller preview

The additive controller implements the disabled preview boundary in
`docs/policy/decisions/repository/release-controller-preview-boundary.md`.
Use only explicit synthetic approved-package assertions, operating records and
API transcripts. They do not authenticate production evidence or permissions.
The package protocol at `tool/version-control/release-control-package/protocol.md`
describes the bounded schemas and supplied-input limits.

1. Run `tool/configs doctor repository`. Set `CONFIGS_CONTROLLER_PYTHON` to an
   existing functional Python >=3.9 if the default Python command is unavailable;
   this command does not install or change a host runtime.
2. Preserve the reviewed exact public control/master commits, complete manifest
   and synthetic approval assertion. Supply pinned configuration bytes and
   append-only event history with its reconstructed index; supply live-stop
   fixture bytes separately. Never execute a candidate's script or artifact.
3. Run the inert preview:

   ```sh
   tool/configs release-control preview --fixture-inputs \
     --bundle-repository ./synthetic-public --approved ./approved.tsv \
     --operating ./synthetic-operating --transcript ./api-transcript.json \
     --request ./preview-request.tsv
   ```

4. Read its bounded outcome/stage/count. Disabled config emits nothing; unknown
   identity/schema/protocol, missing records, index disagreement or inconsistent
   observations refuse. Inspect the supplied records to repair the cause; do not
   fabricate approvals or rewrite successful release objects. Missing functional
   Python is unverified (69 locally, failed under REQUIRE_NATIVE=1).
5. Run `tool/configs test` for repository fixtures. CI declares Python and runs
   the narrow controller fixture on native Git for Windows in addition to Linux.
   Foreign proof does not establish Windows behavior.
6. For the actual preparation fixture on native Linux/Darwin, run
   `tool/configs test-refresh-candidate-nix` with an existing functional Python,
   Git and Nix CLI. This test extracts the reviewed trusted utility into disposable
   providers using only controlled local upstreams. It snapshots source bytes,
   modes, refs and commit counts; no-op/failure/confirmed timeout publishes no
   candidate. Only a changed lock creates a local automation dependency commit.
   A required base update uses a normal merge on that same fixture-owned branch.
   Missing Nix is unavailable, never installation permission or a native Windows
   prerequisite. The selected Nix-enabled CI lane must pass separately.

Current semantic protocol 2 has distinct refresh-branch/refresh-pr requests;
the promotion pr operation remains dev to master. A batch owns a fixed branch,
while immutable candidate revision/effect IDs bind exact source/base/parent/head,
lock and preparation identities. Historical observations replay old effects;
current schema/head/base/checks gate the next request. Unknown effects fence
revision change and promotion invalidation until exact reconciliation. Confirmed
absent old intents become history-only, and completed effects remain absorbing.
No PR body or asserted DTO supplies production authority. The loader executes
supported protocol 1 packages at their exact pinned source with the original
serializer/reducer; it does not upgrade old records. Unknown protocol or missing
closure refuses. The supplied single envelope is still not global storage or
automatic cross-batch configuration/package selection.

For global supplied history, add `--global-history --operating-head <full-sha>`
to the same explicit preview. Supply a complete local operating Git repository,
not a mutable directory projection. Fixed global-1 context/index schemas are in
`tool/version-control/release-control-package/protocol.md`. Retain reachable
config objects and completed-envelope transcript objects with exact approved
package identities. Missing bindings/objects, old offsets, malformed history,
shallow/replaced inputs or inconsistent whole-ledger indexes refuse without fetch.
Do not migrate or renumber old records to bypass refusal. The preview reads only
accepted objects and uses isolated scratch; no-outstanding is quiet, old completed
effects stay complete, and fresh stop cannot waive damaged history.

The master-only workflow is an inert interface with independent inspection and
constant writer-job serialization shape; it reads no private connection, secret
or Environment and has no schedule or enabled write mode. This source contract
does not authorize dispatching it. Actual operating repository, approval bootstrap,
credentials/protection/notification receipt and manual/scheduled rollout require
their separate authorized operating proof. Existing calendar releases and host
activation boundaries remain in force.

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

Use the project skills under .agents/skills/. An unspecified "work on X"
request first checks existing work through plan-work; only a small clear
single-criterion task goes straight to execute-work. Planning owns the roadmap
and work plans. Implementation owners update other docs affected by their work.
Do not turn every documentation edit into a planner assignment.

At pickup, inspect the plan and current repository. Fetch origin/dev, enter a
new linked worktree immediately and record both the execution base and the
reviewed plan revision. The plan's age alone does not require replanning;
changed acceptance, dependencies or ownership does. A worker can adjust details
inside the agreed result without silently weakening the criteria.

Run tool/configs session start <plan-path-or-> <lane> in that worktree. The
ignored .work-session.md holds lane, base, plan revision/content digest,
optional session ID and a free-text handoff. No PR state or check result cache
belongs there. Before interruption or role change, feed a meaningful handoff
into tool/configs session checkpoint suspended. Include goal, current commit
and uncommitted work, evidence, remaining work, reason and next action.
After approved replanning, run session replan <spec-path> while suspended;
it records the new revision and preserves the preceding checkpoint. A
recreated workspace uses session recover rather than checkpoint active; the
original base remains unknown unless separately verified. If a hard crash
leaves .work-session.lock, confirm ownership with the operator, preserve any
useful note/body, remove only that stale lock, then retry. PID or age alone
is insufficient. Use handed-off after Ready delivery; abandoned requires explicit disposition of
useful work. A resumed worker inspects local and remote changes before marking
active. An unfinished worker may return to planning after this checkpoint.
The planner chooses continuation, split, supersession or abandonment and names
its owner. A checkpoint is not a heartbeat or an atomic remote lane claim.

A worker resuming a Ready PR first coordinates withdrawal of admission,
confirms any auto-merge request is cancelled, and converts the PR back to
Draft before editing or pushing. Recreated workspaces follow the same rule.
Ready is restored only when the revised result and its checks are complete.

Workers commit, push, create a Draft PR and finish with Ready after current-head
required checks. They never use commit --publish or arm auto-merge. The legacy
commit --publish convenience remains a human-authorized integration operation;
its confirmation is not a worker handoff. Worker authorization to publish is
not permission to merge. Existing authorized scope does not need repeated
confirmation for each commit or push.

Use tool/configs session inspect to find local handoffs; inspect-work combines
that with fresh GitHub observations. Resume guidance is printed only for a
recorded session identity. An unknown session remains unknown.

Reclaim-workspaces is read-only by default. Before removal, inspect owner,
tracked/index/untracked/ignored paths and commits absent from the freshly
fetched remote. Do not read notes/ content. A clean diff or a merged PR alone
is insufficient. Recommend retain/resume, uncertain, or eligible. Obtain
explicit deletion authorization; then use a non-force worktree removal. The
worktree done helper removes a named worktree but does not establish safety.
A PR with all work pushed permits pre-merge reclamation after this review.

## GitHub integration

The integration session queries GitHub Draft/Ready PRs, exact heads, checks,
reviews, conversations, dependencies, mergeability and outstanding auto-merge
requests. It never reconstructs candidates from local worktree/branch lists.
GitHub native states are not duplicated as labels or local state files.
Semantic labels such as blocked and high-risk may inform admission.

One maintainer-managed integration session admits one candidate at a time.
Merge Queue is not used. Keep dev's PR requirement, Required checks with strict
base, administrator enforcement, resolved conversations, no force push and no
deletion. Do not grant agents bypass. Risk-specific human review is an explicit
admission requirement; add CODEOWNERS only with actual owner identities and
review rules. Required approval count remains zero for ordinary changes.

Re-query the candidate head/checks before admission. If strict protection needs
a newer base, ask its worker to merge origin/dev into its feature branch and
revalidate. Do not eagerly update every worker. Return conflicts and failed
validation to a worker, recreating its workspace from the remote if necessary.
With separate merge authorization, request GitHub merge-commit integration
with the expected head after checks pass. Do not arm unattended auto-merge
requests that could admit a later worker head. On recovery cancel any existing
auto-merge request and confirm cancellation before asking for head changes;
if it merged concurrently, inspect the actual result. Never
use an administrator bypass. Confirm merged state before admitting the next;
an accepted request or armed auto-merge is not a completed merge. Strict base
protection remains the safeguard if dev changes during admission.

Native stacks were demonstrated in a separate lab, not certified for this
repository. Until trunk-wide CI and all-layer admission are implemented and
verified, do not create or merge a native stack here. Wait for a dependency to
land and then branch from dev. Stacks can automatically rebase upper layers
and multiple PRs can share a merge commit; ordinary branch-update assumptions
must not be applied to them. No local dependency database is added.

The new role contract takes effect when this governance PR enters dev. Existing
workers checkpoint their actual state and adopt it at the next handoff; do not
rewrite their history. Effect-based CI changes and domain efficiency work are
separate follow-ups. Keep post-merge validation until equivalence with the
actual integrated result is proved; a prior PR success is insufficient.

## Promote dev to master

Promotion is a deliberate source-acceptance operation, not a release. The only
valid promotion pull request has base `master` and head `dev` in this
repository. Keep at most one such pull request open. The repository maintainer
owns the promotion decision. There is no operational bypass; a different flow
requires an accepted policy change first.

1. Fetch `dev` and `master`, then run `tool/configs plan-promotion`.
2. Review every commit and owning scope in `master..dev`. Do not add a fix to
   the promotion pull request; land the fix through its owning branch into
   `dev`, then refresh the promotion.
3. Open a pull request from `dev` to `master` titled
   `chore(repository): promote dev to master`. Record included pull requests,
   scopes, check evidence, and known unavailable native evidence.
4. Require `Required checks`, resolved conversations, and an explicit merge
   request. Merge with a merge commit only.
5. Run local and remote version-control audits after the merge. Do not merge
   the promotion commit back into `dev`.
6. Plan domain release tags or deployments separately when their own evidence
   is available.

If promotion is wrong, revert or fix it through `dev` and promote again. Never
rewrite `master` or move an existing release tag. `dev` requires an up-to-date
base before merge; `master` does not, because it accepts only `dev` and its
promotion merge commit intentionally does not flow back into `dev`.

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

Work with more than one acceptance criterion or more than one pull request
has a spec and a report. Any other change is a single pull request whose body
carries its evidence; an issue for it is optional. `docs/work/README.md` is
the format; this is the procedure.

1. Classify the outcome. The work item is `docs/work/<scope>/<slug>/`, and
   the spec has that one scope. Work whose outcome spans scopes is one spec
   per scope. An increment may classify differently from its spec, and its
   commit and pull request stay single-scope.
2. Write `spec.md`: the problem, the decisions with what was rejected, the
   increments — one for each coherent reviewable same-scope outcome, not
   one for each step or verification lane — and an `## Acceptance` table naming for each criterion the
   evidence lanes that must be verified. A criterion no check can decide
   names `review`. Set `review-by` to the date by which someone could tell
   whether the work is done. Argue a direction first in `study.md` when it
   needs a survey or a measurement, quoting each measurement with the date
   and the commit it was taken at.
3. Create `report.md` in the same commit, with one `pending` row per
   criterion. Before implementation, run
   `tool/configs work --working-tree docs/work/<scope>/<slug>` for
   read-only feedback on the new pair, including untracked files. This does
   not validate the proposed commit. When staging is authorized, stage both
   and run `tool/configs work --staged`; the hook runs that check too.
4. When implementation starts, open the execution issue. Its first line names
   the spec path; it holds the increments as a checklist and carries no
   acceptance criteria. Add `issue: #<n>` to the spec's header. A report
   issue that already exists — a bug, an upstream watch — links the spec and
   becomes the execution issue.
5. Work in coherent same-scope increments, one worker branch and PR each.
   Multiple verification lanes can support one result. Record the evidence
   and report changes in that same PR; external host/session evidence may
   justify a documentation-only result. The plan/report pair can be the first
   commit of the implementation PR, or a planning handoff reviewed beforehand.
   Preserve evidence distinctions and link issues with Refs references, never
   closing keywords (INV repository/no-closing-keyword). Publish a Draft early
   when useful and make it Ready only after completion and required checks.
6. To change a criterion after the report exists, add a paragraph to the spec
   that opens `Amended YYYY-MM-DD` and names the criterion. The checker
   refuses a criterion removed or rewritten without one.
7. End the report as `done`, `abandoned` or `superseded`. The push to `dev`
   that carries it closes the execution issue with a comment linking the
   report (`INV repository/issue-closes-from-report`); nothing else closes
   one automatically, and `tool/configs audit-remote` reports an
   issue left open beside a terminal report. A durable rule the work produced lands
   in a decision record or an invariant that names the document as its
   source, never by citing the work item from a document that carries
   authority; `tool/configs design-citations` refuses that citation.

`docs/work/roadmap.md` states priorities and dependencies, not schedule or PR
state. Maintain active, deferred and historical outcomes with reasons and
references; standalone work need not enter it. GitHub milestones are not used. A spec whose
`review-by` has passed while its report is pending is overdue:
`tool/configs work --overdue` lists it.

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
3. Keep public constructor composition in
   `unixlike/modules/flake/configurations.nix`; consumers own final host outputs.
4. Run narrow formatting, lint, evaluation, and native build checks.
5. Treat this flake's exported `fixture-*` and `example` outputs as synthetic
   test coverage. A Unix-like provider release certifies these checks and the
   constructor API, not any private host's final output.
6. Build and activate a real host only from its reviewed output in the
   private `configs-hosts` repository and only on explicit
   request. That consumer owns its independent evaluation, build and runtime
   evidence.

Do not add Windows desired state to a Nix module merely because the same tool
also runs on Windows.

Earlier in-repository host procedures remain in Git history. Provider-checkout
Justfile entry points now refuse real host selection; use the private
consumer's current procedure and reviewed host facts.

### Validate a private Unix-like host

Use the reviewed output from the actually delivered flake and lock in
`configs-hosts` for a real host. Its delivered source now uses one root
`flake.nix` and `flake.lock`, explicit `flake-modules/hosts/` declarations and
shared selected inputs. Its current pin and the public template's pin both
select the delivered provider repair; see `docs/status/repository.md` for exact
current pair refs, qualified evaluation/build evidence and remaining U1/API
release work. Earlier per-host and initial U1 records describe their original
source and locks. Shared source adoption does not imply simultaneous deployment.
That repository owns the final output, identity, pinned provider revision,
installation procedure and deployment target. Run its `tool/check-hosts`
for final evaluation, then build on the target architecture and record native
runtime separately. A shared pin update requires evaluating every affected
declared output; builds and deployment remain individually selected per host
(`docs/policy/decisions/repository/single-flake-host-consumers.md`).
Review the selected source, disk and host before any
installation, test activation, switch, reboot or rollback; those actions need
an explicit request. Neither a `configs` provider check nor its release tag
supplies private host evidence.

Installation planning and disposable VM proofs use consumer-owned tools and
the selected private host declaration. The provider no longer owns disk
layouts, target selection or installation inputs.

## Windows changes

Windows defaults, payloads, consumer generation, checks, capture and Apply
live inside `windows/` and are validated on native Windows. Provider
contributions and host-original edits have different destinations:

1. Edit `windows/desired/manifest.json` for provider features, packages and
   managed-file policy. Every package, managed file, font and terminal
   delegation names one declared feature; the loader refuses missing ownership.
2. Edit provider defaults below `windows/desired/files/`.
3. Update PowerShell under `windows/src/` when domain semantics change.
4. Run native Windows tests and read-only verification appropriate to the
   changed behavior. Source tests, client observations and deployment are
   separate evidence lanes.
5. Create a Windows release tag only after required native evidence exists
   and release is explicitly authorized.

Host selection and private settings belong in external environment/settings
documents, not provider payloads. See [the host example](windows/examples/README.md)
and [Windows usage](README.md#windows). Provider source, host originals,
generated configuration and runtime state remain separate.

### Contributor verification

```powershell
.\windows\win-env.ps1 setup-dev
.\windows\win-env.ps1 validate
.\windows\win-env.ps1 test
```

`win-env.ps1` forwards arguments and returns the target's status unchanged.
`setup-dev` installs the toolchain declared in `windows/toolchain.json`,
including the pinned Pester and Lua tools. A missing parser or Pester is
reported as unavailable (69), or fails when native tooling is required.
The suite discovers capture fixtures directly; runtime-specific cases may
be skipped on a foreign host. The retired provider-publisher E2E opt-in is
not part of the current capture workflow.

An unpublished branch can be inspected in a separate native Windows clone:
fetch it from the Unix-like session's primary checkout, not a linked worktree
whose gitdir path Git for Windows cannot resolve, check it out, run that
host's own commands and restore its prior branch afterwards. Once published,
use origin as the transport. This does not make that verification clone
the tracked source authoring workspace.

### Generate and check host intent

Use the pinned clean provider checkout's own PowerShell 7 tools. Inspect
returns its full source commit; set the external declaration's
`provider.commit` to that exact value and review its explicit feature list
and unit connections before generation:

```powershell
pwsh -NoProfile -File C:\provider\windows\win-env.ps1 inspect -SourceRoot C:\provider
pwsh -NoProfile -File C:\provider\windows\win-env.ps1 export-selection -SourceRoot C:\provider -State C:\host\legacy-state.json
pwsh -NoProfile -File C:\provider\windows\win-env.ps1 generate -SourceRoot C:\provider -Environment C:\host\environment.json -Output C:\generated\current
pwsh -NoProfile -File C:\generated\current\windows\win-env.ps1 check -Generation C:\generated\current
```

Export is a read-only migration proposal, not a declaration write. With no
State it proposes required core only. Resolve blockers such as retired WSL
selection before authoring the environment. `.wslconfig`, personal layouts
and layout hotkeys now belong to hosts; do not restore provider capture
instructions for them.

Keep generation output outside the provider and host originals. Connected
host documents supply a complete owned unit; they do not merge provider
defaults. Generation validates selected parsers and binds provider source,
host inputs and tools. Use the generated entry point with `-Generation`,
whose declaration owns selection; legacy selector flags cannot accompany it.
Report the actual source, selection and generation identity for Check
evidence, including drift and unavailable observations. Core-only evidence
does not certify excluded features.

Apply changes a host and requires an explicit request. Generation,
source adoption, Check and capture Save grant no deployment permission.
When authorized, use the generated entry point's `apply -Generation`
rather than mixing its declared selection with legacy runner flags.

### Capture host originals

Run capture using the exact pinned provider and external environment.
Select the relevant feature and enable the requested unit first; for example,
select powertoys before capturing advancedPaste:

```powershell
pwsh -NoProfile -File C:\provider\windows\win-env.ps1 capture -SourceRoot C:\provider -Environment C:\host\environment.json -Unit advancedPaste -Document settings/paste.json
```

The default is a preview. Review the complete host-source document and first
connection, then use `-Save` only when writing originals is intended.
`-Save -WhatIf` retains a preview. First capture needs a relative Document;
later capture uses its existing connection and cannot rename it. Multiple
Unit/Document values align by order. Capture does not select or enable units.

Every requested unit prepares before Save, with identities checked before
writes. The first document precedes its connection. Read per-unit outcomes:
a failed connection leaves an inert document, and an explicit matching retry
can attach it; conflicting content refuses overwrite. Some units may already
be completed when a later save fails. There is no multi-file atomicity or
automatic rollback. Keep originals and review failures before retrying.

Capture writes host originals only. It does not change app targets, provider
defaults, generated output, runtime Apply state or Git. The removed
Feature/Id/Branch/Publish capture parameters do not provide a publication
path. Host commits and publication follow the host repository's workflow;
provider contributions require a separately reviewed provider change.
Do not copy private originals or host observations into public source.

Regenerate after originals, selection, source or tools change. Old generation
identity is deliberately stale; a failed generation preserves previous output
but does not validate it against changed inputs. Check the newly generated
configuration before any separately requested Apply. Documentation checks
provide no new Windows native execution, Save or Apply evidence.

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
and builds its selected native synthetic outputs. The default selection covers
one representative per constructor supported by the runner. Set
`CHECKS_BUILD_TARGETS` to space-separated `flavour.name` attributes for a
specific affected contract, or `CHECKS_BUILD_ALL=1` for all native fixtures.
A missing, foreign or failed selected build refuses the check. Foreign
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

`tool/version-control/audit --history` runs on every push and in the
repository-wide CI scan job, and judges committed history alone. It reads
`dev` and `master` as `origin/dev` and `origin/master` when those refs
exist, and the local branches only when they do not, so a local `dev` or
`master` that lags or leads its remote neither blocks a push nor lets one
through unchecked. A clone that has not fetched is judged against the remote
as it last saw it. Every local tag is still judged, including one the push
does not carry: a stray local `*-v*` tag still fails the push until it is
deleted. The full form, which also judges this clone — local branch names,
the hooks setting — and reads the local branches first, is a read-only look
by hand, because a clone's scratch branch is not a property of the change
being pushed. `tool/configs plan-release` checks reachability from
the local `master`, because it plans a tag this clone creates.

The history form also judges, through `.githooks/commit-msg`, the non-merge
subjects of the commits being published: the pre-push hook names the tips it
pushes, and CI names `HEAD`, which for a pull request is the merge GitHub
would make. A commit made without the hooks or with `--no-verify` therefore
fails the push that carries it, and the pull request, before it merges. A
commit on a branch the push does not carry is not judged.

### Desired-state hygiene

`tool/version-control/hygiene` scans the tracked tree for undeclared user and
host names, absolute home paths, tracked runtime state, and machine-unique
identifiers. It runs on every commit from `.githooks/pre-commit` beside the
secret scan and outside domain dispatch, and again in CI, because the invariant
is repository-wide rather than scoped to the domain being changed.

```sh
tool/configs hygiene
```

When it reports something, in order of preference:

1. Remove the value. A leaked value is desired state that names one machine.
2. If it is a synthetic provider fixture name or a value that genuinely
   belongs to another declaration in this repository, declare it in
   `tool/version-control/hygiene.names` with the owning change. Real Unix-like
   host names and accounts belong in the private consumer repository.
3. If it is a runtime artefact, delete it and add an ignore rule. The ignore
   rule alone changes nothing once the file is tracked; it has to leave the
   index too.
4. Only when the reported text is genuinely not what it looks like, add one
   `<path>`, tab, `<literal string>` row to `tool/version-control/hygiene.allow`
   with a comment giving the reason. Both halves of "one string at one path"
   are enforced, not conventions: an entry whose literal no longer occurs at
   its path fails the check and is removed together with the text it forgave,
   and an entry that forgives more than one line fails as the whole-file
   exclusion it is. Write a literal specific enough to name the occurrence.

Adding an allow entry is a governance change and is reviewed as one. There is
no operational bypass: `git commit --no-verify` skips every hook and leaves CI
to reject the same content.

A bare account name written into prose is not detectable and is not covered.
Reading prose in the diff for one is a manual obligation recorded in
`docs/policy/definition-of-done/`.

### Cross-domain reads

`tool/version-control/domain-reads` scans each domain's code in the index —
the flake, the modules and the Unix-like checks on one side, the Windows
scripts on the other — for a path that names the other domain's tree, with
comments stripped and payload trees left out. It runs on every commit beside
the hygiene scan and in CI, because a read across the boundary is a property
of two trees rather than of the domain being changed.

```sh
tool/configs domain-reads
```

When it reports something, copy what the other domain owns into the domain
that reads it; the destination then owns the copy (`docs/policy/architecture.md`,
"Default rule: keep implementations separate"). There is no allow list: a
read across the boundary has no legitimate form.

### Design citations

`tool/version-control/design-citations` scans the index for a citation of a
work item from authority-bearing files. It runs on every commit and in CI.

```sh
tool/configs design-citations
```

When it reports something, decide which of the two the sentence is doing. If
it says where work documents live, name the directory rather than a file:
`docs/work/` passes and `docs/work/<file>` does not. If it rests on the
document's argument, put the accepted rule in a decision record or invariant,
or register a temporary measure, and cite that instead. There is no allow list.

### Document indexes

`tool/version-control/records` refuses an area README — decisions, candidates
or work — that names one of the area's documents: a record or candidate by
its file name, a work item by its `<scope>/<slug>`. The list is printed from
the headers instead, so a new record never edits a repository file
(`INV repository/document-index-generated`). It runs on every commit and in
CI.

```sh
tool/configs records
tool/configs records --table decisions
```

Branch protection on `dev` and `master` requires the stable `Required checks`
job. That job fails unless classification and secret scanning pass and every
selected domain job succeeds. Conditional domain job names are deliberately
not branch-protection contexts because unselected domains are skipped.
