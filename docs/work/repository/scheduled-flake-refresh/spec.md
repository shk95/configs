# Refresh the provider flake daily before promotion
kind: spec
date: 2026-09-26
scope: repository
status: approved
review-by: 2026-10-10

## Bounded source pickup, 2026-09-30

Amended 2026-09-30: AC1-AC5 and their required lanes remain unchanged. This
pickup makes the next pure source outcome concrete, without treating synthetic
requests as scheduler integration or operating proof. It supersedes the older
unassigned root/B planning-continuation wording. D owns this planning delivery;
root assigns source continuation only after reviewing the plan and the repaired
shared-controller delivery has merged. Parent acceptance remains zero of five.

Planning inspection base is origin/dev
`54b2b794e5a0aa867f264d1bff548eebe5cc4892`, containing refresh-tool PR #455.
Source pickup pins fresh dev and the reviewed plan separately; this planning
base is not a future execution pin. The refresh entry derives its provider root,
requires functional Python >=3.9 and Nix with the verified update/reference/output
lock options, and has only `--check` as a read-only inventory option. Its output
is selection JSON followed by a textual status; it supplies neither a publication
transport nor an authenticated refresh receipt. A publisher must independently
validate exact source/head/lock identities rather than trust that status text.

PR #456's reviewed controller baseline is preview-only: supplied synthetic trust
and endpoint observations, eight fixed executing manifest paths, PR operation
meaning dev-to-master promotion, and one supplied outstanding-batch envelope.
It does not deliver feature-to-dev refresh publication, arbitrary provider-source
provenance, long-lived multi-batch history/config/package transitions, real HTTP,
credentials or a schedule. Its pending review repairs and later merged revision
must be inspected before source pickup; this plan grants no use of its old head
as completed implementation evidence.

### Next coherent source outcome

Use the additive child `docs/work/repository/refresh-candidate/spec.md` and its
pending report for one repository-owned fixture delivery: actual trusted refresh
CLI -> disposable lock candidate -> isolated local dependency commit/branch/head
-> shared-control refresh request or refusal. The child does not complete any
parent row. It reuses the existing controller and bounded single-envelope model;
it does not create a second controller, recorder, database or generic framework.

Extend schemas/functions within the existing main/records/engine/adapter files
and their exact manifest closure where possible. Review semantic protocol
compatibility explicitly; eight fixed paths do not prevent new functions or
request schemas. Keep the existing promotion PR operation unchanged and add
separate bounded refresh-branch/refresh-PR meanings. Execute old outstanding
packages with their exact retained source/protocol, never current rules; unsupported
protocols or required automatic history/config migration refuse. No long-lived
operating storage transport or multi-batch selection is supplied by the child.

The actual CLI runs only in a credential-free disposable workspace with local
fixture upstreams. Trusted source identities and literal lock bytes pass as data
to the preview side. A privileged retained-control/publisher path must not execute
arbitrary provider/candidate code. Fixture Git may create isolated dependency
commits and branches only locally; all external branch/PR operations are fake
requests/observations. No actual provider lock update, remote push, private
connection, protected-branch commit, activation or schedule is permitted.

Source dependencies are the merged refresh tool and **repaired, merged** shared
controller plus root-reviewed child plan and recorded source owner. Required
proof joins actual disposable CLI/Git integration with fake request lifecycle:
no-op/failure/timeout without publication; exact source/base/lock/commit/head;
open/merged/stale PR and unrelated human changes; non-forced reconciliation;
stop/resume, bounded transient outcomes and 05/06/07 late/missed opportunities.
The cutoff never cancels refresh. Before-promotion integration changes the next
validated candidate; after-promotion integration belongs to the next opportunity.
Simulated outcomes are not real Required checks, actor authentication, unattended
admission, endpoint receipt, notification delivery or workflow dispatch proof.

Long-lived history/retained-config/package selection and authenticated operating
transport remain shared-controller prerequisites for later real scheduler wiring.
R-manual supplies actual source provenance, connection/PAT/Environment/protection,
request/notification receipts and manual-cycle proof. Separately authorized
R-scheduled enablement follows those prerequisites. No live schedule or credential
provisioning is authorized here, and pure-child success cannot close AC1-AC5.

Source ownership, runtime/native evidence and stop/replan boundaries are in the
child. Root reviews the concrete planning diff before any planning publication;
source pickup additionally waits for the repaired controller merge and assignment.

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

## Pickup clarification, 2026-09-30

This clarification preserves AC1-AC5 and the latest 05/06/07 KST/shared-controller
amendments. The implementation owner is unassigned; the B continuation owns plan
delivery only. Read the provider-release-contract implementation pickup table for
the shared preview/control/manual/scheduled dependencies before implementation.
The older root-agent wording below is historical, not an implementation claim.

Pure scheduler/PR-lifecycle fixtures may be prepared from explicit fake refresh and
controller interfaces. Final scheduler implementation/integration waits for the
merged Unix-like refresh tool, its actual post-U1 input ownership and the delivered
shared trusted-control interfaces; no mocked proof certifies that final wiring.
Record fresh origin/dev and reviewed plan revisions, inspect competing issue/PR
ownership, and create a dedicated repository worktree after Git authorization.
Generated lock-only PRs remain Unix-like-owned; no second controller is introduced.

Required evidence covers no-op/failure without publication, open/merged/stale PR
handling, refusal of unrelated human changes, no force updates, exact-head checks,
candidate movement before/after promotion, cutoff without refresh cancellation and
late/missed opportunities. Verify credential-free refresh versus trusted lock-data
publication, shared stop/resume/record recovery and affected workflow dispatch.
Local fixtures and policy checks precede authorized manual observation; scheduled
enablement is separately authorized after actual connection/permission/notification
proof. Do not complete a report row from planning preflight or mock-only live claims.
Stop/replan for changed tool/controller interfaces or acceptance, broader remote
authority, provider/host lock scope expansion, ownership conflict or gate bypass.

## Earlier pickup lane (read with the clarification above)

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
