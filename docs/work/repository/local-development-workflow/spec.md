# Local development completion and protected master
kind: spec
date: 2026-10-07
scope: repository
status: approved
review-by: 2026-10-21

## Goal

Reconstruct from reset dev 0fc573e and reset master 60bcd46. Include the
accepted Unix-like patch at master; do not adopt the cancelled backup flow.
Local implementation, relevant verification and sequential dev integration
complete development before optional push and maintainer-selected promotion.

## Decisions

Use local dev for worktree creation. Author and resolve conflicts in topic
worktrees, verify the final candidate, then fast-forward primary dev to its
exact SHA. Remove implicit publication, pruning, dev CI and report-driven
automatic issue closure. Keep scope ownership, honest evidence, linked
authoring, protected master and immutable domain releases. Small changes need
only a concise result; retain paired plans for work that needs them.

Agent Rack, its extraction overlay and plugin installation are outside scope.
Do not introduce a controller, queue, state database or automatic base repair.

## Execution

1. Local flow: project policy, used skills, helpers, lightweight hooks and
   fixtures change together in one repository outcome.
2. Remote-ready source: master CI/protection expectations and input patch
   declaration duplication are aligned with regression coverage.
3. Integrate the verified local candidate into dev. Remote ref replacement is
   a separate one-time operation after review of exact candidate/current refs;
   it is not a prerequisite for this implementation report to be done.

No dev PR boundary is required. Master adoption uses the first normal dev to
master PR after cutover. Remote qualification remains in Actions/PR records.
Stop for unexpected ownership, changed acceptance or unsafe remote drift.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Worktree creation uses local dev without origin and includes local-ahead work. | fixtures |
| AC2 | Routine edits cannot publish or prune; dry-run and refusal preserve refs and source. | fixtures |
| AC3 | Final candidate integration supports parallel work and conflict resolution with exact SHA ff-only; push checks inspect transmitted commits without running checkout suites. | fixtures, review |
| AC4 | Project policy, used skills, adapters and records allow local completion without PR, issue or push. | policy checks, review |
| AC5 | Dev automatic CI is absent; master admission, stable required gate and distinct protection expectations remain covered. | fixtures, affected dispatch, review |
| AC6 | Input patch uses one allowed-input declaration and retains exact-source checks, immutable publication and recovery behavior. | fixtures, policy checks |
