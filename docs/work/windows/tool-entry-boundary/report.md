# Report: keep Windows operator and automation commands separate
kind: report
spec: docs/work/windows/tool-entry-boundary/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Fixtures: `INV windows/automation-tools-standalone` exercises direct `check-desired-state.ps1` and `test.ps1` child processes with missing prerequisites, verifying exit 69 and required-native exit 1. Native runtime: [PR #406 Windows CI run 36207364118](https://github.com/shk95/configs/actions/runs/36207364118) invoked `setup-dev.ps1`, `check-desired-state.ps1`, and `test.ps1` directly with immediate exit checks; the job passed and Pester reported 320 passed, 0 failed, 1 skipped. |
| AC2 | verified | Fixtures: the native suite retains `INV windows/entry-point-forwards-status` coverage of `windows/win-env.ps1` argument and status forwarding, including unknown verbs. Review of the Windows diff and help examples confirms people are directed to `windows/win-env.ps1`, while automation uses `windows/tool/`. Independent Astra medium review found no actionable defect. |

## Evidence lanes

- Fixtures: native Windows Pester in run 36207364118 passed 320 tests, failed 0, skipped 1; foreign-host PowerShell passed 304, failed 0, skipped 17, with native-only cases correctly unavailable there.
- Native runtime: run 36207364118 used the repository PR #405 direct-call CI routing and passed `Windows desired state` plus `Required checks`. This proves direct success on Windows; the fixtures prove unavailable and required-native failure statuses.
- Review: an independent Astra medium review inspected the Windows diff, preserved public entry point contract, and merged CI routing on 2026-09-26; no actionable finding remained.
