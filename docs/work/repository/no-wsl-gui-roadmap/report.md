# Report: remove WSL GUI from the active roadmap

kind: report
spec: docs/work/repository/no-wsl-gui-roadmap/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review at `6a9cd34`: `docs/work/roadmap.md` has no WSLg row, and its former #21 paragraph directs any new proposal through the Unix-like architecture and invariant first. |
| AC2 | verified | Review at `6a9cd34`: `README.md`, `docs/policy/architecture.md` and troubleshooting state the current command-line boundary. The 2026-09-19 work-model spec keeps its original table with a dated 2026-09-24 correction. `git diff --check`, `tool/version-control/work --staged` and the repository pre-commit policy scans passed; the Windows WSLg version-parser test was left intact because it does not configure GUI support. |

## Evidence lanes

- Review: verified at `6a9cd34` against the active roadmap and the historical work-model spec.
- Policy checks: repository pre-commit hygiene, domain reads, design citations,
  records, work, invariants, provisional and gitleaks passed at `6a9cd34`.

No configuration output, native runtime or host activation is claimed.
