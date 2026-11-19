# Verification and publication gates report
kind: report
spec: docs/work/repository/verification-gates/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Local Git fixtures exercise full commit messages, merge-only paths and lock values, receiver-bound pushes and tag reachability. Gitleaks 8.30.1 refused synthetic credentials present only at a merge, in reverted side history, and at a root. Clean controls passed. The wiring fixture checks that CI invokes only incoming-mode audit and secret scans. |
| AC2 | pending | Local selection, gate and event fixtures pass. Release declarations, release workflow edits, Git for Windows fixture inputs and both Windows runtime declaration inputs have distinct coverage. Live native job verification and its proof binding are pending. |
| AC3 | pending | Local fixtures bind both consumers to the same versioned, attempt-specific result. Refusals cover the wrong workflow, source, unit, platform, checkout, job or artifact. The first live PR artifact is pending. |
| AC4 | verified | Local Git and simulated Actions fixtures exercise the exact-merge provider reuse path and refuse wrong trees, expired evidence, other attempts and unproven runtime checks. Hosted proof replaces the covered local commands while the current provisional policy still vetoes. Release writer fixtures refuse changed PR metadata and master and confirm an immutable tag with its run and attempt. |
| AC5 | pending | Procedure and final regression verification are in progress. |

## Qualification

The initial reorganization was exercised in a disposable snapshot of the
current checkout on macOS. The complete repository suite passed, including 22
workflow, 20 mechanical, 14 staged-check and 21 release cases. Repository
policy scans and actionlint passed. PowerShell parsed the changed Windows
controller, which supplies syntax evidence. Hosted native Windows execution,
provider builds and deployment evidence belong to their respective checks.
The released master and its tag serve as the source baseline for this work.
