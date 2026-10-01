# Provider release contract and staged planning
kind: spec
date: 2026-09-27
scope: repository
status: approved
review-by: 2026-10-11
issue: #451

## Sequential continuation planning, 2026-10-01

The maintainer selected sequential non-deferred continuation. See the dated
release-control-history compatibility amendment, followed by
legacy-capture-caller-retirement, production-release-qualification and
release-operating-transport child specs/reports. These children close planning
gaps; they do not certify actual production bootstrap, authenticated source or
manual/scheduled operation. Root records explicit source pickup assignments only
after predecessor integration and reviewed plan publication. Operating repository,
approved source, credentials/Environment/protection and actual receipts remain
separate inputs and authorization gates. Deferred host work is not selected.

## Global-history follow-up planning, 2026-09-30

Additive `docs/work/repository/release-control-history/spec.md` and its pending
report bound global outstanding-batch selection and exact old config/package
semantic replay. Root reviewed and approved this planning delivery on 2026-09-30; it assigns
neither source nor live operation. D's actual refresh-candidate package/protocol delivery and root's dated
compatibility review precede B source pickup. Preserve original event bytes and
exact old package semantics; unsupported offsets or missing bindings refuse.
The completed single-envelope child does not complete global history storage or
the operational loop. All fourteen parent criteria remain pending, with manual
and scheduled obligations separately open. No parent acceptance text changes.

## Current reading order after reconciliation

Reconciled 2026-09-28 after the later simplifications: read "Cross-work pickup and
evidence reconciliation" and the latest controller/selection/template amendments
before earlier stage proposals. Historical full-build matrices, gitlinks, per-host
flakes, App credentials, whole-domain unknown-impact fallback and stronger atomic
merge claims are superseded. Latest same-date amendments take precedence. This
is accepted planning, not implementation or permission to execute remote actions.

## R-control concrete pickup, 2026-09-30

Amended 2026-09-30: AC1/AC5/AC6/AC10/AC11/AC12/AC13/AC14 retain their
acceptance text and required lanes. This engineering pickup clarifies their
controller portions; it does not adopt unattended policy, production semantic
releases or a permission bypass. The integrator reviewed this concrete pickup
for planning delivery. Execution issue #451 names B as continuation owner for this
planning delivery. Controller implementation receives a later explicit assignment.

The additive offline R-preview was delivered in #429; its completed report is
`docs/work/repository/release-preview/report.md`. It validates pinned structured
replay and refuses incomplete mappings; it authenticates no live evidence. Parent
acceptance remains zero of fourteen verified. Read this pickup before the earlier
2026-09-30 clarification and historical proposals below. Pure fake-adapter fixtures
can proceed independently of Darwin capture, the provider refresh tool, private
hosts or PAT provisioning. Actual affected-domain eligibility and required template
pair evidence remain prerequisites of an affected live release.

### One outcome and implementation boundary

R-control delivers one disabled-by-default repository controller with bounded
request/record handling, retained approved control and explicit fake adapters.
Its prospective owning files are repository controller tools, narrow fixtures,
the master entry workflow and its policy/dispatch wiring; each file's author must
be assigned before implementation. Current assignment changes only this work
item, and compatible scheduler dependency clarification if needed. It does not
edit README/CONTRIBUTING/architecture, domain code or sibling plans. The operator
entry will be `tool/configs release-control`; automation calls its implementation.
The mode is explicit `preview` until separately authorized R-manual operation.
No fixture invokes a real write endpoint, credential, dispatch, cancel, merge or
ref mutation. Existing accepted calendar tag tools remain authoritative.

| Choice | Concrete initial design | Refusal/proof obligation |
| --- | --- | --- |
| Trusted entry | One master-only controller workflow with schedule, manual request and completed-validation wakeup; Environment only on trusted entry jobs | Wrong repository/ref/event/workflow refuses before loading private data; no dev checkout or candidate artifact/cache execution |
| Old-batch control | Stable loader executes the exact previously approved public control package, rather than current-master decision rules | Verify approved-master provenance, full package manifest/digests and old approval/transition semantics; unknown compatibility refuses |
| Records | Version-1 strict TSV, operating config, append-only events and reconstructed current index in one private Git branch | Fixed grammar and exact parent commit; non-forced update conflict reloads; never execute record text |
| Serialization | A constant job-level writer concurrency group, cancel-in-progress=false, plus exact remote owner/run/attempt/generation checks | Actions pending work is not a durable FIFO; generations cannot fence external APIs; no duplicate writer |
| Wakeup/approval | Completed trusted check identities wake reconciliation; one manual approval mode sends an exact request to the same entry | API-verified actor/run/ref/attempt and exact candidate tuple; request or dispatch acknowledgement is not approval or ownership |
| Recovery | Intent precedes each external write; actual remote observation follows; ambiguous results stop | Compare remote commit/PR/tag identity/content before retry, retaining fixed completed releases |

### Trusted loader and retained bundle

The future master workflow has a small loader with literal public repository,
package-root and supported protocol constants. An operating record supplies only
a validated full commit identity and its expected manifest; it cannot choose a
repository, URL, executable path, shell fragment or arbitrary checkout target.
Digest equality proves identity, not approval. At batch creation, authenticate the
current approved master control commit, its promotion/review provenance and any
required control-change approval. Store that approved master SHA, package-manifest
blob identity, package file digests and supported loader/adapter/record protocol.
The first control installation's approved source is an R-manual bootstrap input.
No arbitrary ancestor becomes trusted merely because it is reachable from master.

An outstanding batch always selects that recorded approved commit, configuration
and exact package. Verify its recorded approved-master provenance and continued
reachability without replacement objects; read package files only from that public
commit and constant package root. The manifest enumerates all executing engine,
classification/approval, transition, remote-adapter and serializer dependencies.
Do not combine an old script with new rules, new approval checks or new adapters.
Use an isolated scratch directory and explicit tools, never candidate artifacts or
caches. A new master loader may resume an old compatible package; an unsupported
retained protocol or altered package stops for manual recovery rather than silently
migrating records or weakening old obligations. No generic plugin loader is needed.

Old control governs candidate selection/approval and operation meaning, including
required old-batch evidence and publication recovery. The small current entry
only supplies the fixed invocation/secret boundary and compatible scheduling
interface. A changed current entry incapable of preserving that interface refuses
old-batch execution. Fixture review must cover two different approved master
revisions where the newer rules would waive a gate: recovery still applies the
older gate/approval semantics. Initial approval provenance, old-master ancestry,
manifest tampering and incomplete dependency pinning require negative cases.
Master ref restriction alone does not prove secret isolation; actual workflow,
Environment and credential access are a separate R-manual observation.

### Record grammar, identities and compatibility

Use one operating branch, initially called `operations` in the connection contract;
its actual repository and authorized branch are R-manual inputs. Its fixed layout
is `config/operating.tsv`, `control/stop.tsv`, `history/NNNNNNNNNNNN.tsv` and
`current/index.tsv`. There is no database, external lock or second notification
store. Operator config/stop updates also advance this branch without force; a
controller reloads them rather than overwriting the changed head. Only the
controller appends batch events and changes its index.

Every file starts with the two-field row `format<TAB>1`. Original bytes must be
valid UTF-8, end in LF and contain no NUL/CR or other controls except separators.
No blank/comment rows, unknown keys/kinds, duplicate singleton keys, duplicate
IDs or incorrect field counts are accepted. Values are printable one-line data;
tab/newline has no escaping alternative and is refused. Backslash/quote/Unicode
are literal narrative characters, JSON-escaped only on output, never shell/AWK
source. Git IDs are full 40-hex object identities for this GitHub SHA-1 lane;
digests/batch/request/operation IDs are 64 lower-hex. Decimal IDs/counters have
no leading zero; booleans are exactly 0/1; timestamps are fixed UTC seconds.
The 12-digit zero-padded event filename is the sole counter-format exception;
its event-sequence value is the equivalent canonical unpadded decimal.
Missing required records, unsafe paths, unsupported object/format versions or an
unexplained history/index mismatch refuse. This is a bounded record reader, not
a new general format framework.

Singletons use `key<TAB>value`. Fixed repeated tuples below have the shown arity;
all other fields are singleton keys. Lists are sorted unique identifier lists
with `-` for empty, never expressions. Canonical field ordering and byte encoding
make duplicate operation payloads comparable. Event sequence is a 12-digit decimal
filename with no gaps; exhaustion refuses rather than wrapping. An event includes
its prior-event digest. Index is the deterministic projection of those events,
including the owning generation and outstanding batch; mismatches require
explicit reconstruction/inspection before any external mutation.

| Record | Required content |
| --- | --- |
| Operating config | schema, enabled flag, literal connection IDs/ref, public controller/validation workflow IDs, authorized numeric actor IDs, reviewed coverage/check definitions and permitted operation scopes; no credentials or code locator |
| Live stop | schema, stop flag, monotonically increasing stop revision, reason and operator identity; reread from current remote head rather than pinned config |
| Batch start | batch ID, initial trigger/day/run identity and time, config commit/blob digest, approved controller/master/manifest/provenance identities, rules/selector and loader protocol; preserve these across recovery |
| Owner | public repository ID, workflow ID/path, run ID, attempt, writer job identity, increasing generation, stage and exact observed operating head; no generation-only claim of API fencing |
| Candidate | increasing candidate generation, dev SHA, master base SHA, expected merge tree, preview engine/rules/baseline digests, selected check IDs and complete evidence identities; replaces pre-promotion candidate only |
| Evidence tuple | `evidence<TAB>check<TAB>dev<TAB>master<TAB>tree<TAB>rules<TAB>tool<TAB>state<TAB>run<TAB>attempt<TAB>job<TAB>reference`; real check provenance is authenticated by the adapter, not by offline preview |
| Approval | actor ID, authenticated manual source run/attempt/ref, exact candidate generation/dev/master/tree, classification/versions/migrations and evidence digest; no PR prose authority |
| Publication tuple | `release<TAB>domain<TAB>version<TAB>source<TAB>previous-tag-object<TAB>annotation-blob<TAB>tag-object<TAB>intent-id`; fixed annotation/tagger time and initial run identity, not a retry's current time |
| Operation tuple | `operation<TAB>id<TAB>kind<TAB>payload-digest<TAB>owner-generation<TAB>request-state<TAB>remote-object<TAB>observation`; absent identity uses `-`, state is intent/observed/unknown/conflict |
| Event/index | event sequence/kind/request/batch/prior digest, owner and state transition; append-only full operation/observation payload and deterministic outstanding index |

