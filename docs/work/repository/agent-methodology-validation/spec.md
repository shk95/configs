# Agent methodology correction and three-state comparison
kind: spec
date: 2026-11-06
scope: repository
status: approved
review-by: 2026-11-20

## Goal and boundaries

Correct the staged-check subject, inconsistent task entry guidance, incomplete
pre-commit verification routes and ambiguous capability summary identified in
the maintainer-requested analysis. Use this correction as one reproducible
development-methodology case. The maintainer selected a separate linked
workspace; source remains uncommitted. No integration, push, release, input
refresh, native deployment or workspace removal is authorized.

Keep configuration and domain-owned check semantics unchanged. Repository
governance owns hook orchestration, capability presentation and shared procedure.
Historical work evidence remains intact; this task has its own acceptance.

## Comparison protocol

Freeze the source states before implementing the correction:

- A, before the existing optimization:
  `e824c6f328edb9f9a73a66b5c00ae6523aefc23c`.
- B, the analyzed current source:
  `53a3f7e09aa1e217567941c884e87f1af56de270`.
- C, this linked workspace's corrected files, identified by a content digest
  of the measured source paths because no source commit is authorized.

Use one final regression runner against disposable A/B exports and C. Fix the
case inputs and expected behavior across states. Exercise partial staging in
both directions, staged checker changes, untracked/deleted files, linked and
alternate-index context, unchanged original data and capability reporting.
Record failures as failures in A/B, rather than changing their expectations.
Native parsers may be fixture doubles: that evidence tests orchestration and
does not certify actual Nix or Windows behavior.

Repeat the same bounded runner three times per state, reporting correctness
and elapsed time separately. Include fixture setup cost and report sample
count/environment. Timing is illustrative local overhead, not an agent-speed
benchmark. Reconstruct document routes from the relevant source sections with
the same task starts/finishes; do not count entire old documents against
selected new sections. Actual session events and reconstructed historical
routes are different evidence. No historical agent time, token saving or
independent reviewer result is inferred.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Fix the three source identities and run the same reproducible cases against all three, preserving the primary checkout and distinguishing retrospective routes from executed evidence. | fixtures, review |
| AC2 | Selected staged domain checks read an isolated index snapshot, preserve partial work and alternate-index contents, and retain local/required-native evidence semantics. | fixtures, policy checks |
| AC3 | Capability output states the limits of local candidate verification, and entry/development guidance consistently distinguishes new work, continuation, dirty source and committed candidates. | fixtures, review |
| AC4 | Record the correction's observed costs, three-state correctness/timing results, document routes, scope and evidence limits; final repository fixtures and applicable policy checks pass without a commit or publication. | fixtures, policy checks, review |

Amended 2026-11-06: after AC1-AC4 were verified at the uncommitted source
checkpoint, the maintainer authorized local source commit, exact-base/head
no-ff integration into master and preservation-reviewed removal of this task's
linked workspace and merged topic. AC4's original source-preparation evidence
remains unchanged. Push, release, input refresh and deployment remain outside
this follow-on authorization.
