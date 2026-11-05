# Contributing

This is the workflow for people and tools. `AGENTS.md` contains stable
judgement and safety rules, `docs/policy/architecture.md` defines domain ownership,
and `README.md` contains usage.

Repository text is English because the repository is public.

Read the [procedure index](docs/development/README.md) for one task concern.
The headings below preserve existing links; each procedure has one full text.

## Prepare a clone

See [Prepare a clone](docs/development/environment.md#prepare-a-clone).

## Classify the change

See [Classify the change](docs/development/authoring.md#classify-the-change).

## Branch and commit flow

See [Branch and commit flow](docs/development/authoring.md#branch-and-commit-flow).

## Local verification and integration

See [Local verification and integration](docs/development/verification.md#local-verification-and-integration).

## Local work and handoff

See [Local work and handoff](docs/development/handoff.md#local-work-and-handoff).

## Workspace preservation

See [Workspace preservation](docs/development/handoff.md#workspace-preservation).

## Candidate CI without a PR

See [Candidate CI without a PR](docs/development/publication.md#candidate-ci-without-a-pr).

## GitHub integration

See [GitHub integration](docs/development/publication.md#github-integration).

## Explicitly approved history maintenance

See [Explicitly approved history maintenance](docs/development/publication.md#explicitly-approved-history-maintenance).

## Add or change governance

See [Add or change governance](docs/development/governance.md#add-or-change-governance).

## Add or change an invariant

See [Add or change an invariant](docs/development/governance.md#add-or-change-an-invariant).

## Register a provisional measure

See [Register a provisional measure](docs/development/governance.md#register-a-provisional-measure).

## Retire, extend or promote a provisional measure

See [Retire, extend or promote a provisional measure](docs/development/governance.md#retire-extend-or-promote-a-provisional-measure).

## Plan and verify work

See [Plan and verify work](docs/development/handoff.md#plan-and-verify-work).

## Record a decision

See [Record a decision](docs/development/governance.md#record-a-decision).

## Observe before adding or removing

See [Observe before adding or removing](docs/development/governance.md#observe-before-adding-or-removing).

## Unix-like changes

1. Put feature declarations under their owning `unixlike/modules/` concern.
   For structure/composition, read [module layout](docs/policy/architecture.md#unix-like-module-layout).
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

Prepare missing native tools explicitly with `windows/win-env.ps1 setup-dev`;
that operation installs development dependencies. Native read-only verification is:

```powershell
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

See [Verify](docs/development/verification.md#verify).

## Bounded scheduled release

See [Bounded scheduled release](docs/development/publication.md#bounded-scheduled-release).

### Input patch operation

See [Input patch operation](docs/development/publication.md#input-patch-operation).

### Manual operation and recovery

See [Manual operation and recovery](docs/development/publication.md#manual-operation-and-recovery).
