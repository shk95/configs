# Report: select CI suites by change effect

kind: report
spec: docs/work/repository/ci-effect-selection/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Repository fixtures cover docs, lock, modules, payloads, deletion, cross-scope rename and shared dispatch inputs. Replaying #392's actual six-file diff selects no suite while retaining Unix-like ownership; #408's lock diff selects the Unix-like suite. Workflow review confirms global scans keep ownership outputs. |
| AC2 | verified | Repository fixtures reject unknown paths, malformed input, failed selection/scans, skipped or cancelled selected jobs, invalid booleans, unselected jobs running, native stack metadata and mismatched/layer event bases. Invariant and work checks pass. |
| AC3 | pending | Local repository suite passes on 2026-09-26, including the Git environment regression child. Hosted native CI is pending. Manual prose review found no account or machine identifier introduced by this change. |

## Limits

The CI mode narrows by documentation versus executable inputs, not by a full
dependency graph. Platform payload changes still select the whole native suite.
Shared CI machinery deliberately exercises unrelated platforms to verify its
routing. Native stacked PRs fail before selection; supporting them requires a
separate trunk-range and history-policy change. Cross-run reuse is absent, so
PR and push checks can repeat. No deployment or real-host readiness is claimed.
