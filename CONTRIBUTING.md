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
`tool/doctor.sh` is read-only. Pass `unixlike`, `windows`, `common`, or
`repository` to check only that scope; omit the scope for a complete host
inventory. A missing foreign-platform capability does not block scoped work.

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

Prefer a single scope per branch and pull request. If a common change and its
platform adoption are both needed, land them separately so neither release is
synchronously coupled to the other.

## Branch and commit flow

```text
master <- dev <- feature/<domain>-<topic> or fix/<domain>-<topic>
```

Examples are `feature/unixlike-shell`, `fix/windows-zellij`, and
`feature/common-terminal-colors`. Governance examples are
`feature/repository-vcs-audit` and `fix/repository-ci-dispatch`.

Use merge commits for completed work; do not squash or rebase published work.
Do not commit directly to `master`. Scope commits where practical, for example
`feat(unixlike):`, `fix(windows):`, `chore(common):`, or
`refactor(repository):`.

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
user explicitly requests those mutations. Activation and Windows Apply happen
after release and are not implied by a tag.

For agent-assisted work, invoke `run-version-control-workflow`. Its canonical
Agent Skills implementation is under `.agents/skills/`; model-specific
discovery files are adapters only. Audit and release planning are read-only by
default. This document remains the human fallback and the contract the skill
executes.

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
   evidence exists.
6. Activate only when explicitly requested, from the intended Unix-like
   release.

Do not add Windows desired state to a Nix module merely because the same tool
also runs on Windows.

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
.\windows\tools\setup-dev.ps1
.\windows\tools\check-desired-state.ps1
.\windows\tools\test.ps1
.\windows\bootstrap.ps1 -Check
```

`setup-dev.ps1` installs the contributor toolchain declared in
`windows/toolchain.json`, which is also what CI installs from, so local Windows
and CI use the same Pester discovery, scope, and assertion semantics and the
same Lua compiler. Without it the checks still run: a source whose parser is
absent is reported as unverified and the command exits 69, so Windows work
remains pushable from a clone that has not installed anything.

Apply is a deployment, not verification, and requires an explicit request:

```powershell
.\windows\bootstrap.ps1
```

A host may deploy part of the manifest with `-Minimal`, `-Feature`, `-Add`, or
`-All`; `README.md` describes the selection model. Selection is host state and
is recorded in `state.json`, so a change to the feature model is a Windows
desired-state change while a host's chosen set is not. Report which selection
produced any `-Check` or Apply evidence, because a check that passed under a
minimal selection says nothing about the features it excluded.

A change made in an application's own UI moves back into desired state with
`.\windows\tools\capture.ps1`, which reads the managed targets, writes only
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
than working around them, and read the hook output under its commit rather
than assuming a hook ran: whether the POSIX hooks execute under Git for
Windows is recorded in `docs/status.md` as an open question.

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

## Common changes

Do not create common material by default. First show that independently owned
Unix-like and Windows implementations have stable, genuinely platform-neutral
semantics.

When common ownership is justified:

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

```sh
tool/version-control/test
tool/version-control/audit
tool/version-control/audit-remote  # when gh is authenticated
```

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

Branch protection on `dev` and `master` requires the stable `Required checks`
job. That job fails unless classification and secret scanning pass and every
selected domain job succeeds. Conditional domain job names are deliberately
not branch-protection contexts because unselected domains are skipped.

## Documentation ownership

| Location | Responsibility |
| --- | --- |
| `README.md` | Setup, outputs, and everyday use |
| `CONTRIBUTING.md` | Domain-scoped workflow and releases |
| `AGENTS.md` | Stable judgement and safety boundaries |
| `docs/architecture.md` | Domain authority and dependency policy |
| `docs/status.md` | Current state and expensive decisions |
| `docs/troubleshooting.md` | Recurring problems indexed by symptom |
| `docs/definition-of-done.md` | Domain-specific evidence requirements |
| `.agents/skills/` | Model-neutral workflows specific to this repository |
| `tool/`, hooks, CI | Executable policy |

Cross-project methods are maintained in the separate sibling `skills` project
and adopted explicitly. They do not become a source of project policy.

Repository text is English because the repository is public.