The initial reducer supports batch-start, claim, candidate, evidence, approval,
intent, observation, retry-wait, blocker, stop-observed, resume and complete events.
Every kind has one fixed legal transition and field set; reject impossible stage,
wrong owner or repeated operation ID with different bytes. Approval/evidence are
invalidated when the candidate or bound classification changes. After promotion,
freeze source, versions, tag names, annotation bytes/tagger time, previous releases
and publication operation IDs. A partial publication retries only the unchanged
missing operation, even if dev, config or master subsequently advance.

Configuration edits govern later batches; retained records/config are never
rewritten by an implicit version upgrade. Live stop/revocation remain exceptions.
Malformed history, unavailable storage, missing old package or unverified approval
blocks new writes. A manual recovery can inspect and reconstruct the index from
history; it cannot infer missing approval/evidence from tags or rewrite completed
release objects. Changing a protocol or approval meaning returns to planning.

### Requests, wakeup and bounded execution

Manual mode is one of preview, start, approve, resume or stop; ordinary patch/minor
eligibility does not require approval mode. The one manual approval workflow is
this shared entry's approve path, not an independent private-record writer. Bind
an approval request to the exact displayed candidate digest, then validate actual
Actions actor/triggering actor IDs and source event metadata against the pinned
allowlist. Caller-supplied actor strings are never identity. A rerun is a new
attempt and must revalidate request and actor; approvals do not merge.

Schedule and `workflow_run: completed` are signals to read actual outstanding
state. Match source repository ID, literal workflow ID/path, expected event,
ref/head SHA, run ID and attempt through fresh API reads. Completion or a supplied
success flag alone is not evidence. A candidate check artifact is never executed
or trusted as the authority of a result. Select authenticated check-run/job/tool
provenance for the exact candidate/master/tree/rules tuple before producing the
existing R-preview evidence TSV. Unsupported coverage/bootstrap refuses; synthetic
fixtures cannot manufacture production coverage or real tool provenance.

Read/cancel inspection runs outside the job-level writer concurrency group, so
an owner stuck inside that group cannot block inspection of its own termination.
Only the trusted record-writer job uses the same constant group across every
entry/mode. It rereads remote state after acquiring the group and processes
requests in that critical section. Repeated signals join outstanding work rather
than create another batch. Actions can replace pending jobs and does not promise
FIFO; a canceled pending manual approval is not approved and has no private
consumption receipt. Do not assume the run API reconstructs dispatch inputs.
The operator must resend the same complete exact request; missing request data
refuses rather than reconstructing approval from run prose or a guessed input. Scheduled
or validation signals merely cause state reconciliation on the next surviving
entry; delayed/missed opportunities follow the existing 05/06/07 agreement.

| Bound | Initial value and meaning |
| --- | --- |
| Privileged controller job | 15 minutes; small record/remote operations only, never builds or sleeps with the PAT |
| Individual API call | 30-second response deadline; a timed-out write has unknown outcome, not permission to retry |
| Cancel observation | Poll exact run/attempt/jobs every 30 seconds for at most 5 minutes; expiry is unknown termination and refuses takeover |
| Credential-free waits | Accepted 5/15/30-minute delays, wait-job deadlines 6/16/31 minutes in the same workflow |
| Candidate checks | Run without the PAT/private configuration; retain each domain's existing declared timeout and evidence boundary |

A known validation/retry wait is a legitimate stage, not an expired writer. A
writer timeout begins inspection/cancel only; it cannot grant ownership. Before
cancel match the recorded repository/workflow/run/attempt and reread latest attempt.
The cancel endpoint accepts run ID, not an atomic expected-attempt condition;
attempt races cannot be atomically prevented by that API. Reread immediately
before and after the call; a detected change or unknown result refuses takeover.
Serializing operator rerun mutations with controller cancellation is a separate
R-manual operating prerequisite, not a proven atomic API fence. A 202
response is only acceptance. Confirm exact attempt and all its writer jobs are
terminal, re-read current records and reconcile outstanding operations before
claiming the increasing generation. Unknown status/attempt or missing job pages
blocks takeover. Never cancel input refresh at the cutoff or unrelated CI.

Before every external mutation reread owner/generation, remote operating head,
live stop and actual target. Persist its exact intent first. Stop may race an
already accepted request; observe the actual effect, record it and perform no
further mutation. A stop/config commit author field alone does not authenticate
an operator or grant write authority. Clearing stop does not resume; an explicit
authenticated resume
reconciles remote effects and renews any changed-candidate evidence/approval.
A generation change is checked locally and in operating history but is not an
atomic fence on GitHub's merge/tag API. Do not claim zero race windows.

### Concrete endpoint adapter and permission contract

The adapter initially pins API version `2026-03-10`, explicit method/path/body
schemas and supported response forms. Verify the account's actual responses
before R-manual operation. Unknown fields needed for identity or incompatible
statuses refuse; do not silently treat legacy acknowledgements as current proof.
No write endpoint or live controller operation is called by this planning
delivery. Actual read-only protection inspection is recorded in the report;
fake-adapter fixtures call no live endpoint.

| Operation | Endpoint and documented fine-grained permission | Identity/reconciliation rule |
| --- | --- | --- |
| Load operating/source objects | GET Git refs/commits/trees/blobs; Contents read | Fixed repository/ref, full object and exact parent/tree/file identities, no redirects to an unconfigured host |
| Save operating event/index | POST Git blobs/trees/commits; PATCH Git refs with force=false; Contents write | Commit has exactly the observed head parent; read ref/history after a lost response; matching operation+bytes is applied, conflicting advancement reloads |
| Inspect/create promotion PR | GET/POST pulls and GET reviews; Pull requests read/write | Same-repository dev to master, one promotion PR, exact head/base, resolved conversations/required protection; no topic PR source |
| Admit promotion | PUT pulls/{number}/merge with merge_method=merge and sha=expected-dev; Contents write | Read actual merged SHA/parents/tree after response or loss; unexpected result blocks tags, never auto-undo |
| Validate required evidence | GET commits/{ref}/check-runs and statuses plus Actions runs/attempts/jobs; Checks read, Commit statuses read, Actions read | Exact run/workflow/attempt/job/source/tools and trusted definitions; missing/failed/unverified required checks refuse |
| Wake one manual entry | POST actions/workflows/{id}/dispatches, ref=master; Actions write | Current documented version returns 200 with run ID/URLs; acknowledgement does not prove execution, ownership or approval |
| Cancel owner | POST actions/runs/{id}/cancel then GET exact attempt/jobs; Actions write/read | 202 is not termination; mismatched run/attempt and unknown outcome refuse takeover |
| Inspect full protections | GET branches/{branch}/protection; Administration read | Exact required contexts/app and protections; denied/missing/mismatched state stops, never updates settings |
| Publish domain annotation | POST Git tags, then POST Git refs for its tag; Contents write | Fixed annotated object/name/source/bytes; successful immutable tags retained, existing conflict refuses |

Permission claims are scoped to those endpoint contracts, not proof that a token
was issued or a real protected operation succeeds. The template repository is
selected only if its separate authorized update is included; configs-hosts is
never selected. No Issues write, Administration write, workflow editing, App,
renewal service or speculative capability is introduced. Source/ref writes that
would need an additional permission must stop and demonstrate the specific need,
not expand the token or bypass protection automatically.

Root endpoint review selects Administration read for authenticated full protection
GET: the documented endpoint demonstrates the missing read permission rather than
a speculative capability. Check exact Required context/app, administrator and
conversation enforcement, no force/deletion, dev strict=true and master strict=false
before protected operations. This permission applies across all repositories
selected by the one PAT, including private operating/template scope when included;
it is not per-repository isolation. Actual PAT issuance, selected-repository scope,
permission-denial tests and Environment/protection observations are still unapproved
R-manual inputs. No Administration write, protection-update endpoint or bypass is
included, and this document issues no credential.

