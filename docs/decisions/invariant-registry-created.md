# The invariant registry is created with pending entries

date: 2026-09-03
scope: repository
status: accepted
source: 9f1e8ce:docs/status.md § Invariant registry

Layer-3 invariants are enumerated under `invariants/<scope>/` as of
2026-09-03 (`INV repository/registry-coverage`). The 2026-09-02 audit found
twenty-one prose statements of which seven had no enforcement and four were
violated; the registry records each such statement as `pending` with an
issue rather than fixing it, so the gap is visible in
`tool/version-control/invariants` output on every commit. The repository
entries landed first; the Unix-like and Windows entries followed in their own
scopes.

2026-09-03: the Unix-like entries landed. 2026-09-04: the Windows entries
landed.
