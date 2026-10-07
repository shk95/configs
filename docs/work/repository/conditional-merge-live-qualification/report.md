# Live conditional-merge qualification report
kind: report
spec: docs/work/repository/conditional-merge-live-qualification/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | PR #538 had exact pre-dispatch CI, but both conditional-run attempts ended in a post-merge identity audit failure. It does not qualify as a successful request. See the first-trial record below. |
| AC2 | pending | No controlled stale-base refusal or H→I(C) request has been performed. |
| AC3 | pending | Bootstrap promotion #540 registered the workflow; the meaningful conditional `dev`-to-`master` trial has not been performed. |
| AC4 | pending | The first trial's failure is recorded separately from passing push CI and manual audits below. The writer flag was reset to zero after each attempt; complete scoped qualification remains pending. |

## First live trial: PR #538

PR [#538](https://github.com/shk95/configs/pull/538) was the first normal
`dev` candidate. Its approved source head was
`bfd583644f7ebb4f187151b3898184ca6d3f2f60`, and its tested base was
`8b7e7ff5d1cff5d344c4991dc30f88b856f09dee`. Pre-dispatch [Required checks
run 37563166623](https://github.com/shk95/configs/actions/runs/37563166623)
passed; `ci-source` artifact `11458195227` matched the exact base, head and
tree `46a8aabb0450515b04f796d50a621a3d01864123`. This run preceded App
dispatch and is not evidence that the App triggered this CI.

The protected merge did occur. Its merge commit was
`dd85933af227addc77c360c8746aab9dc219048d`, with actual parents
`8b7e7ff5d1cff5d344c4991dc30f88b856f09dee` and
`bfd583644f7ebb4f187151b3898184ca6d3f2f60`, and the same tested tree. The
merge was performed by `configs-conditional-merge-shk95[bot]` at
2026-10-07T02:43:50Z.

Conditional request [37563316321](https://github.com/shk95/configs/actions/runs/37563316321)
ended as `merged-with-audit-failure` in attempt 1 and again in attempt 2.
Attempt 2 inspected the already-merged PR; no second merge occurred. Both
attempts failed because the implementation expected REST `merge_commit_sha`,
which API version `2026-03-10` removed from pull-request responses ([GitHub
REST API changelog](https://github.com/github/rest-api-description/blob/main/descriptions/api.github.com/CHANGELOG.md)).
This was an API-version compatibility defect, not a delayed REST response. The
maintainer reset `CONFIGS_MERGE_ENABLED=0` after each attempt. These outcomes
are failures for AC1, not successful audit evidence.

Separate evidence: ordinary [post-merge push CI
37563373575](https://github.com/shk95/configs/actions/runs/37563373575) ran
under the App identity and passed. Manual local history and remote protection
audits later passed with zero warnings and failures. Those audits were not
performed by the conditional writer and do not erase its failed post-merge
audit. Read-only GraphQL inspection then confirmed merge OID
`dd85933af227addc77c360c8746aab9dc219048d`.

## Repair and continuation

The URL-construction repair in [PR
#541](https://github.com/shk95/configs/pull/541) is included in the tested
base. The GraphQL merge-identity and master-recovery CI repair in [PR
#542](https://github.com/shk95/configs/pull/542) merged as
`bb24d2017cbdfdfdced54921a49b50f62433b682`. Read-only verification confirmed
that GraphQL returned the exact merge OIDs for PR #538 and bootstrap PR #540,
while REST API version `2026-03-10` omitted the legacy field. This confirms
the repair's data source, not a new conditional writer trial.

After #542, the maintainer also verified the scoped App installation token's
read permissions and live repository/branch-protection checks, then revoked
the token. These were manual read-only credential and policy checks, not an
Actions writer run or a successful post-merge writer audit. The writer flag
remains zero.

The documentation PR carrying the 2026-10-07 continuation in the spec is the
successor normal candidate P2. AC1–AC4 remain pending until new scoped live
evidence satisfies their unchanged criteria. The controlled target race,
integration update, and meaningful conditional master request have not been
performed. The fixture coverage for source changes, conflicts,
failed/cancelled checks, the deadline, compare-and-swap, ambiguous updates,
and recovery remains local evidence, separate from affected-dispatch and
protected-merge evidence. The writer flag is currently zero; the maintainer
owns any later scoped enablement and dispatch.
