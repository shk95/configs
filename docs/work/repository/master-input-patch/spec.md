# Master-based Unix-like input patch releases
kind: spec
date: 2026-10-06
scope: repository
status: approved
review-by: 2026-10-20

## Implementation

One repository lane owns workflow reduction, the bounded patch controller,
master admission policy, audit/CI enforcement and operator documentation.
Pick up current origin/dev in a linked worktree; the reviewed plan is this
provisional working-tree revision until its planning commit is published.
Deliver one repository PR against dev. Normal dev-to-master promotion rolls
out policy before any direct input patch is admitted. No host adoption or
Windows release operation belongs to this lane.

Scheduled and manual operation share one master-based path. Only the four
permitted Unix-like inputs and the next patch declaration may change. A
same-repository single-commit patch PR enters protected master directly;
CI binds its exact base/head/tree. General development remains on dev and
its independently operated promotion must include accepted patch history.
No candidate execution receives writer credentials. Existing tags stay
immutable; interrupted patch publication finishes before a new refresh.
Stale master candidates stop rather than merge over a new base.

Stop/replan on a broader input boundary, host consumer changes, tag mutation,
protection bypass or a required cross-domain source edit.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Both entry points refresh only current master permitted inputs and publish its next Unix-like patch without dev integration, development promotion or Windows publication. | fixtures, affected dispatch |
| AC2 | Master admission and audits accept only ordinary dev promotion or a validated single-commit input patch; subsequent dev promotion preserves accepted patch history. | fixtures, policy checks |
| AC3 | Exact CI source binding, credential separation, stale/failing/expired candidate stops, unchanged no-op and immutable interrupted publication recovery remain enforced. | fixtures, affected dispatch |
| AC4 | Branch strategy, operator procedures and current scope document patch-only automation and independent development and consumer responsibilities. | review |
