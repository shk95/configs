# Live conditional-merge qualification report
kind: report
spec: docs/work/repository/conditional-merge-live-qualification/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Successor PR #543 completed the normal dev request with exact pre-dispatch CI and artifact evidence, protected merge, and successful writer audit. The earlier PR #538 audit failure remains recorded below and is not treated as success. |
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

The documentation PR carrying the 2026-10-07 continuation in the spec was
designated successor normal candidate P2; its later successful trial is
recorded below. The controlled target race, integration update, and meaningful
conditional master request have not been performed. The fixture coverage for
source changes, conflicts, failed/cancelled checks, the deadline,
compare-and-swap, ambiguous updates, and recovery remains local evidence,
separate from affected-dispatch and protected-merge evidence. The writer flag
is currently zero; the maintainer owns any later scoped enablement and
dispatch.

## Successor normal trial: PR #543

Successor candidate [PR #543](https://github.com/shk95/configs/pull/543) was
admitted at its unchanged approved source head
`4765cf2d401934f3aca6d03a40141971b9acc573` and tested base
`bb24d2017cbdfdfdced54921a49b50f62433b682`. Required checks run
[37567180800](https://github.com/shk95/configs/actions/runs/37567180800)
passed, and `ci-source` artifact `11459410776` matched that exact
base/head/tree tuple before dispatch.

Conditional workflow run
[37567304296](https://github.com/shk95/configs/actions/runs/37567304296)
used the accepted workflow revision at the pinned base and completed with
writer output `state: merged`, `audit: passed`. The protected merge was
`b8e927317a08acb9a451ed3770047302305bd09b` at 2026-10-07T03:34:04Z; its
parents were the tested base followed by the approved source head, and its
tree was `39295d7bd60e315528ddfc3cca1b18e3a3d2d9ac`. The maintainer verified
`CONFIGS_MERGE_ENABLED=0` after the trial. This satisfies AC1; it does not
erase or replace the separate failed audit record for PR #538.

The next candidates R and B are separate useful documentation PRs created
from this resulting `dev` base. The maintainer will capture R's frozen head
and prechecks in the remote PR after review; this report intentionally does
not contain R's own final head SHA. AC2–AC4 remain pending.
