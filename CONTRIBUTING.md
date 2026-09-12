# Contributing

This is the workflow for people and tools. `AGENTS.md` contains stable
judgement and safety rules, `docs/architecture.md` defines domain ownership,
and `README.md` contains usage.

## Prepare a clone

```sh
tool/setup
tool/setup --fix
tool/doctor.sh
```

`tool/setup` changes only the clone-local hooks setting and only with `--fix`.
`tool/doctor.sh` is read-only. `tool/doctor.sh` also prints a one-line
summary of the outcomes the hooks have recorded on this clone;
`tool/version-control/hook-evidence` prints the full count. Pass `unixlike`,
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
describes, so `docs(windows)` over `docs/status.md`, which classifies
`repository`, is correct. If a common change and its platform adoption are
both needed, land them separately so neither release is synchronously coupled
to the other.

## Branch and commit flow

```text
master <- dev <- feature/<domain>-<topic> or fix/<domain>-<topic>
```

Examples are `feature/unixlike-shell`, `fix/windows-zellij`, and
`feature/common-terminal-colors`. Governance examples are
`feature/repository-vcs-audit` and `fix/repository-ci-dispatch`.

A branch belongs to a milestone. Cut it from `origin/dev` when the
milestone's work starts, take its topic from the milestone's own
`<scope>: <outcome>` title, carry every commit that work produces on it, and
merge it through one pull request when the work is complete
(`docs/decisions/branch-lives-as-long-as-its-milestone.md`). A change no
milestone plans is a branch of its own and merges when it is done.

A commit marks a judgement point. It carries the change one decision
produced, however many files that is, and is not split further merely because
it has parts (`docs/decisions/commit-marks-a-judgement-point.md`). Scope the
subject, for example `feat(unixlike):`, `fix(windows):`, `chore(common):` or
`refactor(repository):`. The one accepted two-scope commit is an invariant
entry together with the evidence item that enforces it, which "Add or change
an invariant" describes; anything else is two commits.

Branches interleave where one blocks another, and no rule is needed to make
them: the pre-commit hook refuses a staged path with no owning scope, so a
move cannot be committed before the classifier accepts its new paths, and the
old paths cannot be deleted before the move has merged. Where that happens
each half merges when it is ready rather than when its milestone completes.

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
the evidence in `docs/definition-of-done.md`.

Use independent release tags:

- `unixlike-vYYYY.MM.DD`, with `.N` for another release that day;
- `windows-vYYYY.MM.DD`, with `.N` for another release that day;
- `common-vYYYY.MM.DD`, with `.N` for another release that day.

Keep `flake.lock` refreshes in dedicated `chore(unixlike-deps)` commits. A
domain tag certifies only the named domain even though the commit may contain
accepted history from the others.

For a routine desired-state edit whose message is a template — a Homebrew
formula or cask, a `flake.lock` refresh — `tool/version-control/commit` shows
the edit, the classification, the selected checks, and the message, then
applies it and commits on your confirmation. It refuses on `master` and never
bypasses a hook.

Run it from `dev`. On any other branch it commits where it stands, and with
`--publish` it arms auto-merge on the pull request already open from that
head, which on a milestone branch would merge that milestone unfinished.
Every edit it templates is `unixlike`, so on a `repository` milestone branch
it would also produce a two-scope commit.

Add `--publish` and that one confirmation carries the change the rest of the
way. On `dev` the helper branches to `feature/<scope>-<topic>` from
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
`unavailable` or `not applicable` values. Create and push a tag only when the
user explicitly requests those mutations. Create no GitHub Release: the
annotation is the whole record. Activation and Windows Apply happen after
release and are not implied by a tag.

For agent-assisted work, invoke `run-version-control-workflow`. Its canonical
Agent Skills implementation is under `.agents/skills/`; model-specific
discovery files are adapters only. Audit and release planning are read-only by
default. This document remains the human fallback and the contract the skill
executes.

### zellij overlay

This subsection is disposable and carries the tag
`PROV unixlike/zellij-combining-marks`, so it is deleted with the measure it
describes.

`modules/zellij.nix` carries upstream zellij-org/zellij#5500 for Darwin until
nixpkgs ships a zellij whose source already has the fix;
`provisional/unixlike/zellij-combining-marks.md` registers the measure and
names the condition that ends it. The overlay is pinned to one zellij version
and refuses to evaluate against any other, so a `flake.lock` refresh that moves
zellij takes two commits, in this order:

