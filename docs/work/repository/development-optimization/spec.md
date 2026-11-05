# Incremental development environment optimization
kind: spec
date: 2026-11-05
scope: repository
status: approved
review-by: 2026-11-19

## Goal and boundaries

Reduce implicit decisions, unnecessary work and context in the existing
development environment. Start from master e824c6f328edb9f9a73a66b5c00ae6523aefc23c,
not from an obligation to retain the exploratory implementation. The earlier
exploration is retained in stash 0218953aea146aeca96d35c79e551683a44025e5 and
an independently verified external archive. It supplies candidates, not policy.

Use the selected current checkout and local same-scope topics/commits. Do not
push, publish, integrate into master, refresh inputs or deploy. Preserve user
authorization, domain ownership, existing work and truthful evidence lanes.
Domain-owned increments, if justified, use separate master-based topics.

## Method and stopping rule

Compare the same six tasks: repository prose, Unix-like source, Windows source,
continuation, exact verification and release/history inspection. Compare only
the relevant old sections with the relevant new sections. Track required
reading, operator decisions/commands, independently maintained implementations,
and code/document line deltas separately; static paths are not reader benchmarks.

Each loop identifies a concrete cost and predicts its reduction, implements one
coherent concern, then receives independent review, correction and rereview.
Start with inconsistent guidance/duplicated decisions; increase intervention to
work paths and responsibility only when a remaining cost warrants it. Record
loops in the paired report, not a new framework or report for every step.
Keep improvements which preserve required behavior and reduce a named cost
without disproportionate new dependencies. Stop when the selected paths are
coherent and remaining proposals lack a demonstrated net benefit. Higher
strengths are considered, not compulsory. Broader engines, provisioning and
remote/native adoption are outside this outcome.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Preserve the exploration and master baseline; record fair before/after routes for the six tasks and identify changes to existing source, not just reductions from the exploration. | review |
| AC2 | Selected low-strength improvements remove actual duplicated decisions or misleading instructions while preserving ownership, authorization and recovery boundaries. | fixtures, policy checks, review |
| AC3 | Evaluate deeper path/context changes in bounded loops, implement justified improvements, and explain retained/deferred alternatives using concrete costs. Independent findings are corrected and rereviewed. | fixtures, review |
| AC4 | Final relevant checks pass with unavailable evidence stated separately; local commits/topics remain scope-pure, master stays at its baseline and no remote publication or deployment occurs. | fixtures, policy checks, review |

Amended 2026-11-05: AC2 and AC3 include evaluating retirement of the specialized
brew/cask/mas editor. The current provider has no app inventory and consumers
own app selection. Retiring success even for modified synthetic inventories is
an intentional interface reduction, not behavior-equivalent extraction.
Retained command names must refuse clearly before Git/host effects; common
commit admission, hook and recovery evidence must remain on the flake path.
