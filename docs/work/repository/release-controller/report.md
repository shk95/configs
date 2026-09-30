# Report: disabled release controller and pure recovery fixtures
kind: report
spec: docs/work/repository/release-controller/spec.md
status: pending

## Pickup and proof boundary

Root assigned B through parent issue #451 on 2026-09-30. Execution base is
5204457ee9d16ff934b2b2260471202784c6c6c9; reviewed pickup delivery is
c35feccf35e4824ee92383c20025a2a2e6fc7582. The dedicated linked workspace and
branch are recorded in the spec and local checkpoint. This pair is prepared for
root review before source implementation. Document preflight proves form only.

The disabled controller source and seven pure proof-family fixtures are prepared.
Local narrow fixtures and the full repository suite passed on 2026-09-30 with
existing Python 3.13.15 and Git 2.55.0 on macOS. Working-tree/staged work, invariant
registry (77 entries), hygiene, domain-read, design-citation, records, provisional,
whitespace, shell syntax and Python syntax checks passed. Source review corrected
one workflow-fixture `choices`/`options` assertion failure, then reran the narrow
suite successfully. Historical observation lists preserve unknown-to-applied
replay; stop-race observation and two-domain partial recovery cases also pass.
The local suite includes supplied fake API transcripts and disposable file-only
repositories, without live transport. The full suite exercised inherited routing
isolation and the retained R-preview/classifier. A normal temporary source update
between independent fixture families does not provide an immutable-head CI claim.
The first normal source commit hook reported controller fixtures unverified
because its default Python shim was unavailable; the separate local suite used
the discovered functional runtime and passed. Subsequent delivery commands bind
that existing runtime explicitly. No failed/unverified check is recorded as pass.
Self-review then strengthened observed remote ID grammar, actual merge-commit SHA
binding and canonical synthetic annotated-tag object bytes, with narrow reruns.
Draft source head 95d4f836dc946944547c72837a537f8867ac11dd's
[CI 36705255125](https://github.com/shk95/configs/actions/runs/36705255125)
passed Linux repository, Unix-like and policy scans but failed native Windows
controller launch: guarded MSYS script paths reached native Python as an incorrect
drive path. Explicit native script conversion and normalized Python-to-sh paths
repair that owning-source failure. Windows desired-state also failed independently
while winget obtained Lua (`0x8a15000f`, source data missing); no Windows source
repair is claimed. A new published-head successful native/dispatch run is required.
Final hardening drops ambient credentials/execution overrides from child runtime
environments and rejects contradictory duplicate/parent/head record histories;
separate old-package fixtures refuse both missing evidence and missing approval.

All seven child rows remain pending until published source-bound native Windows,
affected dispatch and reviewer evidence are complete. Parent
`provider-release-contract/report.md` remains pending with zero
of fourteen criteria verified; its domain/live obligations and R-manual and
R-scheduled lanes are not replaced by this child. Delivered R-preview evidence
is independent. No live transport, credentials, Environment, schedule, dispatch,
cancel, promotion, tag/release or host operation occurred.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC2 | pending | |
| AC3 | pending | |
| AC4 | pending | |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | |
