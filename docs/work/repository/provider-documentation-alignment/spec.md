# Align provider documentation and consumer topology
kind: spec
date: 2026-09-30
scope: repository
status: approved
review-by: 2026-10-07
issue: #425

## Problem

The Unix-like provider boundary reached dev in PR #421, but repository usage
and architecture still describe machine-kind routing, provider installation
tools and the earlier per-host consumer flakes. The accepted single-flake
consumer direction also needs a durable repository decision. Prepared root
documentation is a candidate, not evidence that connected repositories have
delivered their new structure.

## Decisions

Adopt the already agreed single-flake consumer direction in a successor to
the initial repository ownership decision. Retain one private repository and
the public template's one-time-copy relationship. One consumer flake and lock
select shared inputs; individual host declarations still select native modules
and deployment remains host-specific. This does not add a common-domain
component or automatic template synchronization.

Align root usage, workflow, architecture and repository status with the
delivered provider. Describe unmerged host/template changes as candidates,
preserve historical records, and distinguish provider delivery, companion
delivery, release readiness and host activation. Private activation is no
provider completion prerequisite.

## Lane D: repository documentation delivery

Outcome: one repository-only PR with the durable topology decision, accurate
usage and pending consumer status, and this spec/report pair.

Inputs: current origin/dev at pickup; the reviewed provider contract and
decision delivered by PR #421; the latest consumer-structure amendment in
docs/work/unixlike/provider-consumer-contract/spec.md; the preserved detached
root-document candidate; fresh connected repository source/pin observations.
The provider spec is design input to this adoption, not continuing policy.

Dependencies: provider boundary and reader tools must already be on dev.
Final companion publication is not required to explain the intended topology,
but present-tense claims of adoption require durable consumer delivery.
The execution issue identifies one continuation owner. No other worker edits
these root documents or topology decisions concurrently.

Evidence: manual source/citation and pending-state review; work-document,
whitespace and repository policy checks; actual commit/push/CI dispatch for
this documentation change. No new invariant or executable control is
introduced, so existing fixture implementations are unchanged.
Configuration evaluation, build, runtime,
activation and Windows Apply are outside this lane.

Stop and return to planning for an unapproved topology choice, a consumer
delivery claim without evidence, a new implementation/enforcement obligation,
or a competing continuation owner. Preserve the detached candidate, stashes,
patches and ignored checkpoints; never use notes/ as context.

Amended 2026-09-30: AC4's affected-dispatch evidence records the actual
selector, correcting the initial no-fixture-suite assumption. Root README
and CONTRIBUTING paths select the repository fixture suite in CI; commit
and push select no suite, and no configuration-domain suite is selected.
This documentation change does not alter selection or lower CI requirements.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The durable repository decision adopts the agreed single-flake/shared-input direction, preserves independent host deployment and one-time template origin, and retires contradictory per-host topology authority. | review, policy checks |
| AC2 | Root usage, contribution procedure and architecture match the delivered provider contract, tools and host ownership, without assuming consumer candidate delivery. | review, policy checks |
| AC3 | Repository status preserves historical adoption and records provider delivery separately from pending companion references, U1 completion, API release readiness and host activation. | review, policy checks |
| AC4 | The final change contains only the assigned repository documents, preserves the original detached candidate, and passes work/policy checks with documentation-only affected dispatch. | review, policy checks, affected dispatch |
