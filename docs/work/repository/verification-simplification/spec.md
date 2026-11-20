# Verification scope simplification
kind: spec
date: 2026-11-19
scope: repository
status: approved
review-by: 2026-12-19

Reduce vetoes whose failures do not warrant stopping the operation. Preserve
the incoming-history, secret, ownership and exact-source publication gates.
Retain full domain checks when the effect of a change cannot be established.

Earlier reductions include effect-based CI selection at `9f22bbc`, the
removal of duplicate promotion checks at `09ebe3f`, and the master and topic
workflow simplification at `a4435b3`.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Routine commits and candidate verification omit document-index and citation vetoes; unrelated changes do not trigger work-record validation. | fixtures, policy checks |
| AC2 | Local setting checks cover payloads. Candidate verification selects the owning platform suite for all settings changes. CI definition edits use one selection, and unknown inputs fail. | fixtures, affected dispatch |
| AC3 | CI proof requires exact successful selected evidence without a veto from diagnostic jobs. The retired capture fixture still proves refusal with no side effects. | fixtures |

## Amendments

Amended 2026-11-19, AC2. The maintainer accepted removing settings-only CI
and the source-record retention exception after neither was selected in a
replay of the last 100 first-parent master changes. Local quick checks and
exact reuse of previously proved provider suites still serve their existing
roles.
