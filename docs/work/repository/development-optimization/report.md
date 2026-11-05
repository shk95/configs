# Incremental development environment optimization results
kind: report
spec: docs/work/repository/development-optimization/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC2 | verified | Loop 1 corrects baseline guidance and consolidates four identical hook decisions; existing primary/linked and refusal fixtures pass in the cumulative repository suite after fixture dependency corrections. Independent review accepts the production change. |
| AC3 | pending | |
| AC4 | pending | |

## Baseline and preservation

Master remains e824c6f328edb9f9a73a66b5c00ae6523aefc23c. All 104 exploratory
files were checked byte-for-byte and by mode against the external archive;
all also match the retained stash payload. The 67 untracked files were moved
to retained external storage before the 37 tracked files were restored.
No scratch notes were read. Rework begins on a clean master-based repository
topic; no exploratory source commit or cross-scope topic was manufactured.

The exploration added 6,243 physical lines: implementation/configuration 699,
tests 1,779, operating documents 657 and work records 3,108. These are a
comparison with the exploration, not the success baseline for this work.

## Loop 1: existing inconsistencies and duplicated hook decisions

Baseline review found the README's brew authoring example targets an inventory
the provider does not have, the Darwin build evidence example already points
to a refusing recipe, and ownership prose incorrectly predicts CI selection.
Correct those instructions without adding an operation. The Darwin conflict
predates the exploration; it is not a regression introduced by it.

Four copies of tracked-hook resolution become one 30-line source-only helper.
The same callers, diagnostics and explicit setup mutation remain. This reduces
independently maintained decisions from four to one and removes 74 net lines
before documentary evidence. Primary/linked worktree and absent/foreign hook
tests establish behavior rather than a new capability declaration.

The first run exposed missing helper copies in the workflow, retirement and
primary/linked hook fixtures. After those corrections, `test-local-workflow`
passes and the cumulative `tool/configs test` exits 0 (log
`/tmp/configs-optimization-loop1-suite-fixed.log`). Missing alejandra skips the
mas-format fixture; installed Nix skips its missing-Nix case. No native Windows
or hosted evidence is inferred. Independent review found the copy omissions;
its production review found no additional blocker.

## Fixed comparison tasks

These are static source/task traces, not timed human or agent sessions. Both
sides allow an experienced operator to open the relevant section directly;
novice discovery and optional diagnostics are counted separately.

| Task | Start | Finish and preserved boundary |
| --- | --- | --- |
| S1 prose | Known repository paragraph needs correction; dirty work allowed. | Owning source/procedure corrected with document/global evidence; no artificial suite or commit obligation. |
| S2 Unix-like | A provider payload needs editing in an existing checkout. | Relevant format/lint/parser/provider evidence identified; consumer build/runtime remains separate. |
| S3 Windows | Native behavior changes, possibly authored on a foreign host. | Windows parser/Pester/Check requirements and unavailable lanes identified; no Nix prerequisite or Apply. |
| S4 continuation | A task already has workspace and authorization. | Actual Git state and relevant unfinished work recovered without reinitialization or renewed consent. |
| S5 verification | Full base/head on a clean committed candidate. | Optional inspection exposes selected commands without executing them; requested execution binds evidence to that candidate. Dirty narrow checks are a separate subject. |
| S6 publication | Local release/history snapshot needs inspection. | Read/refresh/write effects identified; no publication or rewrite follows from inspection. |