1. `just zellij-patch-check v<ver>` for the version the refresh will bring in.
   On a conflict, rebase the upstream commit in a fork and repoint the
   overlay's `url` and `hash` before going on.
2. Commit `chore(unixlike-deps): refresh flake.lock` with `flake.lock` alone —
   `tool/version-control/commit flake refresh`, with no `--publish`. Helper
   flags precede its command, so `--publish` would be
   `tool/version-control/commit --publish flake refresh`; it is not used here
   because it pushes as soon as this commit is made.
3. Commit `fix(unixlike): re-pin the zellij overlay to <ver>` with `appliesTo`,
   the `fetchpatch` hash if the range was rebased, and the new `cargoDeps`
   hash. The pin is the pull request's commit range `base...head` in the
   overlay's compare URL; a re-pin to a branch that gained commits moves the
   head, and a rebase moves both.
4. `just darwin-build` on the Mac, then the reproduction in
   `docs/decisions/zellij-patched-on-darwin-until-upstream.md`.
5. Push only after step 3.

Between steps 2 and 3 the Darwin configuration refuses to evaluate, by design:
that refusal is the overlay's report that its patch no longer matches the
pinned zellij. Nothing selects evaluation for a lock-only change, so the
refusal blocks no commit, but it does block a push, which is why step 5 waits
for the re-pin.

`.github/workflows/zellij-upstream-5500.yml` watches the pull request and
reports a bump or a merge as an issue. GitHub runs a `schedule` only from the
default branch, so the watcher does nothing until this file reaches `master`
through the next promotion; before that its shell body is run by hand with
`DRY_RUN=1`.

## Promote dev to master

Promotion is a deliberate source-acceptance operation, not a release. The only
valid promotion pull request has base `master` and head `dev` in this
repository. Keep at most one such pull request open. The repository maintainer
owns the promotion decision. There is no operational bypass; a different flow
requires an accepted policy change first.

1. Fetch `dev` and `master`, then run `tool/version-control/plan-promotion`.
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
or repository tooling. `invariants/README.md` is the format; this is the
procedure.

1. Classify the invariant's scope. Its file goes under
   `invariants/<scope>/<slug>.md` and the change classifies as that scope.
2. Write the statement as one sentence naming no command, product, or model.
3. Point `rationale` at the section of `docs/architecture.md` or `AGENTS.md`
   that justifies it. If none does, write that section first; a rule with no
   rationale is not ready to register.
4. Declare the enforcement. A `schema` or `tool` entry also declares a
   `fixture`; add the fixture in the same change and tag it with
   `INV <scope>/<slug>`. A `manual` entry names its evidence and is listed by
   id in `docs/definition-of-done.md`; because the checker requires that
   listing and refuses an unregistered tag in the same run, the entry and the
   evidence item land in one commit that classifies as the entry's scope
   and `repository` — the two-scope commit "Branch and commit flow" allows.
   If nothing enforces it yet, open an
   issue and declare `pending #<n>` with an owner. Tag the fixture *unit* —
   the `Describe` or the banner section — or the pre-commit hook refuses the
   commit; `tool/version-control/invariants --untagged` names the unit.
5. Put the tag `INV <scope>/<slug>` in every declared locator: a header
   comment in a script, the test name or a comment above a fixture, the
   loader's refusal message.
6. Run `tool/version-control/invariants`. It runs again on every commit.

Removing an invariant removes its file and every tag that named it; the check
refuses an orphan tag. Weakening a statement is a governance change and is
reviewed as one.

## Register a provisional measure

A provisional measure is an experiment, a workaround, or a patch carried until
upstream ships a fix — anything the tree is meant to stop carrying.
`provisional/README.md` is the format; this is the procedure. Register it in
the same change that adds it, not afterwards.

1. Classify the measure's scope. Its file goes under
   `provisional/<scope>/<slug>.md` and the change classifies as that scope.
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
   `tool/version-control/provisional`. It reads the index, so an unstaged
   entry is invisible to it. It runs again on every commit and in CI.

## Retire, extend or promote a provisional measure

Every entry ends one of three ways, and `review-by` is the date the choice is
made rather than deferred. `tool/version-control/provisional --table` prints
what is registered and when each entry is next due.

Retire it when `exit-when` came true:

1. Delete the measure itself and every line tagged `PROV <scope>/<slug>`.
2. Delete `provisional/<scope>/<slug>.md`, and the scope directory if that was
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

## Write a design document

