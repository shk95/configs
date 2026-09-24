# Remove WSL GUI from the active roadmap

kind: spec
date: 2026-09-24
scope: repository
status: approved
review-by: 2026-09-25
issue: #359

## Problem

The roadmap still offers WSLg as deferred work although the maintainer has
decided that neither WSL output is to support Linux GUI applications. Current
repository-facing text must state the policy revision boundary without
rewriting the historical record of issue #21.

## Decisions

- Remove the active WSLg row and its assignment to #21. State that a future
  proposal begins with revision of the Unix-like architecture and invariant.
- State the same current boundary in user-facing and troubleshooting text.
- Preserve historical work documents and issue evidence, with a dated note
  distinguishing the old plan from the current roadmap.
- Reject retaining WSLg as a deferred item: it suggests implementation is
  authorized once the schedule changes.
- Reject deleting historical issue and report references: they record the
  decision that existed when that work was done.

## Increments

| Increment | Scope | Evidence lane |
| --- | --- | --- |
| R1 | repository | review and policy checks of the roadmap and repository-facing text |

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The current roadmap contains no WSL GUI work item and says that a new proposal starts with a Unix-like policy revision. | review |
| AC2 | Repository-facing guidance contains no current WSL GUI plan, and historical references are visibly dated rather than erased. | review, policy checks |

## Excluded

Unix-like configuration, host activation, and Windows WSL version parsing.
