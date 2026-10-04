# Resolve production refresh handoff and immutable object effect compatibility
kind: spec
date: 2026-10-04
scope: repository
status: approved
review-by: 2026-10-18

## Assignment and purpose

Root owns this planning return under #479 and manual-source-continuation.
The existing protocol-3 refresh-branch effect requires a publicly existing head
object and declares only one ref effect. It cannot authorize hidden blob/tree/commit
writes. Finish a reviewable compatibility contract before assigning production
refresh, public object publication or finite-writer source. This child is design
work and cannot close the parent operating issue.

Candidate source delivery and production exact-map closure are prerequisite source
increments. Pin the current dev and this reviewed planning revision independently
at each pickup. Root keeps shared transport and semantic source ownership serialized.

## Required design result

Preparation runs on a separate runner/run from the privileged writer, with no
writer token, private Environment or private packet. The writer remains one finite
job. The first manual topology consumes an exact already completed preparation
run/attempt; automatic preparation dispatch is a separate future effect and is not
assigned. Preparation executes only pinned reviewed utility bytes and returns
bounded literal lock data and independently checkable provenance. No returned
script, checkout, hook, Git config or executable artifact reaches writer execution.

Choose and document an exact data handoff contract, including run/attempt/workflow/
job/source identity, completion, original tool bytes, source fingerprint and
before/after lock bytes/modes. If Actions artifacts are chosen, explicitly resolve
metadata/digest, pagination, expiring redirect authority, token separation, size/
expansion bounds, exact entries, traversal/symlink/duplicate refusal and replacement/
expiry. An artifact or asserted digest cannot prove independent provenance. A
credential-filtered environment alone cannot establish OS isolation.

Introduce explicit semantic compatibility for immutable public objects, preferably
one refresh-object operation per bounded blob/tree/commit with exact type/bytes/SHA,
refresh generation and prerequisite object identities. Every object has durable
intent before its POST and exact-SHA independent observation afterwards. The
writer derives fixed metadata and complete lock-only tree/parent closure; arbitrary
caller object graphs and metadata are refused. Observe each prerequisite before
existing refresh-branch/ref and refresh-pr effects. An unknown object acknowledgement
fences later objects/refs/PRs; branch absence is not object absence and creates no
retry permission. Read-only recovery must distinguish exact existing object,
conflicting/corrupt object and unavailable observation.

Specify the next semantic protocol and new package manifest explicitly. Preserve
original protocol 1/2/3 packages, reducers, transcripts, operation IDs and replay;
do not reinterpret old refresh-branch payloads. New event/payload/transcript bounds,
loader/transport inventories, historical dispatch and decision/invariant changes
must be enumerated. New object effects need positive/negative real-Git/synthetic-API
fixtures, including partial success, lost responses, restart, stop/head/source
movement, owner/job drift and complete original replay. Public object API authority
is distinct from private Journal object writes, even if REST paths look alike.

## Pickup and boundaries

The design report must identify accepted durable decision/invariant changes and
executable same-scope increments with inputs, dependencies, verification and stop
conditions. Unresolved endpoint origin, credential boundary, original schema or
recovery semantics remain explicitly not ready to pick up. Adopted durable results
belong in decisions/invariants; this work document grants no operating authority.
Source implementation follows a separately reviewed child plan after this design
bar is met. No deployment workflow enablement, token grant, private packet, dispatch,
initializer, master promotion, release, schedule, activation, Apply or cleanup.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Exact separate-run preparation/data handoff and credential/OS boundaries are specified, including independent provenance and bounded data acceptance; every unresolved download/endpoint authority is explicit and prevents source pickup. | review |
| AC2 | New semantic object effects bind exact bytes/hashes/dependencies and durable intent, independent observation and lost-response/restart handling before ref/PR effects without changing historical protocol semantics. | review |
| AC3 | Durable decisions/invariants, package/loader/dispatch/fixture changes and ordered same-scope source increments are enumerated with evidence and replan gates; parent acceptance remains unchanged and pending. | policy checks, review |
| AC4 | Exact generated-lock release declarations and domain review custody bind base, before/after lock and original utility/rules/package; missing or changed declarations block finite manual/scheduled writer pickup without invented impact or compatibility. | review |

## Dated release declaration pickup amendment

Amended 2026-10-04: AC4 adds a required design gate alongside AC1-AC3. The
preparation fixture's chore(unixlike-deps) subject is not a production declaration.
The Unix-like domain decision owner must review exact base, before/after lock,
utility source and original rules/package, and supply Release-Format, Release-Domain,
Release-Impact, Release-Contracts, Release-Compatibility, Release-Rationale and
Release-Migration with explicit custody binding. Writer construction serializes
reviewed declarations; fixed Git metadata does not authorize semantic judgement.
A changed base/lock/rules invalidates the declaration. Exact promotion approval
cannot substitute for missing trailers. Do not turn unsupported source-only/none
into patch or default dependency changes to compatible. Without an accepted narrow
automation policy, manual/scheduled writer records its finite blocker/refusal and
terminates pending domain review. No automatic publishing fallback is introduced.
