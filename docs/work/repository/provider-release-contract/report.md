# Report: provider release contract
kind: report
spec: docs/work/repository/provider-release-contract/spec.md
status: pending

## Planning delivery clarification, 2026-09-30

Reviewed the latest controller/selection/template amendments and preserved the
uncommitted independent-review study summary. Added concrete R-preview/control/
manual/scheduled pickup boundaries, dependencies and proof obligations without
changing acceptance or assigning controller implementation. Initial inspection
established no prior Git publication authorization; the maintainer subsequently
approved publication of this five-file planning diff on the existing B branch.
That approval covers dev-targeted PR delivery, not implementation or integration.
Work-item preflight verifies
document form only; all implementation and live acceptance rows remain pending.
The dated live Git/ownership observations are in the study's current handoff.

## Cross-work reconciliation, 2026-09-28

Parent-only review compared all five current specs/reports with the later accepted
decisions. Corrected scheduler App/stale-time/design-deferral navigation, added
latest-reading summaries for both domains, and made candidate-pair testing versus
provider integration versus pre-release template delivery explicit. The dependency
map now keeps refresh tooling independent, final input wiring aligned with U1 and
scheduling dependent on shared trusted control. Controller operational failure is
not candidate validation evidence. Outstanding implementation proof includes trusted
old-batch recovery, validation wakeup/serialization, timeout/permissions/races and
actual notification receipt. No new sub-agent review, implementation, native run,
remote mutation or acceptance completion is claimed by this reconciliation.

## Controller operating design and read-only observations, 2026-09-28

Latest agreement adds Actions write for identity-scoped automatic cancel, confirmed
termination before takeover, master entry with pinned per-batch control, one serialized
record writer, non-forced operating Git updates, and head-guarded promotion with
post-merge verification before tags. It accepts the lack of an atomic expected-base
guard: unexpected merges stop publication and are not automatically reverted.

Read-only gh repo view returned defaultBranchRef=master. The master protection API
returned Required checks (app_id 15368), strict=false, enforce_admins=true,
allow_force_pushes=false, allow_deletions=false, required_approving_review_count=0
and dismiss_stale_reviews=true. This was not a complete ruleset/permissions audit;
no remote setting or branch was changed.

Actions failure-only notifications and credential-free bounded retry wait jobs were
accepted. Actual receipt, deduplication limits, timeout values, workflow/ref/secret
protection and remote-write races remain implementation/live verification work.
All acceptance rows remain pending. No PAT/environment provisioning, dispatch,
approval/cancel/merge/tag call or notification was performed.

## Controller credential and approval planning, 2026-09-28

The maintainer selected one dedicated fine-grained PAT, a controller-only protected
Environment and manual exact-candidate exception approval workflow. The latest spec
records minimum proposed permissions and their limits, including manual renewal,
common permissions across selected repositories and unresolved cancel/write details.
GitHub documentation was consulted; no token, App, Environment, workflow, repository
protection or approval record was created/changed. All implementation and live
verification criteria remain pending.

## Single-flake template planning, 2026-09-28

The latest amendment records coordinated single-flake dendritic host/template
delivery, shared input transition by default and independently selected host
operations. This is accepted planning, not template delivery or private adoption
evidence. No external repository, workflow, branch or release was changed.

## Post-audit selection refinement, 2026-09-28

The maintainer accepted explicit changed-function check mapping and bounded scope,
replacing environment-driven repetition and automatic whole-domain unknown-impact
fallback. Unknown selection requires review and blocks promotion until resolved.
The latest spec amendment preserves exact-candidate evidence and failure gates.
This is planning only: no selector, workflow, remote configuration or release was
changed; all acceptance rows remain pending.

Stage-1 design was agreed in the maintainer conversation and recorded on
2026-09-27. This report measures implementation, not agreement on direction.
No policy, submodule, workflow, branch protection or release was changed.
Research and the continuation entry are in the adjacent study.md.

On 2026-09-27 the maintainer selected full supported-platform builds before
master promotion. AC5 records that agreed design; its enforcement and dispatch
evidence remain pending. This is not evidence that any platform build ran.

The maintainer selected hosted-first full verification with separate Windows
client evidence on 2026-09-27. AC6 remains pending until complete coverage,
capacity measurements and affected dispatch are implemented and verified.
Later on the same day the maintainer restricted Windows support and verification
to Windows 10. The AC6 amendment removes Windows 11 from required coverage;
it does not waive any required Windows 10 evidence or complete an acceptance row.

On 2026-09-27 the maintainer selected base configuration plus separate
profile/feature selection for host subscriptions. AC7 records the configuration
catalog and discovery contract while retaining domain versions and ownership
scopes. Machine-readable release discovery, dependency-aware impact detection
and its evidence are not implemented; AC7 remains pending. The choice does
not certify any catalog build or change AC5's required evidence.

On 2026-09-27 the maintainer confirmed the recommended supplied-artifact
comparison boundary and asked to continue. AC8 includes necessary dependencies
and consumer tools, separates public-contract changes and mutable external
environment observations, and remains pending. No artifact inventory generator,
comparison implementation or host-side discovery was run or delivered.

On 2026-09-27 the maintainer selected independent initial 1.0.0 releases and
one maintained major per domain. AC9 remains pending until semantic-series
selection, historical-tag handling and maintenance discovery are implemented
and verified. No tag was created, pushed, moved or removed.

On 2026-09-27 the maintainer accepted deterministic, adapter-independent release
classification from commit-preserved structured data and verification records.
AC10 remains pending: no parser, aggregator, CLI/CI integration or refusal
fixtures were implemented. The planning decision does not authorize publication.

