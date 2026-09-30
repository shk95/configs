# Report: default-on flake input refresh
kind: report
spec: docs/work/unixlike/automatic-flake-refresh/spec.md
status: pending

## Plan delivery checkpoint, 2026-09-30

Continuation owner: D (`d_repository_docs`), issue #450. This checkpoint
reconciles the preserved automatic-refresh plan at
`2b074152fc2278c13fda50367854e921011e49b9` with origin/dev pickup
`86abcea4eadd1e4403ec9025eedb7009daf54886`. Only this plan pair was extracted;
the old branch, its other work documents and original worktree were preserved.

Read-only source inventory found six independently locked direct inputs:
`nixpkgs`, `flake-parts`, `import-tree`, `home-manager`, `nixos-wsl` and
`nix-darwin`. The latter three follow root `nixpkgs`; transitive `nixpkgs-lib`
and `flake-compat` are not direct selection names. Removed installer inputs
are not part of the tool contract. This reflects the accepted public
environment/host boundary and U1's machine-ownership transfer.

`tool/configs doctor unixlike` reported Ready with Nix 2.34.8. Read-only
`nix flake metadata --json --offline --no-update-lock-file
--no-write-lock-file path:./unixlike` and evaluation of the current input
declarations confirmed that inventory. Local Nix help confirmed named-input
update, explicit flake targeting, reference-lock and output-lock options;
temporary-write behavior and refusal cases still require implementation
fixtures. The original provider lock SHA-256 remained
`096037b79c002728b9ea3450237acefdfdc5e838f2deb0a377e52a22a69d70d2`.

The dated amendment defines source invocation/configuration, dynamic selection,
preserved exclusions/follows, temporary candidate validation, stale-source
rejection, atomic publication, empty/no-op/failure behavior and lock-only
fixtures. It preserves AC1-AC4 verbatim. This is plan/source-review evidence;
no updater, exclusion file, scheduler or lock change was implemented. All
acceptance rows below remain pending. Evaluation fixtures, real runtime proof
and final implementation review must be supplied by the later assigned worker.
There is no build, activation, Windows Apply, host-lock or release evidence.

## Pickup reconciliation, 2026-09-28

AC1-AC4 are unchanged. Earlier stage-design deferral is historical; tool fixtures
can be implemented independently when assigned, with final input wiring reconciled
to U1 ownership transfer. The tool still writes only provider flake.lock and has no
schedule, publication or private-host authority. No tool or lock was changed; all
implementation evidence remains pending.

Implementation evidence remains pending. Planning preflight verifies format only.

2026-09-27: retained as an earlier draft, with pickup deferred by the dated
spec amendment. Continue from the repository provider-release-contract study
for stages 2 and 3. No input or stateVersion change has been performed.

2026-09-28: the repository-owned schedule changed to daily refresh before
promotion. This tool's AC1-AC4 remain unchanged: selection, atomic lock writes
and no commit/deployment authority. No input was updated or tool implemented.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC2 | pending | |
| AC3 | pending | |
| AC4 | pending | |
