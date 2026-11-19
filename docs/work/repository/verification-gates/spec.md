# Verification and publication gates
kind: spec
date: 2026-11-19
scope: repository
status: approved
review-by: 2026-12-03

## Scope

The maintainer ordered the verification redesign after the Unix-like 2.0.0
release on master. The maintainer owns verification responsibilities and any
later adoption of the resulting workflow on GitHub. This work changes
repository governance and keeps host deployment under the consuming domain.

Prevent incoming commits or merge results from bypassing ownership, message
and secret checks. Avoid repeating work when exact candidate evidence already
covers an obligation. Keep mutable publication state under the writer's own
checks. Record the evidence from each increment in the paired report.

The commit hook checks staged content and supplies fast author feedback. The
push hook checks transmitted commits and tags before exposing them. Exact
candidate checks cover the combined source tree, its incoming history and the
selected suites. Hosted evidence can replace only checks it proves for the
reviewed subject. Full history inspection is an operator diagnostic.

The evidence subject includes the event, base, candidate, tested checkout,
combined tree, workflow revision and definition, run attempt, and individually
identified checks with their platforms. The reader verifies live job results
and source evidence. A dispatch uses the workflow definition from the reviewed
master revision. A PR tests a synthetic merge with the event's exact parents.
Each write still checks current branches, clean source state where applicable,
and mutable PR and tag state. A master-push run may reuse tree-only suite
evidence when exact event evidence establishes that correspondence and the
required workflow and platform agree. Its incoming checks judge the actual
published history.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Commit, pre-push, verification and CI distinguish staged inputs, outgoing history and candidate checks. Incoming audits cover side history, merge-only effects, complete messages and secrets. Full history is an explicit diagnostic. | fixtures, review |
| AC2 | Dispatch selects units by effect, including their platform and runtime prerequisites. Unrelated domains remain independently verifiable and an unavailable selected unit cannot satisfy the gate. | fixtures, affected dispatch |
| AC3 | Merge and bounded release consume the same attempt-aware reader. It binds successful jobs and artifact to the workflow definition, required units and platforms, and exact source identity. | fixtures, affected dispatch |
| AC4 | Hosted evidence replaces covered local checks and CI reuses evidence only for equivalent obligations. Each writer retains immediate source, destination, metadata and immutable publication checks. | fixtures, review |
| AC5 | Current policy, operator procedure, enforcement, and positive and negative fixtures agree. Provider checks, runtime, and deployment evidence retain separate meanings. | fixtures, review |
| AC6 | A racing master update cannot land a bounded patch on an unreviewed base. Publication checks commit and tag metadata. Proof-format cutover detects unfinished automatic publications. | fixtures, review |

## Amendment 2026-11-19

Amended 2026-11-19 AC6: review of the draft identified a race between the last
master read and the GitHub merge call, a gap in metadata secret scanning, and
an unpublished-patch recovery risk during proof-format rollout. The follow-up
preserves the reviewed parent and tree in the actual ref transaction and
checks cutover readiness without editing remote controls.
