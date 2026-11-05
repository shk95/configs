# Simplify existing Unix-like development operations
kind: spec
date: 2026-11-05
scope: unixlike
status: approved
review-by: 2026-11-19

## Goal and scope

Optimize existing provider operations from master
e824c6f328edb9f9a73a66b5c00ae6523aefc23c in the selected current checkout.
Keep this topic independent of the repository optimization topic. Preserve
recipe names/arguments/aliases, consumer authority and actual host utilities.
No source-preparation engine, capability manifest, input update, activation,
publication or master integration is part of this work.

Start with unreachable provider-host recipe bodies and incorrect flake paths.
Separate work/effect labels where the existing menu conflates verification,
observation and mutation. Consider consumer info's implicit local writes as a
deeper boundary candidate; adopt only if a small read-only path is justified.
Each loop receives independent review, correction and rereview, with one report
for the scope. Stop after the concrete paths are coherent; no universal runner
or additional optimization strength is required.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Existing provider-host refusal interfaces retain signatures and aliases, but no longer perform unnecessary host reads or contain unreachable realization bodies. Active utilities retain their effects and menu/documentation identify them. | fixtures, review |
| AC2 | Active named input refresh and formatting bind the owning flake, preserve literal arguments and refuse option/empty inputs; tests prove behavior without updating actual inputs. | fixtures, review |
| AC3 | Evaluate and, when proportionate, remove consumer-info initialization/query writes while preserving mutation coordination and explicit consumer operations; explain measured costs and deferred alternatives. | fixtures, review |
| AC4 | Relevant format/lint/provider checks and independent review support local scope-pure commits, with evaluation/build/native/deployment evidence separated. Master, input locks and remote refs remain unchanged. | fixtures, evaluation, review |
