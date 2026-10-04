# Report: production refresh handoff and object effect compatibility
kind: report
spec: docs/work/repository/release-refresh-object-compatibility/spec.md
status: pending

## Planning return, 2026-10-04

Root and independent read-only reviewer inspected protocol-3 adapter.operation,
Executor.request/reconcile and original reducer intent ordering. refresh-branch
requires a public head object and observes the ref only. Private Journal Git-object
writes do not authorize public object publication. Separate completed preparation
run consumption avoids introducing a new automatic dispatch effect at this stage.
The existing parent explicitly returns to planning for new endpoint/effect kinds
and credential boundaries. No source lane is assigned from an unresolved design.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | Separate-run topology identified; exact data download/redirect authority and deployed isolation have not been accepted. |
| AC2 | pending | One immutable-object intent per blob/tree/commit proposed; exact next-protocol schema, bounds and restart/reconciliation contract remain to review. |
| AC3 | pending | Ordered compatibility planning precedes refresh/object/writer pickup. No durable policy/source adoption or operating receipt is claimed. |
| AC4 | pending | Original fixture emits no Release-* trailers; domain-owned source-bound declaration/custody design must be accepted before generated commit construction and production source pickup. |

## Bounded semantic design settlement, 2026-10-04

Initial-only protocol 4 schema now includes original raw base/path trees/before-lock,
complete lock-only comparison, non-self-referential construction and topological
object IDs. Original replay preparation consumption output supports global
cross-batch uniqueness without reinterpreting old packages. Existing observation-only
recovery precedes takeover; no new claim-before-reconcile authority is needed.
These are reviewed design results, not implemented source or API proof.

AC2's initial-object design is settled for source pickup through refresh-object-protocol;
required-base merge proof remains explicitly pending under refresh-merge-proof.
AC1 preparation/download/provenance implementation and actual deployment remain
pending. AC3 durable adoption/source/native evidence and AC4 exact domain declaration
custody remain pending. Actual REST canonicalization success is an operating receipt
gate; source must enforce strict expected hashes and refuse mismatch before refs.
