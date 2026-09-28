# Refresh the provider flake daily before promotion
kind: spec
date: 2026-09-26
scope: repository
status: approved
review-by: 2026-10-10

## Current controller alignment

Amended 2026-09-28 (cross-work reconciliation): AC1/AC4/AC5 use the latest
provider-release-contract controller design. This supersedes the older App-token
paragraph and stage-2/3 design deferral below. Use one dedicated fine-grained PAT,
including Actions write for identity-scoped automatic cancellation; no GitHub App,
token minting or separate refresh controller. The dedicated master-only Environment,
single record writer, manual exact-candidate exception approval, Actions failure/
action-only notifications and credential-free 5/15/30 wait jobs are shared mechanisms.
No Issues-write permission or separate notification service is required.

Current times are 05:00 refresh, 06:00 promotion, 07:00 waiting cutoff, Asia/Seoul.
The cutoff does not cancel refresh. Later input integration before promotion changes
the current candidate, renewing required evidence/approval. Automatic cancellation
is only for the identified stuck controller owner and requires actual termination
before takeover. The older 08/09/10 times are history, not an alternate schedule.

The Unix-like tool must be delivered before final scheduler integration. Implement
the shared trusted controller prerequisites before enabling this workflow; select
compatible source/dispatch PR ordering with no gate bypass. Run candidate input
refresh without the PAT and publish only validated expected lock-data changes from
trusted control, never execute candidate code in the publisher. The updater still
does not merge or arm auto-merge. No-op creates no commit/PR; compatible patch
admission remains the designated integrator's action. No schedule or credential
provisioning is authorized by this plan. Actual entry/ref/permissions/receipt and
live manual-cycle evidence remain pending before separately authorized enablement.

The following earlier amendments remain provenance and are superseded where they
conflict with this section and the latest provider-release-contract amendments.

Amended 2026-09-28 (later schedule correction): the daily cycle now uses
05:00 Asia/Seoul refresh (20:00 UTC on the preceding day), 06:00 promotion and
fixed 07:00 cutoff. This supersedes earlier clock times. Follow the provider
release spec's later operating agreement for takeover, candidate identity,
recovery, delayed/missed runs and failure fixtures. Missed-run alerts are detected
upon returning execution; no separate watchdog is required.

Amended 2026-09-27: AC1-AC5 retain their original acceptance text, but pickup
is deferred until stages 2 and 3 of
`docs/work/repository/provider-release-contract/study.md` are completed.
This earlier draft is research input, not permission to implement. Exact cron
minute, token mechanism and PR lifecycle details below must be revalidated
against the adopted promotion/release design. Stage 3 must amend this spec if
that design changes any criterion. The Unix-like tool dependency still applies.

Amended 2026-09-28: AC1, AC4 and AC5 follow the accepted daily cycle in
docs/work/repository/provider-release-contract/spec.md. Replace twice-daily
refresh with one 08:00 Asia/Seoul opportunity (23:00 UTC on the preceding day)
and retain manual execution. Exact scheduler encoding and late/missed-trigger
behavior need implementation design. Discover the workflow on master and refresh
current dev after initial workflow promotion/enablement. The daily operation
precedes the 09:00 promotion opportunity, with refresh waiting capped at 10:00.
Failure, no-op or approval waiting does not hold ready dev; ongoing work is not
cancelled by the cutoff. Delayed integration follows candidate-refresh rules.

Call the Unix-like tool from the dependent spec rather than duplicating input
selection in YAML. Scope is this provider flake, not private host consumers.
Deliver changed locks through a dedicated dev-targeted update PR with isolated
chore(unixlike-deps) commits. Reuse an open automation PR, preserve published
history without force pushes, and refuse unrelated human-authored content.
Update the branch from dev only for a required integration update. No diff
means no commit or new PR. Failed refreshes publish no candidate; failed CI
never authorizes bypass or merge. The updater does not arm auto-merge.

Historical credential proposal (superseded by Current controller alignment):
use a narrowly scoped GitHub App installation token for publication and PR
creation so ordinary PR CI can run. Document secret names without storing
credentials. Missing credentials fail clearly. Creating/installing an App and
provisioning secrets require explicit maintainer account authorization.
Missing remote setup remains pending deployment evidence.

Amended 2026-09-28: AC5 includes the provider-release-contract AC13 operating
boundary. Execution stays in public configs, with private operating configuration
and batch records accessed only by trusted control jobs. The automation is
explicitly enabled: disabled/unconfigured use is a quiet no-op, while enabled
but misconfigured use stops and requests action. Honor emergency stop and explicit
resume, pin configuration per batch, and reconcile the daily refresh with the
single-writer cycle. Exact repository connection and permission provisioning
remain pending; no private repository creation is authorized here.

## Pickup lane

Outcome: scheduled workflow, PR lifecycle handling, fixtures and operator
documentation. Scope: repository. Inputs: current origin/dev, reviewed spec,
branch protection and current GitHub Actions documentation. Dependency:
docs/work/unixlike/automatic-flake-refresh/spec.md must be implemented and
merged before pickup. PR boundary: one repository automation PR. Generated
lock-only PRs are Unix-like changes. Verification: workflow checks and fixtures
for no-op, failure, existing/merged PRs, human branch contamination and targets.
Continuation owner: the root agent after explicit Git authorization.

A designated integrator, separate from updater/worker delivery, may admit a
compatible patch refresh automatically after required checks and exact-head
validation. Major/data-migration/uncertain refreshes wait for approval/resolution;
other classifications retain ordinary reviewed admission. Do not arm worker
auto-merge. Promotion/publication belong to the coordinated cycle, not the
refresh tool. Stop/replan for broader unattended authority, host deployment,
other repositories or protection bypass. This plan does not provision an App,
merge, tag, activate, Apply or enable a live schedule. Local fixtures do not
prove live execution. Approval/notification channels and credential separation
must be settled with the promotion implementation before pickup.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Workflow offers one daily 05:00 Asia/Seoul refresh and manual execution, discovering on master and refreshing dev before the coordinated promotion opportunity, with explicit delayed/missed-run handling. | affected dispatch, review |
| AC2 | Changed locks create or update one dev-targeted PR with isolated dependency commits; no-op and failure publish no candidate. | fixtures, policy checks |
| AC3 | Automation history and unrelated branch content are preserved without force pushes, rebases or protected-branch commits. | fixtures, policy checks |
| AC4 | Refresh PRs use Required checks; a designated integrator admits only compatible patch refreshes unattended after exact-head validation, other changes follow approval/review rules, and updater/worker delivery never arms auto-merge, promotes, releases or deploys. | affected dispatch, review |
| AC5 | Permissions, private operating-state connection, explicit enablement/stop/resume, approval/action-only notification mechanisms and 06:00 promotion with 07:00 refresh-wait cutoff are documented consistently with the coordinated cycle; disabled use is quiet, enabled misconfiguration refuses writes, and live evidence remains separate from local validation. | review |