Write one when a direction needs arguing before any of it can be adopted: a
survey, a spike and what it measured, three layouts weighed against each
other, a plan and what each of its steps predicts. Add a file under
`docs/design/` with the header and format the `README.md` there defines, add
it to that file's index, and open it `status: open`.

It has no authority and acquires none by being merged. Quote what you
measured with the date and the commit you measured it at, and leave current
state to `docs/status.md` and the schedule to a milestone and its issues.
When a `plan` names what it expects, write the expectations before the work
runs; an expectation written afterwards is not one and is left out of the
ledger.

Adopt from it through an inlet, never by citing it from a document that
carries authority: a decision record, a promoted candidate, a registered
provisional measure, or an issue. Add an `outcome` line for each thing the
document produces, and set `status: closed` when the last one has landed.
A result that contradicts the argument is written into the ledger and then
corrected in the document that argued it.
`tool/version-control/design-citations` refuses a citation from an internal
location and runs on every commit, so a rule can never come to rest on an
argument nobody accepted.

## Record a decision

Write a record when a choice is expensive to reverse or a reviewer will ask
why it was made. Add a file under `docs/decisions/` with the header and
format `docs/decisions/README.md` defines, and add it to that file's index.
Reversing a decision creates a new record, sets the old one to
`status: superseded` with `superseded-by`, and moves every pointer to it in
the same commit — the checker cannot tell a superseded record from a live
one. Prose and code cite a record by path only; a quoted heading is checked
by nothing and rots. Cite it from a registry entry with `decision:` when an
invariant rests on it.

## Observe before adding or removing

A sentence added to a policy document without a check behind it rots, and a
deletion is as easy to get wrong as an addition. Both pass through
`docs/candidates/` first. `docs/candidates/README.md` is the format; this is
the procedure.

1. Record the observation as `docs/candidates/<slug>.md` with `kind:
   addition` or `kind: deletion`, the target it would change, the criterion
   that promotes it and the date or event that drops it. Write what was met
   and where, not the rule you would like to exist.
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

## Plan work with GitHub milestones

GitHub milestones group planned work after its owning scope and outcome are
known. They coordinate issues; they do not replace repository policy, domain
release evidence, or deployment authorization.

1. Search open and closed milestones for the same outcome before creating one.
2. Choose exactly one scope and title the milestone `<scope>: <outcome>`.
3. Write `Outcome`, `Included`, `Excluded`, `Completion criteria`, and
   `Authority` sections in the description. Link the repository documents that
   own durable decisions and current support boundaries.
4. Set a due date only when the maintainer has chosen a real schedule. Leave it
   unset for an unordered roadmap.
5. Create independently closable issues with the same scope prefix and assign
   only those issues to the milestone. Link cross-scope prerequisites without
   assigning them.
6. Keep one final evidence issue open until the milestone's evaluation, build,
   native runtime, and activation or Apply evidence is reported as applicable.
7. Close the milestone only after every assigned issue is closed and the
   maintainer confirms the completion criteria.

If the scope or outcome was wrong, edit the milestone and its issue membership;
do not reinterpret a closed milestone as a release or move work between domains
silently. The milestone description and final evidence issue are the review
record for this intentionally manual policy.

## Unix-like changes

1. Put feature-oriented declarations under `modules/`.
2. Put Unix-like source payloads in their owning Unix-like asset location.
3. Keep host composition in `modules/flake/configurations.nix`.
4. Run narrow formatting, lint, evaluation, and native build checks.
5. Create a Unix-like release tag only after the required matching-host
   evidence exists, including a build of every configuration with
   `CHECKS_BUILD_ALL=1 tool/checks/test` on a matching host.
6. Activate only when explicitly requested, from the intended Unix-like
   release.

Do not add Windows desired state to a Nix module merely because the same tool
also runs on Windows.

### Import the NixOS-WSL distribution

`just nixos-build`, `just nixos-tarball` (needs sudo) and `just nixos-stage`
produce the rootfs archive and copy it to a Windows drive;
`docs/troubleshooting.md` records why `wsl --import` will not read it from
`\\wsl.localhost\...`. Then, from PowerShell or CMD:

1. `wsl --import NixOS C:\WSL\NixOS C:\WSL\nixos.wsl` registers the
   distribution. Its first boot activates the toplevel and the composed
   home.
2. `wsl -d NixOS -u root -- passwd <account>` sets the account's password.
   The account is created locked and sudo asks for a password
   (`modules/wsl.nix`), so until this has run nothing inside can become
   root; WSL's `-u root` needs no Linux authentication, and the password
   set this way survives every later activation.
