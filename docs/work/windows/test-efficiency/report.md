# Report: Windows test efficiency
kind: report
spec: docs/work/windows/test-efficiency/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Native runtime: [run 36221342095](https://github.com/shk95/configs/actions/runs/36221342095/job/108347079999), source 24429e2, passed 320 tests and skipped one; two suite durations and ten executed-test durations printed. Review: one existing Invoke-Pester call, unchanged selection and exit check. Supplementary synthetic Passed/Failed result checks returned 0/1 and bounded twelve results to ten lines. |
| AC2 | verified | Native runtime: run 36221342095 retained the baseline 320 passed / one skipped result and measured the costs below. Review of source 24429e2 and the unchanged tests distinguishes automation, public wrapper, legacy shell, Appx transport and human capture E2E contracts. No test was removed or filtered. |

## Investigation and boundaries

The previous native run [36207658666](https://github.com/shk95/configs/actions/runs/36207658666)
spent 149s in the Windows job, 106.44s in WinEnv and 0.698s in WslConfig.
It recorded 320 passed and one skipped test. Those are different timing levels;
job preparation is not Pester test time.

The implementation reads Pester 5.7.1's existing result once. Container duration
includes discovery and setup; individual test duration is user plus framework
time and does not distribute every container overhead. The top ten report is
bounded, includes failed executed tests, excludes cases Pester marks unexecuted,
and precedes the unchanged failure exit. No second run, timing threshold,
external timing store, test filter, or repository workflow change was added.

Review of process checks found distinct boundaries, not a safe deletion:

- Direct bootstrap missing-prerequisite results verify the implementation.
  Public `check` forwarding verifies a different caller and status propagation.
- Direct validation and test-script missing-tool cases prove automation can
  call each implementation without the public wrapper; neither replaces the
  wrapper's binding-error and unknown-verb cases.
- Windows PowerShell 5.1 is a different bootstrap runtime from pwsh 7.
- Appx timeout, output-drain timeout, invalid UTF-8 and request validation
  cover separate transport failures. Shortening timeout tests without a
  startup handshake risks runner-dependent false failures.
- Capture module fixtures and capture child-process E2E cross different
  boundaries. Confirmation, hook refusal, partial commits, resumed publishing,
  and human auto-merge remain covered. Similar assertions are not proof of
  redundant execution.

Feature filtering is deferred: deployment feature names do not describe the
shared WinEnv module, capture publication, script entry points or toolchain
impact. A safe future selector needs explicit dependencies, conservative
fallback for module/toolchain/unknown changes, and positive/negative selection
proof. The separate repository CI worker owns docs-only platform suppression.
WslConfig's subsecond baseline makes it a low-priority target.

## Supplementary evidence

The publishing hook on a non-Windows host passed 304 tests, failed zero and
skipped 17 in 42.72s, and printed two suites plus ten executed-test timings.
Desired-state KDL parsing remained unavailable there. These results are not
native Windows or host readiness evidence. Policy hooks passed. No activation,
Apply, release, branch integration, or real human capture was performed.

## Native measurements

[PR #414 native job](https://github.com/shk95/configs/actions/runs/36221342095/job/108347079999)
ran source 24429e2 on Windows Server 2025, image windows-2025-vs2026
20260922.246.2, with native E2E enabled. Required checks passed.

| Measurement | Baseline 36207658666 | Run 36221342095 |
| --- | --- | --- |
| Windows job | 149s | 165s |
| WinEnv container | 106.440s | 112.146s |
| WslConfig container | 0.698s | 0.707s |
| Passed / failed / skipped | 320 / 0 / 1 | 320 / 0 / 1 |

| Slow executed test | Seconds |
| --- | --- |
| Appx payload under Windows PowerShell 5.1; name carried as data | 4.294 |
| Capture two features; title and both commits | 3.821 |
| Capture confirmation, push, PR and human auto-merge | 3.593 |
| Capture second commit rejected; disclose earlier commit | 3.586 |
| Capture reuses existing PR | 3.558 |
| Capture pre-push hook rejects | 3.400 |
| Capture commit rejects before push | 3.253 |
| Resumed capture refuses staged or dirty payload | 3.016 |
| Resumed capture publishes already-pushed branch | 2.809 |
| Direct validation unavailable / required-native failure | 2.643 |

Eight of the ten slowest tests cross the capture E2E boundary. Their distinct
failure/recovery assertions are retained. No redundant process check was
established in this bounded review. Fixture-repository setup costs within
these cases remain unmeasured separately: measure those phases before trying
to share mutable fixture repositories or replacing actual child invocations.
The legacy Appx query includes both absence and hostile-name controls; dropping
one would remove coverage. No test was removed solely for being slow.

This change is a measurement improvement, not a demonstrated speedup. The two
runs use different executions and job provisioning costs; the timing difference
cannot establish a regression or improvement from the diagnostic lines. The
measurements locate the next investigation and do not set a flaky speed gate.
Native validation and Pester are evidence for the tooling and fixtures; build
and activation/Apply are not applicable to this diagnostic-only change. No
host deployment readiness is certified.