## Planning realignment, 2026-09-28

The maintainer defined configs as one desired computing environment with
platform implementations and host-owned final realization/actual-use validation.
The dated spec amendment revises AC1, AC4, AC5, AC6 and AC8. Earlier machine
matrix decisions below are historical where superseded. Provider contract tests,
applicable build/native evidence and provider defect responsibility remain;
the revised coverage map is not yet designed or implemented. Stage 1 is reopened
for contract/ownership review before stages 2 and 3 are finalized. Companion
domain amendments, central stateVersion and template integration review remain
pending. No acceptance row is verified by this agreement or document editing.

## Daily-cycle agreement, 2026-09-28

The maintainer accepted daily 08:00 KST provider refresh, 09:00 promotion with
at most one hour of refresh waiting, automatic compatible patch-refresh dev
admission by a designated integrator, and gated patch/minor promotion/publication.
Major/data-migration batches need exact-candidate approval. Failed or unmerged
approval-waiting refreshes do not block existing dev. Candidate changes require
fresh evidence/approval; publication recovery retains source/versions, preserves
successful domain releases and blocks the next promotion. Domain versions remain
Unix-like/Windows only and aggregate cumulative effective impact once per batch.
AC11 records this accepted design; all implementation evidence remains pending.
No workflow, credential, merge, tag or live schedule was created or enabled.

## Execution and recovery agreement, 2026-09-28

Subsequent discussion adopted role/credential separation, promotion-PR review,
structured recovery records, action-only deduplicated notifications, fresh checks
on changed candidates, approval for controller-rule changes, exact-record tag
idempotence, three transient retries after 5/15/30-minute delays and phased
preview/manual/scheduled rollout. Immutable annotated tags remain the initial
release authority and carry the agreed minimum release metadata. AC12 captures
these requirements. Storage selection, exact permissions and merge-result binding
are unresolved; no implementation, notification or remote write was performed.

## Private operating context agreement, 2026-09-28

The maintainer selected public configs control execution with separate private
operating configuration/records, replacing the public orphan-branch and private
controller alternatives. AC13 records pinned configuration, accumulated history,
reconstructible index, single-writer checks, stop/resume/revocation, unavailable
storage behavior, explicit enablement and a concise private README. Separate
backup infrastructure was explicitly excluded. The private repository is not yet
named, created or configured; this session documents requirements here, not a
README in a nonexistent/unselected repository. No App, secret, protection change,
remote notification or live operation was performed. All rows remain pending.

## Later operating agreement, 2026-09-28

The later amendment adopts 05:00 refresh, 06:00 promotion and 07:00 cutoff
(Asia/Seoul), termination-confirmed takeover, intent/result reconciliation,
exact candidate/approval binding, merge-result checks and delayed/missed-run
handling. Failure fixtures remain required, including alert deduplication and
both permitted and refused progress. No separate watchdog is required. All
implementation and live evidence remains pending; no row is verified here.

## Latest design consolidation, 2026-09-28

The latest dated spec consolidation records environment/host ownership and
domain API/template contracts. All implementation and live evidence remains
pending, including the new API criterion. Document preflight is form validation,
not evaluation, build, native runtime, activation/Apply or live automation proof.
No source implementation, Git publication or host mutation was performed.

## Selective evidence refinement, 2026-09-28

The later verification amendment records bounded release guarantees, affected-
contract selection, required/advisory checks, failure classes and same-candidate
source promotion. These are accepted planning requirements, not passing runtime
evidence. Remote read at this refinement found dev e11bd136 and master 2542d77c,
with no open PRs; branch protection was not re-audited and no worker was assigned.

## Independent review follow-up, 2026-09-28

Accepted independent-review corrections are now recorded in the owning specs.
They clarify cutoff/candidate timing, complete-delta check selection, template
delivery, initial reader bootstrap and host-local applied-state capture. All
implementation evidence remains pending; this update is design acceptance only.

## Final independent planning audit, 2026-09-28

An independent agent reviewed all five work items against latest accepted
amendments and confirmed the previous five corrections without identifying a
new direction conflict. This is planning review only. Concrete consumer paths,
U1 types/transitions/evidence and later lane prerequisites remain; all acceptance
rows stay pending and no implementation or live rollout is certified.

## Acceptance

On 2026-09-27 the maintainer clarified that machine-based distribution is only
one option. The dated AC1/AC7 amendment prioritizes recurring master promotion
and host-pinnable release checkpoints, reopening mandatory machine subscriptions.
Earlier machine schemas/matrices are candidate designs, not implemented or
accepted delivery requirements. AC1 and AC7 remain pending; no scheduler,
promotion controller or release publisher was implemented or authorized.

Later on 2026-09-27 the maintainer accepted mandatory representative machine
configurations across all supported platforms, excluding exhaustive feature
combinations and arbitrary private-host behavior from the guarantee. The dated
AC5/AC6 amendment replaces the earlier exhaustive interpretation. Required
platforms and failing mandatory checks cannot be omitted; separate Windows 10
client evidence remains required. Exact reference cases, bounded feature checks,
capacity and enforcement remain unimplemented. AC5 and AC6 remain pending;
this planning acceptance is not build, native runtime or deployment evidence.

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC14 | pending | |
| AC2 | pending | |
| AC3 | pending | |
| AC4 | pending | |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | |
| AC10 | pending | |
| AC11 | pending | |
| AC12 | pending | |
| AC13 | pending | |