3. If the host is to be reached over ssh, copy an `authorized_keys` into
   `\\wsl.localhost\NixOS\home\<account>\.ssh\`. Keys are host-owned
   (`modules/ssh.nix`); the port is the one `modules/wsl-sshd.nix`
   declares, and any mapping beyond the Windows host is Windows state.
4. `wsl -d NixOS`. The account logs into zsh, flakes are on, and
   `tool/doctor.sh unixlike` reports the host ready.

Rollback is `wsl --unregister NixOS`; Ubuntu is untouched throughout.

### Capture Karabiner drift

On the Mac, `just karabiner-check` reports whether the host still holds the
members `assets/karabiner/` declares, and `just karabiner-capture` reads drift
that belongs in desired state back into the payloads and commits it.

`apply` replaces the declared top-level keys wholesale. Before the first
activation on a Mac whose Karabiner state has not been captured, run `just
karabiner-check` and, on drift, `just karabiner-capture`, and switch from the
tree that carries the capture — `just darwin-switch` builds from `path:.`, so
it delivers the payloads in that working directory, not the ones on a branch
you have not checked out.

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

`win-env.ps1` is the domain's one entry point: each verb runs one script under
`windows/tools/` (`setup-dev.ps1`, `check-desired-state.ps1`, `test.ps1`,
`bootstrap.ps1 -Check`) and returns that script's exit status unchanged, so
the evidence a verb produces is the script's; a command the script refuses
ends the run at 1. CI and the hooks run those scripts directly.

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

A change made in an application's own UI moves back into desired state with
`.\windows\win-env.ps1 capture` (`windows/tools/capture.ps1`), which reads the
managed targets, writes only
this repository's payloads — a JSON payload pretty-printed to this
repository's two-space style — and ends at one confirmation before committing.
Preview it with `-WhatIf` first. It restates the guards of
`tool/version-control/commit` rather than calling it, including its branch
rule: it refuses on `master`, on a dirty index, and on a payload that already
has uncommitted changes, and never bypasses a hook. On `dev` it branches to
`feature/windows-capture-<feature>` from a freshly fetched `origin/dev` (or a
name given with `-Branch`) before it commits, reported in the plan before the
`[y/N]`, so a capture run on `dev` never leaves a commit on that protected
branch; on any other branch the commit stays there. Read its refusals rather
than working around them, and read the hook output under its commit: Git for
Windows runs the POSIX hooks natively, but a clone that has not set
`core.hooksPath` runs none of them.

Add `-Publish` and that same confirmation pushes the branch, opens one pull
request against `dev`, arms auto-merge and prints the pull-request URL. It is
the Windows copy of `--publish` above and behaves the same way: it never waits
on CI and never merges, a rejected push leaves every commit local on the named
branch, and nothing retries with a bypass. It requires `gh` authenticated for
github.com and `Allow auto-merge` on in the repository settings, and refuses
before writing anything if either is missing, if a pull request from the same
branch is open against another base, or if the remote already has the branch
the run would create; a pull request already open against `dev` from that
branch is armed unchanged. It pushes a branch rather than a commit, so it
lists whatever the branch already carries beyond `dev` before the `[y/N]`.
`-WhatIf -Publish` prints the branch, the title, the body and every command
and writes nothing. Promotion to `master` and release remain the flows above.

`windows/tools/test.ps1` leaves out the Pester cases that run `capture.ps1`
end to end in a child PowerShell, and says which ones it skipped. Set
`WIN_ENV_E2E=1` to run them; the `windows-latest` CI job does, so the merge
gate covers them and a local push stays quick.

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
tool/checks/format
tool/checks/lint
tool/checks/payloads
tool/checks/test
```

The fixtures that prove the Unix-like checks refuse what they must —
`tool/checks/payloads-test`, `flake-test`, `composition-test`,
`eval-coverage-test`, `prerequisite-test` and `import-order-test` — run in
the CI unix job. Run one by hand when its check or its fixtures change.
`import-order-test` composes every host twice and is merge-gate only by
design (`INV unixlike/import-order-independence`).

`tool/checks/payloads` parses every source payload declared in
`assets/payloads.json` with the tool that consumes it. Evaluation does not
cover them: Nix copies a payload into the store without reading it.

