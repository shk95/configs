# One-call manual domain release
kind: spec
date: 2026-10-06
scope: repository
status: approved
review-by: 2026-10-20

## Implementation

The maintainer requests a simple Actions entry point that refreshes permitted
inputs and proceeds through protected integration, promotion and domain
publication with one manual/API call. This extends the current bounded release
flow; #515 still separately tracks actual schedule observation.

One repository lane, owned by this implementation session, delivers one PR.
Inputs are current origin/dev and origin/master, the accepted release tooling,
source-owned domain declarations and current GitHub checks/approvals. No other
implementation lane or host adoption is a dependency.

Add one dispatch-only workflow. Refresh executes without writer credentials.
Accepted master tooling publishes the managed refresh PR, waits a bounded time
for checks, integrates it and prepares the exact promotion candidate. A separate
Environment approval job handles exceptional candidates without holding writer
concurrency; the final writer rechecks the same candidate and publishes tags.
Use current PRs/checks/tags and job outputs, not a persistent cycle record,
labels, comments, external service or operating repository. Scheduled behavior
retains its real clock and one-promotion-per-day limit. Manual operation bypasses
only those scheduling choices, never source/check/approval or tag guards.

No-op input refreshes do not invent changes. Failed checks, stale candidates,
conflicting publication and bounded wait expiry fail visibly with remote work
preserved for rerun or ordinary recovery. A source repair, workflow rollout,
promotion and live release require their normal authorization boundaries;
this local implementation does not imply host activation or Windows Apply.

Replan if durable operating state, a new service, protection bypass or a
configuration-domain source change becomes necessary. Local source work is in
a dedicated linked worktree. Remote publication/admission is a separate step.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | One web/API dispatch refreshes only the four permitted inputs and proceeds through CI, protected dev integration, promotion and changed-domain publication without another dispatch. | fixtures, affected dispatch |
| AC2 | Manual operation bypasses only clock/day scheduling; source/check identity, review separation, accepted writer tooling and immutable tags remain enforced. | fixtures, review |
| AC3 | Waiting is bounded; failed checks and stale candidates stop; unchanged inputs and interrupted publication recover without invented changes or persistent cycle state. | fixtures |
| AC4 | Usage explains the one-call path and keeps manual release qualification separate from actual schedule and host adoption evidence. | review |
