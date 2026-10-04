# Restore exact production inventory coverage and prove actual tracked closure
kind: spec
date: 2026-10-04
scope: repository
status: approved
review-by: 2026-10-18

## Assignment and prerequisites

Root owns this bounded source increment under #479/manual-source-continuation.
Wait for observed-release-candidate and release-refresh-object-compatibility planning
delivery to merge into dev before pickup. Pin live origin/dev and the reviewed plan
revision independently. Create the spec/report pair in the task linked worktree and
publish the reviewed plan before implementation. Do not edit shared transport source.

## Outcome

Review each current tracked candidate path independently of release-preview.rules.
Add missing exact production maps to the existing repository policy/native checks;
new child work documents are explicit maps too. No prefix or unknown-path fallback,
new check/tool identity or weakened qualification is introduced. Historical-only
paths keep their existing treatment. A future unreviewed path still refuses.

Add regression coverage to test-production-release.py that builds disposable Git
candidate inventory from actual git ls-files -z, rather than deriving its files from
the rules under test. Stage the child spec/report before inventory collection so
those paths participate. Use existing production preview/classifier/bootstrap-proposal
for coverage proof. The data are synthetic and cannot certify bootstrap or operating
provenance. Positive actual inventory coverage must pass; removing a known tracked
path's exact map must fail with mapping-review-needed. Keep unknown/unmapped tests.

Recompute only the current eight-file semantic package manifest from exact source
bytes in sorted path order. Do not modify original retained packages, protocol,
loader inventory or batch control/manifest assertions. Existing retained full-bundle
and old-gate fixtures must pass. A new control commit/manifest needs separate
source-bound operating adoption; source delivery performs none.

## Verification and boundaries

Run production qualification fixtures, retained controller compatibility fixtures,
normal repository policy and exact-head native Windows affected dispatch. Record all
criteria and evidence with source delivery. Root owns serialized integration and
subsequent compatibility design. Replan for uncovered ownership, unsupported original
schema, new check identities, domains/authority or any need to reinterpret history.
No baseline selection, private packet, initializer, master promotion, release,
workflow enablement, operating dispatch, schedule, activation, Apply or cleanup.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Every actual current tracked candidate path, including this child plan/report, has reviewed exact production coverage with its existing correct ownership and obligations; unknown future paths still refuse. | fixtures, policy checks, review |
| AC2 | Independent actual tracked inventory exercises the original production preview; positive closure passes and removed exact mapping/unknown path negatives refuse without fallback or synthetic operating certification. | fixtures, policy checks, review |
| AC3 | The new current semantic manifest binds exact eight-file bytes while original retained package/protocol/history and old-gate compatibility remain unchanged. | fixtures, policy checks, review |
| AC4 | Normal local/source and exact-head native Windows delivery pass; source inventory proof and actual new-package adoption/operating gates are reported separately. | fixtures, policy checks, affected dispatch, review |
