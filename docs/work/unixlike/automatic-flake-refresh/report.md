# Report: default-on flake input refresh
kind: report
spec: docs/work/unixlike/automatic-flake-refresh/spec.md
status: done

## Implementation verification, 2026-09-30

The assigned tool/connection lane resumed in its original dedicated worktree
at pickup `6e80f2d1edc09d123c13d8faeef0ba49961d104f`, preserving reviewed
spec-content revision `a846ff7451c0a054332f69e6e817fc535000f7a4`.
The operator entry point, standard-library engine, empty exclusion file,
`just up` delegation, documentation and registered fixtures now implement
the accepted boundary. Repository scheduling remains separately owned.

Evaluation and native CLI proof: `unixlike/tool/checks/refresh-inputs-test`
passed on aarch64-darwin with actual Nix 2.34.8 and functional locked Python
3.14.7. Disposable local Git flakes exercise default selection, a new direct
input, excluded dependent source preservation while its followed owner changes,
unknown/duplicate/follows-alias/invalid configuration, an excluded new source
without a baseline, all-excluded no-update selection, byte-preserving no-op
and a real missing-local-upstream refusal. Controlled wrappers separately
inject candidate corruption, excluded-source corruption, update/validation
failure and stale lock/config/source/permission-mode edits; these prove failure handling and
are not successful-upstream claims. Successful/no-op/failure snapshots permit
only the disposable lock to change; stale external edits are retained.

Review found that fingerprinting symlink names cannot guard external target
changes. The tool now refuses provider source symlinks, including a symlinked
lock or exclusion file. Actual fixtures prove lock/config/file/directory-link
refusal and target preservation; the current provider tree has no symlinks.
The initial lock/config reads are bound to their source snapshot, and a final
snapshot is checked immediately before publication. Source snapshots include
bytes and permission modes; the mode fixture proves
that an executable-bit edit is retained and stale publication is refused.
A cooperating directory claim serializes refreshes; the fixture proves claim
refusal. Candidate
validation precedes same-directory atomic replacement, and unchanged locks
preserve original bytes. This is complete-file publication on a filesystem
supporting atomic rename, not arbitrary-writer compare-and-swap or a power-loss
durability guarantee. Runtime recovery instructions distinguish interruption
before publication from a complete old/new lock at the publication boundary.

The entire tracked/untracked source and prose were reviewed for ownership,
permanent write boundaries, hidden Git/deployment calls and account/host
identity. The engine invokes only Nix, writes only the provider lock permanently
and cleans its runtime artifacts on normal exit. Fixture Git operations occur
only in disposable local repositories with ambient Git configuration/transport
restricted. The actual whole `Justfile` was executed against a disposable
provider from another caller directory, proving the public `up` delegation;
it preserved exact bytes in the no-op case.

Read-only provider connection proof used
`nix shell --no-update-lock-file --no-write-lock-file --inputs-from path:./unixlike nixpkgs#python3 --command unixlike/tool/refresh-inputs --check`.
It selected all six independent direct inputs: flake-parts, home-manager,
import-tree, nix-darwin, nixos-wsl and nixpkgs. The exclusion list is empty;
home-manager, nixos-wsl and nix-darwin retain their root nixpkgs follows.
No real provider refresh was run; lock SHA-256 remains
`096037b79c002728b9ea3450237acefdfdc5e838f2deb0a377e52a22a69d70d2`.

Formatting and lint/composition checks passed. `CHECKS_BUILD_TARGETS='' unixlike/tool/checks/test`
passed and evaluated all seven synthetic Home Manager/NixOS/Darwin outputs;
foreign outputs remain evaluation-only and the native Darwin build was not
selected in this local evaluation run. Staged classification is Unix-like;
work, invariant registration, design-citation and record checks passed.
The subsequent normal pre-push harness on implementation source
`44977647308f09d61ea1d640dfe0f39653de4979` independently passed the actual
refresh fixtures, all seven evaluations and the selected native
`darwinConfigurations.fixture-mac` build. Foreign outputs remained
evaluation-only; the push audit reported zero warnings and failures.
Build: this lane adds an
operator source tool, no package or host module; its actual native CLI fixture
is the runtime proof. Activation, Windows Apply, host locks, schedule,
credentials, promotion and release were not performed. Final published-head
CI and Ready delivery are tracked by the PR and do not become evidence merely
because these local checks passed.

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
| AC1 | verified | Actual local Nix default/new-input fixtures and read-only six-input provider inventory; dynamic graph-derived selection reviewed. |
| AC2 | verified | Actual exclusion/follows and invalid-exclusion fixtures; baseline/candidate own-source comparison and operator semantics reviewed. |
| AC3 | verified | Actual empty/no-op/missing-upstream cases, controlled update/validation/candidate/stale faults and serialization/symlink refusal; complete atomic publication boundary reviewed. |
| AC4 | verified | Entire source/prose review, all-source fixture snapshots, empty tracked config, runtime prerequisite refusal and disposable public Justfile delegation; no real provider lock change. |
