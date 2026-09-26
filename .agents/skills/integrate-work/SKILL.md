---
name: integrate-work
description: Inspect GitHub Ready PRs, admit one protected dev integration at a time, request targeted worker repairs, and recover integration from GitHub without local branch inference.
---

# Integrate work

Use CONTRIBUTING.md "GitHub integration" and the accepted GitHub workflow
decision. This role requires merge authorization; worker delivery authorization
does not grant it. Read-only admission review may proceed without a merge.

## Reconstruct from GitHub

Query open Draft and Ready PRs, base/head SHA, checks, reviews, unresolved
conversations, mergeability, dependency/stack and auto-merge settings. Inspect
recent merged PRs when recovering. Use gh pr list/view/checks and the API;
unknown or pending mergeability/check data is not approval. Local worktrees
are repair workspaces, never the candidate list. Do not create ready/merged/
ci-passed labels or local JSON/YAML queues.

## Admit one candidate

1. Review the Ready PR's actual diff/result and linked plan. Check dependencies,
semantic blockers and risk-specific review needs. Respect explicit blocked or
high-risk metadata. No global human review requirement is added.
2. Re-query required checks and reviews at the exact current head. Inspect
existing auto-merge requests before admitting another candidate after restart.
Do not arm several unrelated PRs and claim this serializes integration.
3. With dev strict protection, refresh only this candidate when required.
Return conflict resolution or semantic corrections to its worker. Withdraw
admission and have the worker mark the PR Draft before repair, so a green
intermediate push is not mistaken for completed delivery. A recreated
worktree from the remote feature branch is sufficient. Never locally combine
several PRs into dev and push the result.
4. After every update, wait for current-head required checks and review rules.
Immediately re-query head and base. With merge authorization, request GitHub
merge-commit integration using gh pr merge --merge --match-head-commit <sha>,
after all required conditions pass. Do not arm new unattended auto-merge
requests: they can survive an authorized worker push to a different head.
Never --admin or bypass.
5. Query the result. Accepted requests and armed auto-merge are not merged.
Confirm the merged PR/commit and updated dev before selecting the next PR.
If checks fail or the base moves, return to inspection; do not busy-loop updates.
If recovery finds an already armed request, disable auto-merge and confirm it
is cancelled before asking any worker to change the head. If it merged during
cancellation, inspect that result rather than pretending admission was revoked.

## Constraints and recovery

This personal repository does not use Merge Queue. Auto-merge neither updates
a branch nor validates a queue group. A single operator-managed integrator is
the serialization convention; strict protected dev is the server-side gate.
Do not add a redundant lock or unattended controller framework.

Native stacks were verified in a separate lab, including automatic upper-layer
rebase and shared merge commits. They are not enabled here until trunk-to-head
CI and all-layer admission are verified. Fail closed on a stack candidate:
inspect it but do not merge using the ordinary independent-PR procedure.
Use prerequisite-first independent delivery meanwhile. No published rewrite
exception is granted by the lab result.

A failed or crashed admission is reconstructed from GitHub. If the expected
head changed, inspect again. Do not replay an old merge request automatically.
Promotion dev to master and releases remain run-version-control-workflow tasks;
a completed integration does not authorize activation or Apply.
