# Report: native Windows CI runtime binding
kind: report
spec: docs/work/repository/windows-ci-runtime/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC2 | pending | |
| AC3 | pending | |
| AC4 | pending | |

## Local preparation

Pickup base: cfd6d2718dc048cc1803e95267113d66f54e603d, current origin/dev after
the Windows declaration/reader and companion evidence prerequisites entered.
The approved dedicated spec/report was created and preflighted in this
task-dedicated linked worktree; the runtime selector remains Windows-owned.

Foreign-host PowerShell 7.6.6 parses all five CI source/fixture files and reads
the trusted Windows declaration. Harmless synthetic ZIP hash acceptance/refusal
and native child exit 0/23/69 checks pass on macOS; these are limited helper
checks, not native Windows identity or bootstrap evidence. Repository fixtures,
staged registry (73 registered, zero pending/untagged units), work preflights and
whitespace checks pass. Actual dispatch selects repository, Unix-like and
Windows suites because shared workflow input changed. No configuration source,
Windows selector/reader, public operator interface or B preview registration
was changed. Native evidence is pending and every acceptance row remains pending.

The first native run (36659135714, head bc66c84634ba37fac77c72d0734def074e69bdcb)
verified the archive and actually executed management 7.6.6/x64, then refused
the identity probe because its comparison included every PATH candidate. The
probe now selects the first application candidate, matching native invocation
resolution. This failed run is diagnostic evidence, not completed acceptance;
the repaired head requires new native and selected-suite evidence.
