# Measure Windows test cost before narrowing coverage
kind: spec
date: 2026-09-26
scope: windows
status: approved
review-by: 2026-10-26
issue: #410

## Decisions

Use the existing pinned Pester result to expose per-container and slow-test
execution time without running tests twice. Keep the full native suite and its
exit contract. Investigate feature selection and duplicate process checks;
remove a check only when its distinct failure coverage is demonstrably retained.
Windows human capture auto-merge remains its own contract, independent of agent
worker admission policy. Repository CI dispatch is owned by a separate worker.

Rejected: disabling E2E, choosing tests from deployment feature names without
an impact model, or claiming a faster runner proves an optimization. Native
Windows CI is authoritative; foreign-host checks are supplementary.

## Increments

1. Native runtime verifies bounded timing output from the existing test run and
   unchanged suite results. Review records measured costs and safe or deferred
   optimization candidates in the same Windows pull request.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The normal Windows test command reports suite durations and at most ten slow executed tests from its existing Pester result, without changing selection or success/failure semantics. | native runtime, review |
| AC2 | The report compares native observations with run 36207658666 and distinguishes measured costs, distinct process contracts, and unsafe or unmeasured selection candidates. Human capture auto-merge coverage is preserved. | native runtime, review |
