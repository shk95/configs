---
name: integrate-work
description: Inspect GitHub Ready PRs, admit one protected dev integration at a time, request targeted worker repairs, and recover integration from GitHub without local branch inference.
---

# Integrate work

Use CONTRIBUTING.md "GitHub integration" and the accepted GitHub workflow
decision. The maintainer owns admission and merge authorization; this skill
orchestrates the review and records the explicit grant. Worker delivery
authorization does not grant it. Read-only admission review may proceed without
a merge.

## Reconstruct from GitHub

Query open Draft and Ready PRs, base/head SHA, checks, reviews, unresolved
conversations, mergeability, dependency/stack and auto-merge settings. Inspect
recent merged PRs when recovering. Use gh pr list/view/checks and the API;
pending or unknown checks are not successful CI evidence, though a qualified
conditional request can wait on them. Local worktrees
are repair workspaces, never the candidate list. Do not create ready/merged/
ci-passed labels or local JSON/YAML queues.

## Admit one candidate

1. Review the Ready PR's actual diff/result and linked plan. Check dependencies,
semantic blockers and risk-specific review needs. Respect explicit blocked or
high-risk metadata. No global human review requirement is added.
2. Re-query the reviewed source head and current check state. Pending checks may
   proceed to a qualified conditional request; the writer requires successful
   exact-source checks before merge. A failed check blocks admission. A dev
   base movement during the request may be incorporated only by the bounded
   deterministic integration chain in the adopted decision; source changes
   remain outside the admission. Master promotion stays frozen-base/head. Inspect
   existing auto-merge requests before admitting another candidate after restart.
3. With dev strict protection, refresh only this candidate when required.
Return conflict resolution or semantic corrections to its worker. Withdraw
admission and have the worker mark the PR Draft before repair, so a green
intermediate push is not mistaken for completed delivery. A recreated
worktree from the remote feature branch is sufficient. Never locally combine
several PRs into dev and push the result.
4. After any update, refresh the candidate and its base. Once it is admitted
   and the maintainer has explicitly authorized its merge, ordinary supported
   candidates use:

   ```sh
   tool/configs conditional-merge submit --pr <number> --target dev \
     --head <full-head-sha> --base <full-observed-dev-sha> --confirm
   ```

   The command rechecks the exact identities and returns the Actions run URL.
   `requested` is not merged. Actions owns the bounded CI wait, final protected
   merge and result audit. The operator may leave after the dispatch has a
   confirmed run identity; do not arm auto-merge or infer a result from PR
   checks. If the writer is not yet qualified and enabled, or the candidate is
   marked high-risk, use the synchronous procedure in CONTRIBUTING.md instead.
   It rechecks exact head/base and required checks before the protected merge.
   A blocked candidate is refused.
5. On recovery, reconstruct request and outcome from the Actions run and PR.
   A run failure preserves the PR. If cancelling a run before worker repair,
   confirm it stopped first; if it merged during cancellation, inspect that
   merge. An ambiguous dispatch or merge is inspected on GitHub before any
   retry. A completed merge must identify the approved parents and tree and
   pass the post-merge audit before reporting success.

## Constraints and recovery

This personal repository does not use Merge Queue. Auto-merge neither updates
a branch nor validates a queue group. Qualified conditional requests retain
pending runs in Actions queues: dev writers use their own group, while master
writers share the input-patch group's serialization. Other manual writers do
not participate, so strict branch protection remains the server-side stale
target safeguard and no global writer serialization is claimed.

Native stacks were verified in a separate lab, including automatic upper-layer
rebase and shared merge commits. They are not enabled here until trunk-to-head
CI and all-layer admission are verified. Fail closed on a stack candidate:
inspect it but do not merge using the ordinary independent-PR procedure.
Use prerequisite-first independent delivery meanwhile. No published rewrite
exception is granted by the lab result.

A failed or crashed admission is reconstructed from GitHub. If the expected
head changed, inspect again. Do not replay an old merge request automatically.
Promotion dev to master and releases remain run-version-control-workflow tasks.
A completed integration does not authorize activation or Apply.
