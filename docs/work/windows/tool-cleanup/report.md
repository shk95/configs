# Report: Windows tool cleanup

kind: report
spec: docs/work/windows/tool-cleanup/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Evaluation and native runtime: Windows CI run [36134628694](https://github.com/shk95/configs/actions/runs/36134628694), Windows desired state job, returned `Windows desired state is valid.` through `win-env.ps1 validate` and ran `win-env.ps1 test`: 316 passed, 0 failed, 1 skipped. The entry-point fixture checks the target scripts and exit-status forwarding. On macOS the same test verb passed 302, failed 0, skipped 15; its validate verb returned 69 for missing `zellij.exe`, so that was not native evidence. |
| AC2 | verified | Fixtures and native runtime: commit `9a09752` removes the unreferenced wrapper and its candidate. The revised isolation fixture rejects generated reads of current payload, tool and module paths under `unixlike/`, while accepting a comment and a Windows-owned path. It passed in the local Pester run and the native Windows CI run [36134628694](https://github.com/shk95/configs/actions/runs/36134628694). |
| AC3 | verified | Codex reviewed commit `9a09752` on 2026-09-25: entry-point help, capture output, tests, status, invariants and definition of done name the current interface; dated decision records remain unchanged. |

## Evidence lanes

- Evaluation: native Windows CI run [36134628694](https://github.com/shk95/configs/actions/runs/36134628694) validated desired state. The macOS validation returned 69 because Zellij was unavailable there.
- Native runtime: Windows CI Pester passed 316, failed 0, skipped 1; the job and `Required checks` passed. This is test runtime on a Windows runner, not a host `check` or Apply.
- Fixtures: macOS Pester passed 302, failed 0, skipped 15; Windows CI covered the additional end-to-end capture cases. The isolation positive and negative fixtures passed in both runs.
- Review: Codex inspected the complete Windows diff at `9a09752` on 2026-09-25. `tool/version-control/work --staged`, invariants, domain reads and pre-commit policy checks passed; the change classified only as `windows`.
- Apply: not applicable; no desired host state was applied.