`tool/checks/test` evaluates every declared Unix-like configuration and builds
configurations native to the current host when appropriate. Foreign evaluation
is not native build or activation evidence.

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
tool/version-control/test
tool/version-control/invariants
tool/version-control/provisional
tool/version-control/domain-reads
tool/version-control/design-citations
tool/version-control/audit
tool/version-control/audit-remote  # when gh is authenticated
tool/version-control/hook-evidence
```

`tool/version-control/audit --history` runs on every push and in the
repository-wide CI scan job, and judges committed history alone. The full
form, which also judges this clone — local branch names, tags, the hooks
setting — is a read-only look by hand, because a clone's scratch branch is
not a property of the change being pushed.

### Desired-state hygiene

`tool/version-control/hygiene` scans the tracked tree for undeclared user and
host names, absolute home paths, tracked runtime state, and machine-unique
identifiers. It runs on every commit from `.githooks/pre-commit` beside the
secret scan and outside domain dispatch, and again in CI, because the invariant
is repository-wide rather than scoped to the domain being changed.

```sh
tool/version-control/hygiene
```

When it reports something, in order of preference:

1. Remove the value. A leaked value is desired state that names one machine.
2. If it is a user or host name that genuinely belongs in desired state,
   declare it in `modules/flake/inventory.nix` first. That is a `unixlike`
   change and lands as its own change.
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
`docs/definition-of-done.md`.

### Cross-domain reads

`tool/version-control/domain-reads` scans each domain's code in the index —
the flake, the modules and the Unix-like checks on one side, the Windows
scripts on the other — for a path that names the other domain's tree, with
comments stripped and payload trees left out. It runs on every commit beside
the hygiene scan and in CI, because a read across the boundary is a property
of two trees rather than of the domain being changed.

```sh
tool/version-control/domain-reads
```

When it reports something, copy what the other domain owns into the domain
that reads it; the destination then owns the copy (`docs/architecture.md`,
"Default rule: keep implementations separate"). There is no allow list: a
read across the boundary has no legitimate form.

### Design citations

`tool/version-control/design-citations` scans the index for a citation of a
design document from anything that carries authority. The adoption inlets are
excluded, so a decision record, a candidate and a provisional entry may name
the document they adopted from. It runs on every commit beside the hygiene
scan and in CI, because the document and the text citing it can be in any
scope.

```sh
tool/version-control/design-citations
```

When it reports something, decide which of the two the sentence is doing. If
it says where design documents live, name the directory rather than a file:
`docs/design/` passes and `docs/design/<file>` does not. If it rests on the
document's argument, that argument has not been adopted — record the decision,
promote the candidate or register the measure, and cite that instead. There is
no allow list.

Branch protection on `dev` and `master` requires the stable `Required checks`
job. That job fails unless classification and secret scanning pass and every
selected domain job succeeds. Conditional domain job names are deliberately
not branch-protection contexts because unselected domains are skipped.

## Documentation ownership

`Authority` says whether a location binds the repository. An internal
location is authority: it is read as a rule, it is the context an agent works
under, and it is where an obligation may rest. An external location argues,
observes or proposes, and binds nothing until an internal location adopts
from it.

| Location | Authority | Responsibility |
| --- | --- | --- |
| `README.md` | internal | Setup, outputs, and everyday use |
| `CONTRIBUTING.md` | internal | Domain-scoped workflow and releases |
| `AGENTS.md` | internal | Stable judgement and safety boundaries |
| `docs/architecture.md` | internal | Domain authority and dependency policy |
| `docs/status.md` | internal | Current state |
| `docs/decisions/` | internal | One record per expensive decision; `README.md` there is the index and format |
| `docs/troubleshooting.md` | internal | Recurring problems indexed by symptom |
| `docs/definition-of-done.md` | internal | Domain-specific evidence requirements |
| `invariants/` | internal | Enumerated invariants and how each one is enforced |
| `provisional/` | internal | Registered temporary measures and the condition that ends each |
| `.agents/skills/` | internal | Model-neutral workflows specific to this repository |
| `tool/`, hooks, CI | internal | Executable policy |
| `docs/candidates/` | external | Observed candidates for adding a rule or removing text; `README.md` there is the index and format |
| `docs/design/` | external | The argument for a direction, and what its plan predicts; `README.md` there is the index and format |
| `notes/` | none | Untracked maintainer scratch space; no structure, review or retention, and not project context |

The two external locations differ in size, not in standing. A candidate is
one observation waiting to become a sentence in an internal document; a
design document is a whole argument that may produce several. Neither is
cited by an internal location, and a design document is never deleted,
because an adoption record names it as its source.

Cross-project methods are maintained in the separate sibling `skills` project
and adopted explicitly. They do not become a source of project policy.

Repository text is English because the repository is public.