Primary references, reviewed 2026-09-30: [Git references](https://docs.github.com/en/rest/git/refs),
[Git commits](https://docs.github.com/en/rest/git/commits),
[annotated tags](https://docs.github.com/en/rest/git/tags),
[pull requests](https://docs.github.com/en/rest/pulls/pulls),
[check runs](https://docs.github.com/en/rest/checks/runs),
[commit statuses](https://docs.github.com/en/rest/commits/statuses),
[workflow dispatch](https://docs.github.com/en/rest/actions/workflows),
[run/attempt/cancel](https://docs.github.com/en/rest/actions/workflow-runs),
[concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency),
[workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows),
[Environment ref restrictions](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments),
[protection reads](https://docs.github.com/en/rest/branches/branch-protection).
The retained-loader protocol, job-group selection, reducer and timeout values are
engineering choices inferred from these APIs and accepted constraints; the docs
do not prove this repository's secret isolation, fencing or rollout.

### Unknown response reconciliation and proof families

An operating write first prepares immutable objects with fixed parent/bytes.
Only reachability through the accepted operating branch makes state saved. On a
lost PATCH response, read actual branch history: the same operation ID and expected
commit/event content means applied even if newer valid events now follow it;
absence with unchanged original parent means not applied; conflicting content or
unreadable/incomplete history means conflict/unknown. Reload/reduce remote advancement
before any new action; never force or blindly resubmit an old-parent snapshot.

For a lost PR creation response, find the sole matching source/target PR and
validate its head/base/body-operation identity; duplicates/conflicts stop. For a
lost merge response, inspect that PR and actual commit parents/tree. For a lost
annotation/ref response, inspect the exact immutable tag object and ref; retain
matching success, create only a confirmed absent operation, refuse conflicting
annotation/target/version. Never substitute current timestamp/run, new version or
new source to make a retry succeed. All later effects follow the accepted
intent -> external operation -> observation gap; there is no multi-repository CAS.

| Proof family | Positive and refusal cases required before live rollout |
| --- | --- |
| Trust/retention | Approved old bundle after newer master, changed rules cannot waive old gate, correct package/approval; wrong master provenance/ref/package/dependency/schema/candidate executable refuses |
| Grammar/records | Canonical UTF-8/Unicode/literal escaping, event+index commit projection; original-byte NUL/CR/invalid UTF-8, unknown/duplicate fields, gaps/old format/index mismatch refuse |
| Requests/evidence | Duplicate schedules join, verified completion wakes, exact authorized approve/resume; forged actor/event/ref/attempt/tool, moved candidate, canceled pending approval and missing/unverified checks refuse |
| Ownership/stop | One writer and conflicting head reload, normal wait and termination-confirmed takeover; cancel 202 only, missing pages/changed attempt, timeout-only takeover and post-stop continuation refuse |
| Intent/reconciliation | Lost response before/after record commit, PR creation/merge, tag object/ref and index; matching applied histories resume, unreadable or contradictory remote states refuse |
| Immutable partial release | Preserve successful domain tag and retry only missing fixed payload; changed source/version/tagger time/run/annotation or occupied tag refuses without overwrite |
| Timing/outcomes/isolation | Quiet disabled/no-op, enabled misconfiguration, delayed/missed signals and recorded transient waits; non-transient retry, duplicated intentional action alert and unsafe public/private output refuse |

Fixtures use explicit fake API transcripts plus disposable file-only Git fixtures
under the delivered test environment isolation. Assert no external transport/ref
mutation, no candidate code execution and no secrets/private payload in summaries.
They prove the reducer/adapter contract, not live PAT permissions, notification
receipt, Windows client behavior or production coverage. Required implementation
checks are narrow fixtures, registry/work-policy and affected dispatch, with native
Git-for-Windows evidence for new governance shell behavior. Domain criteria remain
with their owners, selected honestly by changed effect.

R-manual names the actual private operating repository/resource owner/ref,
approved initial controller installation, Environment/PAT/actor allowlist, full
protection assertion choice and real endpoint/notification receipts. R-scheduled
requires that successful manual proof, refresh tool and shared-controller delivery,
and separate enablement. These unresolved operating inputs do not block pure
controller fixture preparation. Stop/replan for changed acceptance/authority,
unapproved retained semantics, missing coverage, unsafe credential exposure,
protection bypass or a request for real remote mutation in fixture mode.

## Implementation pickup clarification, 2026-09-30

This section concretizes the latest amendments without changing AC1-AC14 or
adopting new policy. The earlier R1/R2 lanes and general stage-design deferrals
are historical where superseded. Planning delivery, offline implementation,
authorized manual operation and scheduled enablement are separate outcomes.
No controller implementation owner or execution issue is assigned by this text.

At pickup, inspect the execution issue and open PRs for competing ownership;
record current origin/dev and the reviewed plan revision separately. An unpublished
planning diff is provisional and must be published before another worker relies
on it. Each lane uses its own repository-scope linked worktree and coherent PR.

| Lane | Outcome and PR boundary | Inputs and dependencies | Required proof and acceptance connection |
| --- | --- | --- | --- |
| R-preview | Adapter-free read-only release decision CLI, structured input/output contract and refusal fixtures; one repository PR | Reviewed release plan, exact master/candidate and previous domain-release identities, explicit impact/evidence inputs, trusted selector revision. Decide legacy-history cutover and metadata encoding at pickup; synthetic domain inputs permit independent fixture work, while final domain wiring uses delivered contracts. No PAT/private setup prerequisite. | AC2/AC7/AC8/AC9/AC10 applicable portions: deterministic version or refusal; cumulative changes/reverts; source-only/no-op; malformed/missing/contradictory declarations; unknown selection; required versus advisory evidence; no external writes. Policy and affected-dispatch checks plus positive/negative fixtures. |
| R-control | Disabled-by-default shared controller, request/record handling and previewed remote-operation adapters; one repository PR | R-preview interfaces, agreed master-entry/old-batch recovery mechanism, request wakeup/serialization, approved concrete record schema and endpoint/permission design. Required template delivery gates use exact consumer-facing refs; unrelated Windows/U1 implementation does not block pure controller fixtures. | AC1/AC5/AC6/AC11/AC12/AC13/AC14 applicable portions: candidate/approval invalidation, trusted secret isolation, single-writer conflicts, termination-confirmed takeover, stop races, remote intent/result gaps, immutable partial-tag recovery, retries, delayed/missed runs and safe summaries. Fixtures are required before live operation. |
| R-manual | Authorized manual end-to-end rollout and its evidence; repair source in its owning PR when needed | Delivered controller and affected domain contracts/evidence; durable required template adaptation with delivered-pair proof; selected private operating repository, actual PAT/Environment/ref boundary, operator authorization for each live scope | Observe actual permission/protection behavior, retained old-batch semantics, validation wakeup, exact merge parents/tree, remote record reconciliation and Actions notification receipt. Fixtures and document checks cannot satisfy this live proof. |
| R-scheduled | Separately authorized enablement of the existing shared cycle | Successful R-manual evidence, explicit enable/stop/resume configuration and scheduled rollout authorization; refresh scheduler also depends on the delivered Unix-like refresh tool | AC11/AC12/AC13 and scheduled-flake-refresh criteria: observe 05/06/07 KST opportunity handling, quiet disabled/no-op use, enabled misconfiguration refusal and recovery. No new controller, private-host gate or automatic host adoption. |

These are coherent delivery boundaries, not a branch per test environment. An
implementation report records actual lane evidence in its delivery PR; partial
proof does not verify a criterion that still requires other lanes. All current
acceptance rows remain pending. The planner assigns an owner and records the
lane in an execution issue only after the applicable pickup decisions and Git
authorization are concrete; this planning clarification grants neither.

Before assigning R-preview, settle the committed impact encoding and initial
legacy-history boundary, input/output schema, initial changed-function mapping,
and operator entry point. The complete replay input must include source and
previous-release identities, versioned rules/selector, declarations, tool versions
and exact evidence binding. Keep current-master-to-candidate promotion selection
distinct from previous-domain-tag-to-candidate version aggregation. Unmapped
changes require bounded mapping review or refusal, never an empty successful
selection. Final actual contract paths/ref formats must follow their domain owner;
fixtures must not silently become a second domain schema or evaluator.

Before assigning remote-write implementation, name the concrete trusted master
entry and how recovery retains old approved control/approval semantics, the wakeup
after candidate checks, request serialization and timeout values. Prove stop/cancel
races, exact owning run/attempt matching, termination confirmation and unknown
remote-response reconciliation. Confirm the actual endpoints and protections;
plan-level PAT permissions or Environment names are not proof of isolation. The
head guard cannot guarantee an atomic expected-base merge: unexpected actual
parents/tree stop publication without automatic undo. Actual notification receipt
and duplication limits remain manual-rollout observations.

Stop and return to planning for changed acceptance/dependencies, competing owner,
private-host validation becoming a provider gate, a new release product, candidate
code in privileged control, broader unattended authority or a protection bypass.
Unresolved encoding/selection/trust interfaces block the affected pickup; they do
not authorize a worker to silently invent new accepted governance. No credentials,
live schedules, merges, tags, activation or Apply follow from plan publication.

## Outcome and standing

Record the agreed stage-1 design for frequent, host-consumable provider
releases. Stage 2 designs master promotion and release gates. Stage 3 designs
the daily input refresh before promotion. This spec is an implementation target, not a
replacement for current policy or authorization to publish or deploy.
Stage-1 direction is agreed; implementation acceptance remains pending.

Domain contracts are owned by the companion specs:

- `docs/work/unixlike/provider-consumer-contract/spec.md`
- `docs/work/windows/host-consumer-contract/spec.md`

Start a continuation at `docs/work/repository/provider-release-contract/study.md`.
It records the decisions, research boundaries, current-policy gaps and prompts
for new stage-2 and stage-3 planning sessions. No chat transcript or temporary
research directory is needed to understand the handoff.

## Release meaning

Master should be usable by hosts through the documented consumption contract.
Frequent provider releases must not wait for every private host to deploy.
Source promotion, domain release and host activation/Apply remain distinct.
Retain same-repository dev -> master PRs with merge commits unless stage 2
explicitly proposes and the maintainer accepts a governance change.

Keep Unix-like, Windows and common independently versioned; repository
governance receives no domain tag. Use domain-prefixed semantic versions for
the new release series. Preserve existing immutable calendar tags. Compatible
routine flake refreshes are patch candidates, compatible public additions are
minor, and supported-contract breaks require major classification and migration
information. A lock-only diff is not automatically compatible. Failed checks
cannot be bypassed by assigning a major version.

Initial version and maintenance scope are selected below. Minimum tools,
annotation format and promotion/release cadence remain stage-2 deliverables.
Current annotated-tag-only policy remains effective until explicitly revised.

## Stage-2 decision: initial stable versions and maintenance

Agreed 2026-09-27: start the first implemented and verified stable consumer
contracts independently at unixlike-v1.0.0 and windows-v1.0.0. Either domain
may release first; neither waits for the other's release date. This adds AC9
without changing AC1-AC8 and does not create or authorize a tag now.

Maintain one active major series per domain initially. When a new major is
released, preserve all old immutable tags, but provide no promised fixes or
backports for the previous major. Discovery must distinguish a newer major
and old-series maintenance status from an update within the active series.
Existing host pins remain unchanged until separately adopted. Preserved tags
do not guarantee indefinite availability of external downloads or compatibility
with future host environments.

Preserve existing calendar tags as historical releases outside the new SemVer
series. Do not compare them numerically with 1.x or rewrite their annotations.
Windows ProjectVersion and schema/state-format versions remain distinct from
the domain tag; define their mapping and migration explicitly in implementation.
No preview series, extra maintenance branch or multiple-major backport service
is introduced by this decision. Version classification is selected below;
exact declaration encoding and automatic publication mechanics remain design
work.

## Stage-2 decision: deterministic release classification

Agreed 2026-09-27: release classification and condition evaluation must work
through ordinary repository tools in CLI/CI without an agent, model or adapter
making runtime decisions. Read structured release-impact data preserved in
commit history, actual changes and explicit verification inputs. PR review is
an authoring process, not a requirement to recover mutable PR descriptions or
labels as the classification authority. This adds AC10; AC1-AC9 are unchanged.

Record domain, impact (none/patch/minor/major), affected configurations or
selections, compatibility rationale and migration information where needed.
The exact encoding (for example commit trailers or same-domain committed
records) remains implementation design. Bind declarations to the reviewed
source revision and preserve ownership boundaries. Conventional Commit titles
alone are not sufficient compatibility declarations.

Starting from each domain's previous release, inspect cumulative effective
changes to the candidate and aggregate the strongest required impact, once
per resulting release. Reconcile reverts explicitly. Compare declared scope
with source paths, configuration dependencies, artifacts/contracts and required
evidence. Missing, malformed or contradictory data and failed requirements
produce a deterministic refusal, not an agent-supplied guess or default patch.
A major declaration cannot turn a failed supported case into a passing release.
Source-only promotion remains possible without a consumer release delta.

The same complete input set (history, baseline/target, structured declarations,
versioned rules and verification records) must produce the same next version
or refusal. Return machine-readable results/reasons as well as operator output.
An adapter may prepare inputs or invoke the tool; it must not supply a hidden
step needed to reproduce the decision. The declarations state compatibility
intent; automated checks enforce testable conditions and do not claim to infer
all semantic compatibility from arbitrary code or prose.

Positive and negative fixtures must cover adapter-free operation, aggregation,
malformed/missing declarations, scope/impact mismatches, failed evidence and
revert handling. Define the initial legacy-history transition separately so
old immutable history need not be rewritten to acquire new metadata. Automatic
dependency-refresh classification rules remain stage-3 work. This decision
does not authorize unattended merges, tag publication or host mutation.

## Stage-2 decision: full builds before promotion

The original decision below is retained for history. The later dated
representative-configuration amendment governs the current AC5/AC6 boundary.

Agreed 2026-09-27: before dev enters master, every changed domain must complete
the full build or native generation matrix for its declared supported platforms.
Evaluation or representative builds alone do not satisfy this boundary, and
missing required build evidence cannot be deferred until tagging. For Windows,
this means its native generation/validation contract, not a Nix build.
Unchanged unrelated domains do not become prerequisites. Domain tags add version,
compatibility and release records; activation and Apply remain separate.

This decision adds AC5 without changing AC1-AC4. The precise support/tool matrix,
builders, candidate-evidence mechanism and remaining stage-2 recommendations
still need design and review before execution. It does not authorize a merge,
tag, runner provisioning or host deployment, or adopt the entire study proposal.

## Stage-2 decision: hosted-first verification

Agreed 2026-09-27: prefer GitHub-hosted native runners for complete provider
build/generation verification. Collect Windows 10 client-specific
behavior evidence separately; hosted Server results do not certify client-only
behavior. The domain specs name initial exact CI versions: upstream Nix 2.34.8
and PowerShell 7.6.6, retaining Windows PowerShell 5.1 bootstrap coverage.

This adds AC6. Exact runner labels, full-build capacity/time measurements,
WinGet selection and client inventory remain verification/design tasks. Missing
capacity returns to builder design without weakening AC5 or implicitly enrolling
a private host as a runner. This is a planning decision, not workflow, runner,
credential, branch-protection or host-mutation authorization.

Amended 2026-09-27: AC6 follows the maintainer's replacement Windows support
decision: only Windows 10 client evidence is required. Windows 11 is outside
the supported matrix, rather than a missing mandatory lane. This supersedes
the earlier same-day Windows 10/11 wording; hosted-first verification and the
full coverage obligation for the now-supported matrix remain unchanged.

## Stage-2 amendment: all platforms with representative configurations

Amended 2026-09-27: AC5 and AC6 replace exhaustive configuration-combination
coverage with mandatory representative configurations for each published
machine across all its declared supported platforms. The maintainer selected
"all platforms, representative configurations required". This supersedes the
earlier rejection of representative builds and any interpretation of complete
coverage as all optional-feature combinations. It does not permit omission of
a supported platform or substitution of evaluation for a required build/native
generation result.

For each changed domain, name the mandatory machine/platform reference cases
and their fixed synthetic inputs/selections before verification. All required
cases must pass before promotion. Do not remove a failed case or platform from
the candidate's evidence matrix merely to pass its gate. Platform support
changes remain explicit compatibility decisions. Unchanged unrelated domains
remain outside the required gate; cross-revision evidence reuse and narrower
affected-machine selection remain separate, unresolved design questions.

AC6 retains hosted native runners as the primary venue, measured capacity for
the mandatory reference matrix, and separate required Windows 10 client-specific
evidence. Windows 11 remains excluded. Exact baseline OS/tool versions in the
domain specs remain unchanged. Define bounded feature/dependency checks and
regression cases alongside the reference matrix; exhaustive combinations and
arbitrary private-host behavior are outside the release guarantee. Publish
the actual verified coverage without certifying untested combinations.

The assurance is that the declared mandatory checks passed and provider defects
are corrected through subsequent immutable releases, not that every permitted
combination is defect-free. Fixes retain the accepted compatibility/version
classification, one-active-major maintenance scope and no implied repair-time
SLA. Missing or failed mandatory evidence and invalid release metadata still
block publication. Host customization, deployment and operational recovery
remain host responsibilities; provider public-contract defects remain the
provider's responsibility.

AC1-AC4 and AC7-AC10 are unchanged. Read earlier full/complete-verification
references using this revised matrix boundary. Exact reference cases and
feature-check selection still need design; this acceptance neither implements
the gate nor authorizes a merge, release publication or host operation.

## Stage-2 decision: configuration subscriptions

The machine-based choice below is retained as design history. The later
"release checkpoints first; distribution boundary open" amendment reopens
that choice; the catalog can still identify verification cases without fixing
the unit of distribution.

Agreed 2026-09-27: identify a consumer's base configuration by stable machine
kind and architecture, with selected profiles/features in separate fields.
Keep the existing ownership scopes and one independent version series per
domain; do not introduce a Git scope or version series for every machine or
feature combination. This adds AC7; AC1-AC6 are unchanged.

The initial planned configuration catalog is:

| Configuration ID | Architecture | Consumption boundary |
| --- | --- | --- |
| unixlike/nixos-wsl | x86_64 | NixOS toplevel including managed Home Manager; optional agents profile |
| unixlike/nixos-vmware | x86_64 | NixOS toplevel including managed Home Manager |
| unixlike/nixos-utm | aarch64 | NixOS toplevel including managed Home Manager |
| unixlike/nixos-orbstack | aarch64 | NixOS toplevel including managed Home Manager |
| unixlike/nixos-desktop-amd-apu | x86_64 | Current AMD APU desktop composition's NixOS toplevel |
| unixlike/darwin | aarch64 | nix-darwin toplevel including managed Home Manager |
| unixlike/home-wsl | x86_64 | Standalone Home Manager activation package |
| windows/client | x86_64 | Selected generated configuration and required management tools/format |

These IDs describe public configurations, not private host names. Mapping to
the actual domain constructors/generators and synthetic inputs must be explicit
and tested. The catalog does not certify builds or physical runtime, expand
the domain specs' supported OS/hardware boundaries, or approve all possible
feature combinations. Support versions belong in compatibility metadata.
Windows wsl selection manages Windows-side settings; it does not subscribe
to or deploy a Unix-like WSL guest. Embedded Home Manager remains part of its
owning NixOS/nix-darwin result, not a second independently selected update.

Machine-readable release records must let a consumer identify its base
configuration and selected profiles/features within a domain release. Keep
requested selection and resolved dependency closure distinct and account for
required tools and contracts when determining impact. A change to font must
be considered for a Windows terminal consumer through the declared dependency,
even if terminal payload files did not change. A new domain version alone
must not be presented as proof that every consumer configuration changed.

Domain-owned code retains composition and dependency authority; this repository
contract defines discovery and evidence reporting, not a shared cross-domain
generator. Arbitrary host customization still requires host-local comparison;
an unlisted or unverified combination must not be treated as unchanged or
certified by a nearby standard case. Discovery does not update host pins or
authorize activation/Apply.

The comparison boundary is selected below; exact digest encoding,
record publication, variant evidence coverage under the dated AC5/AC6 amendment
and cross-commit evidence reuse remain subsequent design decisions.
This selection does not weaken AC5, authorize unattended promotion/tagging,
or make the implementation lanes ready for pickup.

## Stage-2 decision: supplied artifact comparison boundary

Agreed 2026-09-27: compare the configuration, necessary dependencies and
consumer management tools supplied by configs for the selected configuration.
Report public-contract changes separately from artifact changes. Keep mutable
external application versions as separate environment observations rather than
expanding this work into pinning and distributing every external application.
This adds AC8 without changing AC1-AC7.

For Unix-like consumers, cover the final system or standalone Home Manager
result, its runtime dependency closure and any separately consumed provider
tools. For Windows, cover selected/required-feature payloads, effective
declarations, interpreted format and consumer generation/check/application
tools. Domain implementation owns the exact mapping. Do not reuse Windows's
existing desired-state hash as this contract without addressing its different
coverage; do not change its drift semantics incidentally.

Keep artifact, public-contract, environment and provenance-only differences
distinguishable. A changed domain version or source SHA alone does not prove
that each consumer's artifact changed. If provenance is embedded in a consumed
artifact, it is a real artifact difference until an explicitly validated
separation exists. A management-tool update can be reported independently of
unchanged deployed settings. Unknown or incompatible comparisons are not equal.

Homebrew/WinGet/app-store declarations, required versions and pinned hashes
belong to provider inputs; later external application bytes remain environment
observations unless a separately adopted immutable artifact contract covers
them. Artifact equality does not prove runtime convergence or future external
installation equivalence. Compare old/new providers with the same host inputs
and non-provider choices, retaining private data locally.

Exact hashing/serialization, release-record publication and evidence-reuse
rules remain to be designed. This boundary grants no activation, Apply,
automatic host pin update, merge or tag operation and does not reduce AC5.

## Stage-2 amendment: release checkpoints first; distribution boundary open

Amended 2026-09-27: AC1 and AC7 reflect the maintainer's clarification that
machine-based distribution is one option, not the fixed architecture or the
goal. Prioritize recurring dev-to-master source promotion and release points
that external hosts can deliberately select and pin. Reopen the earlier AC7
requirement for machine-kind/architecture as the mandatory subscription unit.
Preserve the earlier discussion as candidate design, not a requirement to
implement machine files, per-selection inventories or a machine release train.

Domain source snapshots, domain release bundles, platform/profile groupings,
machine records, or a domain snapshot with optional machine indexes may be
compared as alternatives. Distribution, verification and versioning boundaries
need not coincide. Retain existing domain ownership and independent domain
version series; reopening distribution granularity does not create a shared
cross-domain composition authority or choose new per-unit versions.

Every chosen representation must expose an immutable source binding, discoverable
release identity, compatibility/verification scope and enough structured change
information for a host to make an adoption decision within the representation's
stated granularity. Exact private-host or arbitrary feature-subset equality is
not a prerequisite for creating useful release checkpoints. Coarse/unknown
impact must remain explicit; a new domain release is not proof every host output
changed. Host pins and activation/Apply remain host decisions.

The recurring process needs a defined trigger/batch boundary, candidate source,
required evidence, serialized promotion/publication and failure recovery. Exact
cadence and unattended publication authority remain open. Do not infer a release
every twelve hours from the separately planned input-refresh interval. Keep
same-repository dev -> master PR merge commits under current policy. Source-only
repository/docs promotion remains possible without a domain tag; scheduled
opportunities do not force an empty domain release or bypass failed evidence.

AC2-AC6 and AC8-AC10 retain their existing boundaries. AC5/AC6 reference cases
describe verification coverage, not a requirement to publish a separate artifact
for each case. The detailed machine-file schemas, identity algorithms and
seven-plus-one matrix in the study remain options until selected. This amendment
changes planning priorities and acceptance framing, not repository policy,
workflow implementation or authorization to merge, tag, publish or deploy.

## Stage realignment: one computing environment and host realization

Amended 2026-09-28: AC1, AC4, AC5, AC6 and AC8 follow the maintainer's
definition of configs as one desired computing environment with Windows and
Unix-like implementations. Configs provides supported configuration elements,
defaults, constraints, composition interfaces and implementations. Hosts map
these onto actual computers, own final configurations and validate actual use.
This amendment supersedes earlier machine-centered verification requirements
where they conflict; it changes a planning target, not current repository gates.

Amended 2026-09-28: AC1's environment/host distinction explicitly means
environment desired state and machine desired state; both are declarative.
Configs supplies an implemented, opinionated default environment and its
requirements. Hosts select and declare the hardware, storage, boot, display
and network configuration needed to realize it. Reusable machine recipes may
remain provider implementations with explicit host selection; they are not
universal desktop requirements merely because an existing machine uses them.
This clarification does not adopt the separate stateVersion or template
recommendations, change companion criteria or implement a configuration migration.

Amended 2026-09-28: AC1, AC5 and AC6 require personal machine realization to
be assigned to hosts in the migration plan. Reusability alone does not justify
provider ownership. A retained reusable implementation needs an explicit public
environment contract and bounded provider verification independent of private
machines. Neither migration progress nor private-machine installation/use
acceptance is a recurring provider release gate. Optional selection is not an
exemption from required provider checks; narrow the promised scope or migrate
the implementation rather than waiving failures. Plan initial consumer/API
transition evidence separately from recurring release evidence.

Reopen stage 1 before completing stage 2: name the public configuration contract,
supported composition/extension boundaries and provider/host ownership. Revisit
central stateVersion ownership and template submodule necessity in the owning
specs before pickup; this amendment does not select replacements or silently
change those companion criteria. Then derive stage-2 checks from contract
claims, and finally reconcile stage-3 refresh classification and automation.

AC5 and AC6 no longer require a reference for each private-machine-shaped
catalog entry merely because that machine exists. A reviewed evidence map must
cover public inputs/defaults, constraints, supported compositions, tools and
compatibility with synthetic positive/negative cases and necessary platform
evaluation, build/generation and native behavior tests. Exact cases, coverage,
capacity and dispatch are unresolved and must be selected before execution.
Hosted native runners remain preferred where they can prove the claim; Server
results do not prove Windows client behavior. Existing support/tool baselines
are inputs to review, not implicitly expanded, removed or universally certified.
All selected required checks must pass; a failure is not an excuse to redefine
coverage. Private-host integration, deployment and actual-use success belong
to hosts and are not provider publication prerequisites. Provider defects remain
provider obligations, including defects first discovered during host use.

AC8 distinguishes provider release impact from exact host-output comparison.
The release describes changes to supplied definitions, dependencies, tools and
public contracts at its stated granularity. A host may compare final results
under fixed host inputs locally; producing every such result or an exact
per-host equality digest is not a provider release prerequisite. Unknown impact
must remain unknown, and external environment observations remain separate.

Independent domain versions, immutable releases and the separation of promotion,
publication and adoption remain the planning baseline. A single environment
identity does not create shared composition authority or require one synchronized
version. AC2, AC3, AC7, AC9 and AC10 retain their criteria; AC3's submodule choice
is explicitly under review before pickup. Exact cadence, candidate handling and
unattended authority remain open. Daily promotion opportunities and a dev
integration pause were suggestions, not accepted decisions.

## Compatibility-baseline ownership clarification

Amended 2026-09-28: AC1, AC4 and AC8 follow the Unix-like companion's latest
AC1 amendment: configs owns evaluator compatibility baselines; hosts own their
adoption and actual-state migration. This resolves the stateVersion ownership
review mentioned above without deciding exact values or template integration.
Baseline changes require explicit impact/migration information independent of
ordinary dependency refresh. Release classification reflects supported-contract
impact, not the spelling of the stateVersion value alone. Provider release
evidence covers its declared contract and transition claims, not migration of
every private host or arbitrary host-added service. Host migration completion
is neither a recurring release gate nor inferred from provider build evidence.

## Accepted daily cycle and automation boundary

Amended 2026-09-28: AC1, AC2, AC4, AC9 and AC10 are interpreted through the
following accepted operating rules. AC11 makes their implementation and recovery
explicit. This replaces earlier open cadence, twelve-hour refresh and suggested
dev-freeze wording. It authorizes the future design, not live merges, tags,
credentials, scheduled deployment or host operations in this planning session.

Only Unix-like and Windows have release series in this initial design. NixOS,
Darwin, Home Manager and features have no separate series. Repository governance
has none; common remains an exceptional policy scope with no current release
product. Do not introduce a common release merely to share implementation.

At 08:00 Asia/Seoul daily, prepare/validate one provider input-refresh PR for dev.
At 09:00, open the promotion opportunity. If that day's refresh is still running,
wait only until 10:00; on expiry notify and start with integrated dev. A failed
refresh notifies and does not block ready dev; a no-op or approval-waiting refresh
also allows promotion to proceed. Do not cancel the refresh just because this
wait expires. If it later integrates during promotion validation, refresh the
candidate; if promotion has finished, include it in the next batch. These are
logical schedule times, not promises that a hosted job starts exactly on time;
late/missed-run mechanics remain implementation design. The 10:00 cutoff never
waives required candidate verification.

A designated integrator may automatically merge a compatible patch refresh into
dev only after required checks and admission validation. The updater prepares
the PR; it does not arm worker auto-merge. Major/data-migration/uncertain refresh
changes wait for approval or resolution. Other refresh classifications retain
ordinary reviewed dev admission; this rule grants no blanket unattended minor
refresh merge. Host locks and compatibility baselines are not refreshed.

One promotion/publication cycle runs at a time. Scheduled/manual triggers join
an existing cycle rather than create duplicates. Dev integration continues;
when dev changes during validation, update the candidate and obtain required
evidence for the new candidate. Before merge, verify current dev/master and the
tested source/result binding. Never relabel evidence from a different revision.
Resolve the final merge-result evidence mechanism before implementing automation.
Unchanged batches are no-ops; docs/governance-only source changes may promote
without a domain release. A batch with any failed required lane waits for a fix
through dev; domains are not cherry-picked into master.

Patch/minor promotion and publication may run automatically after all conditions
pass. A major change or explicit data-migration requirement holds the entire
batch for approval. Approval binds the exact candidate and reviewed change set;
a changed candidate requires renewed review/approval. Invalid/missing/uncertain
classification stops unattended action. Manual urgent runs use the same gates.
When validation or approval completes, continue without waiting for the next day.

Compare source promotion with current master and each domain's cumulative
effective change with its last release. Aggregate the strongest remaining
major/minor/patch impact once per changed domain, reconcile reverts, and refuse
contradictory declarations. Migration approval is separate from version magnitude.
A domain with no release delta receives no version. Retain the independent
initial 1.0.0 and one-active-major rules; this cycle does not create tags now.

After successful promotion, fix the source binding and selected domain versions
for publication. If publication fails, retry that same source/version operation,
not a new source promotion. Preserve successful domain releases and retry only
the failed/missing publication. Immutable records must never be overwritten;
idempotent retries verify any existing record against the expected identity.
Outstanding publication recovery blocks the next promotion. New dev changes
do not alter the recovering batch. Failures/blocked publication and approval
needs are visible to the maintainer; routine successful runs retain records.
Notification transport and approval interface remain to be designed.

No host pin update, activation, Apply or private-machine migration is included.
Current policy and annotated-tag transport remain effective until the reviewed
governance implementation adopts the unattended procedure. Account provisioning
and live enablement remain separate explicit operations.

## Accepted execution, notification and recovery contract

Amended 2026-09-28: AC4, AC7, AC10 and AC11 include the following subsequently
accepted operating rules. AC12 adds explicit proof for the control boundary,
retry/recovery and phased enablement. No live writes or enablement are authorized
by this planning record. Operational-record storage remains an unresolved design
choice; the adjacent study compares options without adopting one.

Separate refresh preparation, integration/promotion control and publication
roles; separate services are not required. Candidate validation receives no
merge/tag publishing credentials. Trusted previously approved control logic
checks exact evidence before writes. Changes to automation permissions, gate
omissions, approval rules or version-classification rules require maintainer
approval even for a patch/minor or governance-only batch. New rules govern only
later batches, never waive their own candidate's obligations. Preserve the
controller revision in evidence and recovery records.

The promotion PR presents changes, proposed domain versions, migration needs
and evidence. Required maintainer approval binds that PR's exact candidate and
reviewed change set; changed candidates invalidate it. Structured records, not
mutable PR prose alone, drive classification and recovery. Bind verification to
candidate source/tested result, master baseline, check definitions and tool
versions. New candidates rerun the required checks; build caches may be used,
but prior-revision pass/fail results are not reused. Unchanged unrelated domains
are not newly required. Publication retry of an already fixed batch does not
restart candidate validation.

Notify only on failure or required human action: failed checks/publication,
approval requests, refresh wait expiry and permissions/configuration problems.
Include cause, batch, needed action and PR/run links. Deduplicate the same cause
while blocked. Success, no change, routine candidate refresh and ordinary retry
progress produce records only, not notification comments. Resolution updates the
existing problem state without a separate success announcement. Delivery-channel
behavior and GitHub's user-configured notifications require verification; this
contract controls messages the automation deliberately emits.

Only transient communication/service failures receive automatic retries: after
the initial failure, wait 5, then 15, then 30 minutes before at most three extra
attempts. Notify once when exhausted. Permission/configuration errors, identity
conflicts and actual validation/classification failures stop for action rather
than consuming transient retries. A blocked batch survives future daily triggers;
an explicit resume uses its durable record, retaining completed steps and fixed
publication versions. A repaired pre-promotion dev candidate follows the fresh
validation/approval rule rather than reusing failed-candidate evidence.

Before publication fix source, versions and all record fields including initial
timestamp/run identity. Absent tags may be created; existing tags are accepted
only when their expected target and immutable record match. A conflict stops
and notifies; never overwrite or choose another version to escape a conflict.
After a lost response, inspect remote state before retrying. Preserve successful
domain tags and retry only incomplete publication. Recovery must work without
the original local workspace or changing a fixed record's timestamp.

The first transport remains immutable annotated domain Git tags, with no GitHub
Release, packaged asset or machine-specific release file required. Minimum tag
information: domain/version, promoted source commit, previous release, cumulative
change summary, compatibility and migration information, supported/verified scope
and evidence links, and Unix-like evaluator compatibility baselines. Distinguish
evaluation, build and native runtime; tags certify no private deployment. The tag
is the completed release authority; batch state is operational recovery data.

Introduce automation in three explicit phases: read-only decision preview;
authorized manual end-to-end execution; then separately authorized daily
enablement. Fixtures exercise candidate movement, partial publication, lost
responses, identity conflicts and recovery without inducing production failures.
Live manual evidence and schedule enablement remain distinct from fixture proof.

## Public execution and private operating records

Amended 2026-09-28: AC4, AC11 and AC12 now use a separate private operating
repository; AC13 specifies the accepted boundary. This resolves the storage
choice left open above. Supersede the public orphan-branch proposal and the
proposal to move control execution into the private repository. Public configs
owns reviewed executable control rules and Actions workflows; the private
repository stores operator configuration and runtime records only.

Public code knows the connection contract and record schema. CI settings/secrets
supply the actual private repository locator and authentication. The running
controller reads the private data; neither the public source nor public outputs
must embed its private contents. Credentials stay in CI Secrets, not the private
Git history. Personal machine configuration remains in hosts and is not an input
to this automation. Private configuration may select only values allowed by
public rules; it cannot disable required evidence, approvals or access boundaries.

The private repository starts with three parts: versioned operating configuration,
append-only batch history, and a small current-state index reconstructible from
that history. A short private README explains purpose/relationship, locations,
access roles and configuration locations without secret values, troubleshooting,
emergency stop/resume and manual recovery. Link public rules rather than copying
them. No separate database or backup system is in initial scope. Protect history
from force updates/deletion where supported; repository loss requires manual
recovery, not a promise that public tags reconstruct all unpublished plans.

Pin the operating configuration commit when a batch starts and retain the control
code revision and candidate identity beside it. Configuration edits take effect
in subsequent batches; recovery uses the original configuration. Emergency stop
and credential revocation remain live exceptions. Missing or malformed required
configuration refuses new writes. A private configuration fetch is data loading,
not authority to execute private scripts or unchecked values as shell code.

One authorized controller writes operating state at a time. Repeated schedule
or manual triggers reconcile an outstanding batch before creating another.
Combine execution serialization with checked remote updates; changed state must
be reloaded, never blindly overwritten. A superseded/stopped execution must not
continue external writes; the precise fencing protocol needs implementation and
fixtures, not an assumed guarantee from Actions concurrency alone. Interrupted
runs must be recoverable without permanent abandoned locks.

Emergency stop prevents new dev integrations, master promotions and tag writes.
Read-only verification may finish. Preserve completed changes and pending batch
records; do not revert merges or delete tags. Clearing stop does not resume work:
require an explicit resume, re-read actual state and renew evidence/approval where
the candidate changed. An operation already accepted by GitHub may still complete
after stop; inspect and record it, then prevent further writes.

If private storage is unavailable, start no new merge/publication. Reconcile any
already requested operation through actual GitHub PR/tag state; an unavailable
response is unknown, not success or failure. On reconnection reconcile records
before resuming. Completed public releases remain usable without private access.
Intent is persisted before an external mutation and the observed result afterward;
there is no cross-repository atomic transaction, so recovery must cover every
gap between those steps.

Automation is explicitly opt-in. Without enablement, missing private setup is
normal non-use with no repeated alert; ordinary development, CI and release
consumption remain independent. Enabled automation with missing connection,
credentials or required configuration stops and requests action. Public workflows
must not leak private contents through logs, outputs, artifacts or caches. A
public safe summary may report an operational failure while private details stay
private. Public run metadata itself is not promised confidential.

Use isolated unprivileged validation and trusted privileged control jobs. Exact
App/key separation, environment/ref restrictions and branch/tag protections remain
to be designed and verified against the actual account; repository/token scope
does not by itself restrict a credential to one file or one batch. Do not expose
minting keys or operational credentials to candidate code or execute its artifacts
in the privileged context. Existing candidate/approval/control-change rules remain.
These requirements authorize no repository creation, credential provisioning,
remote messages, Git writes or live schedule enablement in this planning session.

## Later operating agreement, 2026-09-28

Amended 2026-09-28 (later discussion): AC11-AC13 include these requirements.
The daily schedule is now 05:00 Asia/Seoul refresh, 06:00 promotion and fixed
07:00 refresh-wait cutoff, superseding the earlier 08:00/09:00/10:00 times.

Records contain batch identity/trigger, pinned config/controller, revisioned
candidate/evidence/approval, frozen publication plan, append-only intents and
observations/retries/stops, and a reconstructible current index. Revise candidates
within the batch before promotion; afterward freeze source, versions and payloads.
Missing completion requires remote reconciliation rather than blind replay.

Duplicate requests join existing work. Never take over on elapsed time alone:
cancel stuck execution and confirm termination first. Unknown termination blocks
writes and requests action. Update owner and increasing handover generation against
the exact remote record revision; reload conflicts. Before each mutation recheck
owner/generation/live stop and persist intent. Generation alone does not fence an
external API: reconcile in-flight requests even after confirmed termination.
Unknown outcomes prevent blind retry. Concrete race-window enforcement is pending.

Bind evidence to dev commit, master base commit and proposed merge-result tree.
Required approval also binds versions and impact classification, showing changes,
migrations and evidence. Changed input commits renew necessary checks/approval.
Recheck immediately before merge; verify actual merge parents/tree afterward before
publication. Mismatch stops publication and requests action without undoing a merge.
Separately prove merge-time protection and choose an approval mechanism that binds
this exact candidate, rather than a mutable PR or an unqualified job approval.

Late refresh executes once; duplicate requests join. Late promotion never extends
the 07:00 cutoff. After 07:00 use integrated dev without waiting for refresh; ongoing
refresh may continue. Under the accepted review correction, pre-promotion dev
integrations refresh this candidate; post-promotion integrations enter the next
batch. Missed days
collapse into current accumulated changes, not one release per missed date. Recover
incomplete publication first, then take a due current-day opportunity. A missed
promotion is detectable from next-day 05:00, but alert once only when execution
returns and observes it. Completed no-op is not a miss. No separate watchdog is
required; total outage has no immediate notification guarantee.

Fixtures prove permitted progress and refusal for duplicate runs/takeover, changed
candidates, crashes around merge/tag requests, partial publication, storage outage
and stop/resume. Include intent/result/index gaps, delayed/missed schedules and
notification deduplication. Concrete schema, API/credential protection and approval
UI remain pending. Fixture success is not live rollout evidence.

## Domain contracts and coordinated template delivery

Amended 2026-09-28 (latest discussion): AC3/AC4/AC5/AC7 and new AC14 use this
contract, superseding the mandatory template submodule/gitlink and R2 proposal
below. Template stays independent; configs is the API source of truth. A pinned
template revision is used for compatibility checks, not ordinary provider use.
No generic common schema/interpreter is required merely because both domains
publish contracts. Unix-like and Windows own separate native contracts/tooling.

Publish machine-readable contract data tied to exact provider source: format
version, public inputs/types/requiredness/defaults, supported compositions and
system prerequisites, compatibility baselines, and removal/rename/default-change/
migration information. Derive structural metadata from actual declarations where
possible. Test authored constraints/examples against actual evaluation; contract/API
drift fails checks. Module inputs need honest limits, not claims of complete schema
coverage. Inspection reports usable, change required or unknown, never runtime proof.

Current pinned host tooling reads candidate contract data before candidate code is
executed. Unknown contract formats refuse guesses and direct explicit tool transition
or intermediate upgrade; candidate evaluation/checks follow prepared host changes.
Keep substantial inspection logic versioned with configs rather than copying it
into generated hosts. Old host pins remain supported by their own version; changes
to machine/profile inputs are explicit breaking migration, not silent reinterpretation.

The configs API change owns required template adaptations in the same work outcome,
with scope/repository-owned commits and PRs. Test exact configs/template candidate
pairs, including fresh generation and existing-host update inspection. Changes that
fit the existing contract need compatibility checks, not gratuitous template edits.
Changed contract format/start structure requires completed adaptation and evidence
before release. Cross-repository commits are not atomic. Check tested-source identity
after tagging, then update the template default reference without changing old hosts.

Template default-reference update is a recoverable post-release follow-up. Failure
alerts once and retries without reverting tags or blocking later provider releases.
Collapse accumulated updates to the newest compatible verified release; stale work
must never regress the reference. This exception does not waive required pre-release
adaptation or domain tag publication recovery. Exact update credentials, approval/
integration mechanics and retry implementation remain unresolved.

Template starts Unix-like from provider defaults, Windows from core-only opt-in,
and Homebrew from empty installation lists. Do not duplicate provider policies.
Request only fields needed by the chosen composition; safe path discovery does not
authorize guessing a user/target machine. Missing required machine information blocks
application with actionable errors. Examples/fixtures use synthetic values. Generated
hosts must inspect pinned-provider contracts without following latest template.

This consolidation also fixes Unix-like stateVersions at NixOS/HM 25.11 and Darwin 6,
adopts common default coding agents and independent standalone/graphics/WSL axes,
and retains Windows opt-in with explicit host customization semantics. Domain specs
own detailed acceptance. All earlier exact machine matrices are historical proposals.
Support OS/architecture/venue coverage, concrete exported formats, implementation
lanes and live account provisioning still require resolution before execution.

## Selective verification and release limits

Amended 2026-09-28 (later verification discussion): AC5/AC6/AC10/AC12 use
contract-first selection. Required proof covers public API, generated configuration,
composition/default/override/opt-out rules, dependencies and affected builds.
Add native behavior checks only for important provider-owned behavior that cannot
be established otherwise. Do not require every app launch, OS/session combination
or private machine. Hosts own actual devices, external application combinations,
permissions/accounts/networking and final usage. Narrow guarantees explicitly,
never waive failure of a promised supported contract merely because it is optional.

Declare required versus advisory checks before execution. Missing/failed required
proof blocks promotion; advisory results do not by themselves gate, but actual
contract defects discovered there must be treated as defects. Known external/host
limits may be disclosed without blocking an otherwise valid contract. Data-loss
or unintended-system-mutation risks require repair or safe explicit restriction.
Unknown/unverified behavior is not a pass. Do not reclassify failed checks afterward.

Select affected contracts plus their dependencies, union mixed changes, and fall
back to the owning domain's complete required suite for unknown impact. Test both
selection and exclusion; selector changes verify the selector and affected dispatch.
Changes reducing gates require the agreed control-rule approval and take effect in
later batches. Record candidate, selector revision, selected checks/reasons/results
and effect-based exclusions. Excluded-as-unaffected is not freshly passed evidence.
No cross-candidate pass reuse. Unrelated domains are not prerequisites.

Distinguish contract failure, transient infrastructure failure, missing required
venue and unknown failure. Only transient errors use agreed retry delays. Equivalent
replacement venues require evidence; no automatic private-machine fallback or
support narrowing. Hosted ubuntu-26.04 is a documented potential venue, not executed
CI evidence; Ubuntu graphics/WSL venue feasibility does not by itself define gates.

Same-repository dev-to-master source promotion remains one merge candidate: if both
domains changed and one fails required proof, promotion stops. Repair or explicitly
revert on dev; no selective-domain source promotion. Post-promotion successful domain
tags remain immutable while missing tags recover. Release records separate supported
contract, changed impact, actual evidence and host conditions/known limits.

## Template relationship (superseded proposal)

Include configs-host-template as a pinned submodule for contract discovery,
official consumer examples, compatibility checks and new-host generation.
Generated hosts own independent inputs, locks and changes. Template updates
never rewrite existing hosts. Inject the selected provider revision during
generation rather than requiring a circular provider/template release pair.
An ordinary provider evaluation must not require fetching the template.

Cloning the template is a supported starting approach, not the only possible
transport. Submodule placement, recursive checkout and packaging need explicit
verification; a GitHub flake/archive must not be assumed to include submodules.
Use synthetic identities in public fixtures and retain older consumer contract
cases so updating both template and provider cannot conceal a break.

## Earlier pickup lanes (R2 superseded by independent template delivery)

R1: repository policy, release classification and tooling migration. Inputs:
reviewed domain contracts and completed stage-2 plan. One repository PR for a
coherent adopted governance outcome, with fixtures, policy and affected-dispatch
checks. Retain historical releases and evidence. Stop/replan if proposed
automation changes authorization, protection or domain ownership.

R2: template gitlink/checkout integration and contract-test dispatch. Depends
on reviewed template content and the Unix-like contract. Plan final path
classification before authoring the gitlink. External template changes and
domain configuration changes have their own owning-repository/domain PRs.
Check checkout with and without recursion and ordinary provider consumption.

No lane is ready for execution from this document alone: stage 2 must provide
the actual gate design and the relevant domain lane must be refined before
pickup. The next planning session owns continuation; no worker is assigned.
Resume from the adjacent study's 2026-09-28 handoff: finish the environment/host
contract, derive provider evidence, then design recurring promotion/release
opportunities and batching. Machine-based distribution remains optional.

Amended 2026-09-28 (latest consolidation): add AC14 for contract discovery
and verification. Earlier criteria are interpreted with the latest dated
consolidation above; historical proposals do not override that amendment.

## Accepted independent-review corrections

Amended 2026-09-28 after accepted independent review: AC3/AC5/AC11/AC12/AC14
include these corrections, superseding conflicting earlier timing wording.

07:00 ends refresh waiting, not candidate updates. Integration before promotion
refreshes the current candidate/checks/required approval; only integration after
promotion enters the next batch. Recompute check selection from the COMPLETE
current-master to candidate promotion delta each time, not preceding-candidate
delta. Domain versions still compare previous tags. Record comparison identities;
test candidate A changing one domain and B adding another without pass reuse.

Required template adaptation must be tested AND delivered at an agreed durable
consumer-facing ref before release. Candidate-only PR evidence is insufficient;
changed delivered code requires pair revalidation. Nonblocking post-release
recovery applies only to the provider-tag default-ref update, not required code.
Exact delivery ref and integration mechanics remain implementation design.

Readerless existing hosts need one-time explicit pinned-reader bootstrap, legacy
input inspection/migration proposal, then candidate validation. Test legacy and
ordinary contract-aware upgrades separately. No automatic activation is implied.
Windows applied-state capture records remain host-local, not private release data.

## Change-driven verification selection refinement

Amended 2026-09-28 (after the final audit, latest discussion): AC5/AC6/AC10/AC12
use a small explicit changed-path/function-to-check mapping initially, not an
environment-count matrix or a complex inferred dependency engine. Domain-owned
specs define applicable checks. Supported environments alone do not create repeated
evidence obligations; shared code use alone does not require separate WSL evidence.
Select checks that establish changed behavior or connections, union mixed changes,
and handle additions/deletions and both sides of renames. Document why each selected
check is needed. Documentation-only changes retain applicable policy/document checks.

This supersedes the earlier automatic whole-domain fallback for unknown impact:
unmapped changes require mapping review, with bounded expansion within the affected
area. If that area cannot be established, selection remains unresolved and promotion
waits; unknown never means no checks. Do not automatically require every domain
build or native session to compensate for incomplete classification. This selection
refinement also applies during the redesign: changed wiring needs evidence, unchanged
applications need not be re-certified as a new migration prerequisite.

Preserve the full current master-to-candidate comparison on each candidate,
positive/negative selection fixtures, trusted selector revision, reason/result and
unaffected-skip records, and no reuse of prior-candidate passes. Applicability is
declared before execution, never narrowed after failure. Missing/failed selected
required evidence still blocks promotion. Actual CI/gate changes are implementation
work; this planning amendment does not change existing enforced policy.

## Single-flake template coordination

Amended 2026-09-28 (latest consumer-structure discussion): AC3/AC4/AC14 use an
independent template with one root flake and lock producing multiple Unix-like host
outputs through a minimal dendritic flake-parts/import-tree structure. This replaces
the per-host flake/lock recommendation, not domain independence or explicit adoption.
Unix-like composition details belong to the companion Unix-like spec. Windows does
not acquire a Nix dependency. The template contains synthetic examples only, and
does not synchronize generated hosts automatically.

The private host companion transitions directly to shared inputs and resolves
concrete issues rather than pre-provisioning per-host old-version exceptions.
Hosts remain separately selectable for checks/build/apply/recovery. Template and
host connectors derive comparison declarations from the same explicit inputs used
for construction, without copying the provider schema or consuming internal module
classes. Required template adaptation is still delivered before release; only the
default tag-reference follow-up is post-release. Root dispatch/gate changes have
separate scoped PRs with explicit before/after dependencies and no validation gap.
No private-host checks become recurring release requirements. Current source and
adopted policy remain unchanged until implementation is explicitly undertaken.

## Minimal credentials and exact-candidate approval

Amended 2026-09-28 (latest controller discussion): AC11/AC12/AC13 use one dedicated
fine-grained personal access token initially, not a GitHub App or separately minted
task tokens. Limit selected repositories to configs, the private operating repository
and the template when automated template updates are included. These must be within
the token's supported resource-owner boundary. No configs-hosts access is needed.
Accept account dependence and manual token replacement; do not add token renewal
infrastructure. Expired/revoked credentials stop writes and request operator action.

Initial permissions: Contents read/write, Pull requests read/write, Checks and
Commit statuses read, Actions read. Verify each actual endpoint at implementation;
add only demonstrated missing permissions, not speculative Issues/Administration/
workflow-edit access. One token's permission set applies across its selected
repositories; this is not per-repository privilege isolation. Preserve protection
rules without operational bypass. Stuck-run cancellation still requires termination
confirmation; Actions read alone does not implement cancellation, so the eventual
endpoint/permission design must explicitly resolve controller versus manual cancel.

Use one dedicated GitHub Environment in configs for the PAT and private repository
locator. Only trusted controller jobs receive it; candidate validation has neither
the token nor private operating configuration. Restrict allowed execution references;
do not require human Environment approval for every routine daily run. Implement and
verify the actual workflow/ref/secret boundary against the account before enablement:
an Environment name alone does not establish trust. Candidate scripts, executables,
artifacts and caches are never executed by privileged control. Previously approved
controller revision and next-batch control-change rules remain in force.

For exceptional approvals use one manual approval workflow. The request identifies
batch/candidate, dev/master commits and expected merge result, proposed domain
versions/impact, migrations and evidence. Operator supplies the candidate identifier;
the workflow verifies an authorized actor and exact current candidate, then records
approval in private operating history. It does not merge. The controller revalidates
approval and live candidate before acting. Candidate/version/impact changes invalidate
approval. PR prose/comments are explanations, never approval authority. Ordinary
eligible patch/minor work needs no such approval. Actor identity verification and
write serialization must be tested in implementation; do not create a second
unsynchronized writer through the approval workflow.

GitHub references reviewed for this design:
https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
and https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow .
The proposal does not authorize token issuance, environment/protection changes,
workflow dispatch, external messages or live writes. Remaining concrete protection,
remote-write reconciliation and notification delivery decisions stay pending.

## Controller execution and remote-write simplification

Amended 2026-09-28 (latest controller agreement): AC5/AC11/AC12/AC13 adopt the
following implementation direction and explicit limits. This supersedes earlier
Actions-read-only, unresolved cancellation and stronger merge-time isolation claims.

Give the single PAT Actions read/write for automatic cancellation. Only cancel the
recorded owning controller run after matching repository, workflow, run ID and
attempt. Do not cancel unrelated CI, merely old work or the input-refresh job at
07:00. Repeated schedules join existing work. Use GitHub execution status and bounded
job timeouts, not a new heartbeat service. Legitimate validation/retry waits are
recorded and not considered stalls. A timeout can initiate cancel, never authorize
takeover by itself. Confirm actual termination and reconcile outstanding remote
effects before acquiring ownership. Unknown termination blocks new writes.

Use master for scheduled/manual controller and approval/resume entry; restrict the
operational Environment to that ref. Observed default branch was master during
read-only GitHub inspection on 2026-09-28. Pin the approved controller commit for a
batch, retaining it across recovery; newly promoted control governs new batches.
Implementation must prove that a new master entry resuming an old batch retains
old control/approval rules, not just an old script path. No candidate dev code is
executed with the PAT. Ref restriction alone is not complete secret isolation.

Schedule, approval and resume deliver requests to one controller entry rather than
becoming independent operational-record writers. Process requests after ownership
is acquired. Cancellation/termination inspection may run before the record-write
critical section so a stuck owner does not prevent its own cancellation; this phase
does not mutate operating records. Re-read state before takeover. Do not automatically
cancel an existing owner merely because a newer trigger arrived.

Persist related state and appended history as one Git commit whose parent is the
exact operating-branch head read. Update its ref without force; conflicting advancement
requires reload and revalidation, not blind replay. Preserve history against rewrites.
No database/lock service is introduced. If the response is lost, reconcile operation
identity and expected content against remote history, including already-applied
commits. This groups writes inside the operating repo only; external merge/tag writes
still follow intent -> external operation -> observed result, without cross-repository
atomicity. Git objects not reachable through the accepted branch are not saved state.

Before promotion recheck dev/master/expected merge tree, evidence and any exact
approval, then request a merge commit with the expected dev head SHA. Verify actual
merge parents/tree before publishing tags. Keep one promotion path, including manual
operator promotion through that path. Do not enable master strict up-to-date checks
merely to require promotion-merge history back in dev. The current inspected master
protection had Required checks, admin enforcement, no force/deletion and strict=false.
The API head guard is not an atomic expected-base guard. Concurrent outside mutation
can therefore change a source merge despite the preceding checks; the accepted
guarantee is to stop publication of an unexpected result, notify, and never auto-undo
the merge. Do not claim prevention of every competing source merge. This explicitly
refines the earlier requirement to prove merge-time candidate protection.

Use GitHub Actions failed-workflow notifications initially, without notification
Issues or external services; no Issues-write permission is added. Failures and new
human-action/approval needs end the controller run with a failure conclusion and
a safe summary distinguishing their reason (approval-needed is not failed candidate
validation). Successful/no-op/normal-wait runs emit no deliberate alert. An already
reported identical blocker remains recorded and visible without deliberately raising
a fresh action alert; it never becomes passed validation. GitHub user notification
settings and platform-generated duplication are outside complete controller control.
Verify actual receipt for scheduled runs during the authorized manual rollout.
Do not promise durable deduplication when the private record store cannot be read.

Keep transient retry delays 5/15/30 minutes in credential-free wait jobs in the
same workflow. Each controller job records the retry and finishes; the workflow
remains pending during its bounded wait. The resumed controller rechecks ownership,
stop state and remote outcome before retry. No extra scheduler, polling service,
heartbeat or token renewal machinery is required. Wait jobs consume runner time;
this tradeoff was accepted for initial simplicity. Known waits must not trigger
stuck-controller cancellation. Three extra failed attempts produce one action-needed
outcome; non-transient errors do not blindly retry. No workflow has been implemented.

References checked: GitHub workflow events/notification documentation and REST Git
commit/ref and PR merge APIs. The controller protection, dispatch, race/refusal,
recovery, notification and permission fixtures/live checks remain delivery evidence,
not established by the planning probes.

## Cross-work pickup and evidence reconciliation

Amended 2026-09-28 (cross-work reconciliation): AC3/AC4/AC5/AC6/AC11/AC12/AC13/AC14
use the following dependency and evidence interpretation. Earlier general statements
that stages 2/3 are still undecided are historical. Work assignment still pins fresh
origin/dev and the reviewed plan and requires explicit implementation/Git scope.
No implementation lane, native result or operational setup is certified here.

| Outcome | Owning work / scope | Dependencies and delivery boundary |
| --- | --- | --- |
| Unix-like environment API, composition, contract/reader and readiness | provider-consumer-contract U1 / unixlike | Synthetic independent consumer proof; preserved host transfer material; candidate-pair proof with template; no private fleet activation gate |
| Darwin host capture | provider-consumer-contract U2 / unixlike | U1 setting inputs; whole-unit ownership and minimal provider-only schema; root capture/publication coupling has its own repository change |
| Windows declaration/generation | host-consumer-contract W1 / windows | Native independent implementation and explicit source/host/generated boundary; no dependency on U1 or its evaluator |
| Windows host capture | host-consumer-contract W2 / windows | W1 document/connection format; ownership capture, not delta merging; generation/source/partial-write fixtures |
| Provider lock refresh tool | automatic-flake-refresh / unixlike | Can implement tool fixtures independently; select actual provider inputs after U1 ownership transfer for final wiring |
| Shared release selection/controller | provider-release-contract / repository | Relevant domain contracts/evidence and delivered required template adaptation before affected release; unrelated domain work does not block it |
| Daily refresh/PR orchestration | scheduled-flake-refresh / repository | Refresh tool delivered; shared controller/trust/record/approval mechanisms reused, not a second controller |
| Host/template adoption | separately owned external companion work | Single-flake dendritic topology, common inputs by default; exact candidate proof and one-time transfer; no recurring private-host dependency |

Distinguish candidate-pair evidence, provider PR integration and release readiness.
Template may be checked against an exact provider candidate before either final
delivery. Provider PR integration need not wait for a not-yet-created release tag;
required adapted template code must be delivered at a durable ref before releasing
that API, with exact delivered-pair revalidation when code changes. Only the later
default tag-ref update is nonblocking. U1 work completion still accounts for its
required companion delivery; it is not synonymous with its provider PR merging.
Private host restructuring is separately owned and does not enter public CI.

Repository dispatch prerequisites compatible with current source may land first;
new-structure-dependent dispatch follows the owning source without an unchecked
integration window. Identify exact files/PR order at pickup; root governance cannot
be included in a Unix-like/Windows PR merely to make one atomic change. Existing
enforced policy is amended by its implementation owner, never bypassed by a plan.

The five acceptance tables cover complete work outcomes, not an unconditional
per-change test matrix. Select checks by changed function/connection and record
applicable evidence before execution. Empty/unmapped selection is not a pass;
resolve unknown scope or block. Initial support/tool qualification remains finite
implementation evidence, not repeated proof for every unrelated feature edit.
Document checks verify document form only; all report criteria remain pending.

One PAT includes Actions write for confirmed automatic cancellation and no Issues
write. The scheduler uses the same master-only control and failure/action-only
notification model. Candidate refresh runs unprivileged: the publisher may validate
an expected lock-data diff but must not execute candidate scripts/artifacts with
the PAT. Generated lock-only changes and trusted publication remain distinct jobs.
Approval-needed/operational failure conclusions belong to controller runs, not a
substitute for or a manufactured failure of the candidate's Required checks.

Implementation pickup must resolve the concrete controller entry/recovery mechanism
for pinned old-batch semantics, wakeup after candidate validation, serialized request
handling, timeout values, stop/cancel races and actual API permissions/protections.
These are explicit engineering proof obligations, not reasons to add App services,
heartbeats or broad machine tests. Short controller jobs may be separated by the
accepted credential-free wait jobs; the workflow itself stays alive while waiting.
Actions notification receipt and possible duplicates, particularly when records are
unavailable, remain rollout observations rather than absolute guarantees.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC14 | Independent domain-owned API contracts match implementation; API change work delivers required template adaptations and exact-pair checks before release, while post-release template reference updates recover independently without regressing refs, changing host pins or blocking later releases. | review, fixtures, policy checks, affected dispatch |
| AC1 | Adopted policy and tooling release configs as one desired computing environment with independent platform implementations, supported configuration/composition contracts and host-owned final realization; recurring dev-to-master promotion and immutable host-pinnable releases specify triggers, candidate/evidence binding and recovery separately from host deployment. | review, fixtures, policy checks, affected dispatch |
| AC2 | Domain semantic release classification preserves old tags and refuses a routine patch when the supported contract breaks. | review, fixtures, policy checks |
| AC3 | The independent template is discoverable and tested at an exact revision against the provider contract without a required gitlink; generated hosts are independent and ordinary provider consumption works without template checkout. | review, fixtures, affected dispatch |
| AC4 | All three stages are reconciled in order around the environment/host contract, with dated scope-owned amendments for changed criteria and explicit dependencies, evidence, recovery and authorization before implementation. | review |
| AC5 | Master promotion requires all evidence in a reviewed provider-contract coverage map for each changed domain, including applicable evaluation, build/native generation and native behavior checks; missing or failed required evidence blocks promotion, while private-host final integration, deployment and actual-use validation remain host responsibilities and unchanged unrelated domains are not prerequisites. | review, fixtures, policy checks, affected dispatch |
| AC6 | Provider verification uses contract-derived synthetic positive/negative cases and justified platform/native checks, prefers hosted native runners, demonstrates coverage and capacity for the selected checks, and reports limits without equating a machine inventory with required coverage or hosted Server results with Windows client behavior. | review, fixtures, affected dispatch |
| AC7 | Release discovery lets hosts select immutable source-bound release points and assess structured changes, compatibility and verified coverage at an explicitly chosen distribution granularity; machine-based units remain optional, domain versions and ownership are retained, and coarse or unknown impact is not presented as exact host-output change or equality. | review, fixtures, affected dispatch |
| AC8 | Release impact covers configs-supplied configuration definitions/artifacts, necessary dependencies, management tools and public contracts at a declared granularity, distinguishes environment/provenance-only changes, and leaves exact final-host comparison with hosts rather than requiring it for publication; missing or incompatible evidence is never reported as unchanged. | review, fixtures, affected dispatch |
| AC9 | Unix-like and Windows start independent stable semantic series at 1.0.0 after contract implementation and verification, maintain one active major each, preserve legacy and retired-major tags without an implied backport promise, and expose maintenance/major-transition information without changing host pins. | review, fixtures, policy checks |
| AC10 | CLI/CI release tooling independently evaluates commit-preserved structured impact declarations, cumulative domain changes and explicit verification records, produces the same version or refusal for identical complete inputs without an agent/model adapter, and rejects missing, malformed or contradictory classification and unmet conditions rather than guessing. | review, fixtures, policy checks, affected dispatch |
| AC11 | The accepted 05:00 refresh / 06:00 promotion / 07:00 refresh-wait-cutoff cycle and manual path enforce serialized exact-candidate validation/approval, permitted unattended actions, cumulative independent-domain versions, no-op handling, notification and immutable same-source publication recovery without private-host deployment or verification bypass. | review, fixtures, policy checks, affected dispatch |
| AC12 | Trusted control logic and credential boundaries, exact-candidate approvals and fresh validation, action-only deduplicated notifications, bounded transient retries, durable workspace-independent idempotent tag recovery and preview/manual/scheduled rollout are implemented and verified without treating mutable PR prose as machine authority or claiming fixture results as live enablement. | review, fixtures, policy checks, affected dispatch |
| AC13 | Public configs control reads pinned private operating configuration and append-only batch records through restricted CI connections, with reconstructible indexing, checked single-writer recovery, live stop/revocation and explicit resume, opt-in/misconfiguration distinction, private README and public-output isolation; unavailable storage prevents new mutations, and no separate backup system or private-host dependency is introduced. | review, fixtures, policy checks, affected dispatch |
