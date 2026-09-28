# Report: Unix-like provider and host customization
kind: report
spec: docs/work/unixlike/provider-consumer-contract/spec.md
status: pending

## Cross-work reading and dependency reconciliation, 2026-09-28

Latest-reading guidance separates current U1/U2 contracts from retained historical
proposals. Candidate template proof, provider PR integration and required template
delivery before release are distinct; no circular unpublished-tag dependency or
recurring private-host CI gate is intended. Selective evidence remains bounded to
changed functions. This is documentation reconciliation only, with all rows pending.

## Capture scope narrowed, 2026-09-28

The maintainer explicitly excluded compatibility/reconciliation for host-owned
capture extensions, including overlap with future configs features. Latest AC3
amendment records the two-input surface, managed-key semantics and host-invoked
pinned tool with explicit destination. No generic extension registry or extra
private-host verification is planned. These remain design decisions; no new source,
capture, native execution or acceptance evidence was produced.

## Darwin capture ownership design, 2026-09-28

The maintainer accepted whole capture-unit ownership transfer, a versioned JSON
envelope with explicit source selection, bounded schema compatibility and separate
preview/save/apply. This supersedes proposed Darwin baseline/delta merging only;
Windows retains its own contract. Existing Karabiner module/tool and root capture
entry were inspected read-only. Current activation still reads provider payloads
directly, and root capture still targets provider source. New host-data consumption,
format checks and save flow are unimplemented. No live app capture, build, native
read verification or activation was performed; AC3 remains pending.

## Single-flake consumer planning, 2026-09-28

The maintainer adopted the latest spec's single-flake dendritic consumer/template
direction and U1 delivery boundary. Read-only inspection found seven current host
flakes/locks and their existing per-directory check loop. No consumer or template
source was modified; new topology, connection helpers, shared-lock transition and
new API remain unimplemented. All criteria remain pending.

## Bounded connection and baseline investigation, 2026-09-28

Nix 2.34.8 was reported ready by tool/configs doctor unixlike. A temporary external
consumer pinned github:shk95/configs/e11bd1368d2f5138ad0f9b7017040b2b76e055e6?dir=unixlike
and followed configs/nixpkgs. Evaluation returned the three current lib constructor
exports, identical followed nixpkgs outPath, injected system/home values, Darwin
hostname and standalone username. These used the existing constructor schema, not
the planned schema. A path probe confirmed configs.outPath is the flake subdirectory
and configs.sourceInfo.outPath is the repository source root. The planned contract
file is absent. No full derivation evaluation, build, runtime or activation evidence
is claimed. A temporary consumer lock was created; provider inputs were not updated.
The initial /tmp symlink path failed and evaluation succeeded using /private/tmp.

The provider pins nixpkgs e94cb152ed51bd6e24eb4a41f1460252beb52cd2. Source inspection
of 26.05/26.11 stateVersion branches followed by selected option evaluation found
postgresql, mysql, grav, netbox, dovecot2, taskchampion-sync-server, hyphanet, lauti,
sabnzbd, tandoor-recipes, olivetin and nextcloud disabled, and boot.zfs.enabled false,
in fixture-wsl (26.05), fixture-vm (26.05) and fixture-desktop (26.11). This bounded
search/evaluation found no active member of those inspected changes. It does not
prove all indirect default effects, whole-output equality or real-host migration.
Home Manager already declares 25.11 and Darwin 6; conversion to overridable defaults
still requires implementation and checks. No acceptance row is completed.

Subsequent accepted design adds minimal contract contents, optional explicit host
declarations, host-owned sops+age extension boundaries and a small changed-function
check map. See the latest spec amendment. Reader and new API are not implemented.

## Post-audit design consolidation, 2026-09-28

The latest spec amendment records accepted concrete inputs, host-owned hostname,
overridable stateVersion baselines, public connection/data paths and narrowed
change-driven verification. Existing check sources were reviewed, not executed.
The environment examples are not required recurring suites. Actual consumer proof,
transition effects, implementation and selected evidence remain pending. This
entry supersedes earlier broader evidence and stateVersion ownership descriptions
where they conflict; it verifies no acceptance row.

Design agreed on 2026-09-27. Adjacent study.md preserves pre-implementation
evaluation evidence. The original centralization plan is superseded by the
2026-09-28 amendment. Constructor migration and host capture are not implemented;
no activation is certified by this report.

On 2026-09-27 the maintainer selected macOS 26 as the first formal Apple
Silicon support baseline. AC5 remains pending until the adopted contract and
complete required native evidence exist. The planning investigation evaluated
all seven current provider fixture derivations on macOS 26.6.2 with Nix 2.34.8;
it did not build or activate them and does not complete AC5.

The maintainer also selected upstream Nix 2.34.8 as the initial exact CI
baseline on 2026-09-27. AC6 remains pending: local evaluation does not establish
the required CI installation or full native build evidence.

On 2026-09-28 the maintainer confirmed environment selection plus host modules.
The dated spec amendment revises AC1/AC2/AC4/AC5 and adds AC7/AC8. It preserves
host-owned NixOS stateVersion and separates public provider evidence from private
machine realization/use. Exact coverage, WSL dependency wiring, administration
boundaries and HM/Darwin migration ownership remain design work. All rows remain
pending; document validation is not implementation or runtime evidence.

Later on 2026-09-28 the maintainer confirmed provider-owned compatibility
baselines with host-owned adoption and persistent-state migration. The latest
AC1 amendment supersedes the earlier same-day host-owned value choice. Exact
initial values, any compatibility escape hatch and concrete transition evidence
remain pending. No effective stateVersion, consumer pin or host data was changed.

## Latest design consolidation, 2026-09-28

The latest dated spec consolidation records environment/host ownership and
domain API/template contracts. All implementation and live evidence remains
pending, including the new API criterion. Document preflight is form validation,
not evaluation, build, native runtime, activation/Apply or live automation proof.
No source implementation, Git publication or host mutation was performed.

## Delivery refinement, 2026-09-28

U1 now names a coherent public environment/host contract outcome, dependencies,
evidence and stop conditions. Ubuntu 26.04 LTS x86_64 is the first standalone
baseline; the live 26.04.1 WSL OS read is identity evidence only. Earlier claims
that initial stateVersion values remain open are superseded by 25.11/25.11/6;
transition analysis remains pending. Required/advisory contract checks replace
blanket machine/session certification. Input schema, WSL wiring, ownership map
and contract export still need resolution before pickup. All rows remain pending.

## Independent review follow-up, 2026-09-28

Accepted independent-review corrections are now recorded in the owning specs.
They clarify cutoff/candidate timing, complete-delta check selection, template
delivery, initial reader bootstrap and host-local applied-state capture. All
implementation evidence remains pending; this update is design acceptance only.

## File-level delivery preparation, 2026-09-28

The spec now maps current source groups to retained provider behavior, host
transfer or split ownership, with corresponding evidence and completion conditions.
It records the accepted public-input and generated-contract approach and one-time
transfer evidence, without private-host CI dependency. No migration, build, native
test, activation or implementation completion is claimed. All rows remain pending.

## Final independent planning audit, 2026-09-28

An independent agent reviewed all five work items against latest accepted
amendments and confirmed the previous five corrections without identifying a
new direction conflict. This is planning review only. Concrete consumer paths,
U1 types/transitions/evidence and later lane prerequisites remain; all acceptance
rows stay pending and no implementation or live rollout is certified.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC9 | pending | |
| AC2 | pending | |
| AC3 | pending | |
| AC4 | pending | |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
