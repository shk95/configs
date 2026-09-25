# Report: repository tool call cleanup

kind: report
spec: docs/work/repository/tool-cleanup/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Fixtures: `tool/version-control/test` passed locally and in the pre-commit gate for `1d3a61d`, covering both entry-point verbs, a failed validate verb in pre-push, and immediate CI exit checks for setup, Zellij, validate and test. Affected dispatch: the staged change selected `repository:fixtures`; the fixture exercised the selected Windows hook path with Unix-like and Windows PowerShell stubs. Native Windows runtime remains for the Windows-scope PR. |
| AC2 | verified | Codex reviewed commit `1d3a61d` on 2026-09-25: the nonexistent worktree installer is gone; root current guidance, troubleshooting, invariant explanation, status and fixtures no longer depend on the Windows private tool directory name. Historical decision records retain their dated paths. |
| AC3 | verified | Policy checks: pre-commit on `1d3a61d` passed hygiene, domain reads (131 Unix-like and 14 Windows files), design citations, work (27 items, 23 pairs), invariants (73 registered), provisional (2 registered) and gitleaks. Codex reviewed the removal of the two resolved repository candidates and the staged `repository` classification on 2026-09-25. |

## Evidence lanes

- Fixtures: `tool/version-control/test` passed on 2026-09-25, including the pre-commit run for `1d3a61d`. Its Windows stubs prove caller routing and refusal, not Windows runtime behavior.
- Policy checks: pre-commit on `1d3a61d` passed the repository gates; `tool/version-control/work --staged` and `git diff --cached --check` passed before the implementation commit.
- Affected dispatch: `git diff --cached --name-status | tool/dispatch/select push` selected `repository:fixtures`. This repository-only change skips the native Windows CI job; the Windows-scope PR must supply that lane.
- Review: Codex inspected the complete implementation diff at `1d3a61d` and resolved the two repository candidates on 2026-09-25.
