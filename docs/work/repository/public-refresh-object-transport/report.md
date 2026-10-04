# Report: public immutable refresh object transport
kind: report
spec: docs/work/repository/public-refresh-object-transport/spec.md
status: pending

Root prepared this child at dev 32f4e75a87f8d56b39668bcda7ed500ab7fad5c4 after
candidate and compatibility/custody planning integration. Source pickup waits for
the semantic and typed transport prerequisites; root retains continuation ownership.
Independent read-only API review identified recursive-query semantics and masked 404
as concrete observation hazards. No transport source, permission or API effect
was changed. Planning verification is not source or operating acceptance.

Primary API contracts: [blobs](https://docs.github.com/en/rest/git/blobs),
[trees](https://docs.github.com/en/rest/git/trees),
[commits](https://docs.github.com/en/rest/git/commits), and
[masked 404](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api#404-not-found-for-an-existing-resource).

Independent review identified a concrete additional pickup requirement: current
protocol adoption must include produced records and loader/package selection, not
only entry guards. The spec now requires a complete protocol 4 projection-to-replay
round trip and mixed-3/4 refusal while original protocol 3 histories remain intact.
This is planned source verification, not an observed production initialization.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | Source prerequisites and fixed request boundary planned; not implemented. |
| AC2 | pending | Exact object and absence/recovery contract planned; fixtures and source remain pending. |
| AC3 | pending | Durable adoption/current closure/local/native delivery and actual operating proof remain separate. |

## Independent source inventory review, 2026-10-04

Read-only review compared reviewed plan f5e32cd with actual dev 32f4e75 and semantic
source 12a40cad without importing or executing unmerged transport source. The dated
clarification identifies dedicated anonymous direct readers, exact original4
observation targets and full serialization adoption. Insufficient original dependency
custody finitely refuses; signed gitlink metadata is never invented. This records
pickup design only. All acceptance remains pending prerequisite integration and
actual source/local/native delivery.


## Original private publication delivery review, 2026-10-04

Root and a read-only reviewer confirmed a continuation gap in the retained
Journal: API-created private child objects are not delivered to the owned local
original database before later head/context/graph reads. Existing fake API and
Snapshot share one object store and mask this difference. This is source inspection,
not an actual private API failure or operating receipt.

The dated spec amendment includes deterministic prospective raw-object retention,
complete remote identity comparison, bounded local import/original replay before
logical acceptance, and pending/fence preservation after local failure. Distinct
REMOTE/LOCAL two-publication and start-continuation fixtures are required at source
pickup. No source correction or native fixture for this gap is delivered by this
planning amendment; all ACs remain pending. It introduces no retry/rollback authority.
