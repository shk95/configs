# CI runs the Windows checks through the entry point rather than the scripts directly

kind: addition
scope: repository
first-observed: 2026-09-05
target: .github/workflows/ci.yml Windows step; the README and CONTRIBUTING sentence saying CI and the hooks call the scripts directly
promote-when: a Windows script CI runs in-process is removed from the entry point's verb table, or the CI Windows step is edited anyway
drop-when: no new occurrence by 2027-03-05

## Observation

The CI Windows step runs `check-desired-state.ps1` and `test.ps1` in-process and reads `$LASTEXITCODE` after each. That read is sound only because both scripts end in an explicit `exit`, which the entry-point fixture holds for scripts in the verb table. CI's callees are in that table today by coincidence, not by construction; `setup-dev.ps1` is run without its status being read, and a `winget` call leaves a stale status that nothing pre-zeroes. Routing CI through `win-env.ps1 validate` and `win-env.ps1 test` would make the covered set the set CI uses. No false status has been observed.

## Evidence

- `.github/workflows/ci.yml` Windows step; `windows/tests/WinEnv.Tests.ps1`, the case "every verb names a script under tools that ends in an explicit exit".
- Audit of 2026-09-05 (ledger); the controller verified that both CI callees end in `exit`.

## Occurrences

- 2026-09-05: observed in audit; no failure.
