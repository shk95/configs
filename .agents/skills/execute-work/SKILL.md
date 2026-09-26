---
name: execute-work
description: Implement a planned worker lane or a small unambiguous change in an isolated worktree, checkpoint interruptions, and deliver a Ready PR without merging.
---

# Execute work

Read the owning scope's policy and use CONTRIBUTING.md "Agent roles and
handoff". Confirm the request authorizes necessary branch, commit and remote
writes; existing authorization carries through the agreed task.

## Pick up

1. Check linked plan, execution issue and GitHub open PRs for an existing owner
or completed result. A planned lane requires an explicit assignment from the
planner or user to this worker before implementation; a free-looking checklist
is not a claim. Conflicting assignments return to the planner. A task with uncertain scope, multiple criteria or a
substantive design decision goes to plan-work before implementation.
2. Fetch origin/dev, record its exact SHA, and immediately enter the task's
linked worktree. One worker lane owns one feature branch. Pin the plan's
reviewed commit separately; if using an approved uncommitted plan, record that
it is provisional and publish its revision before handoff to another worker.
3. Validate plan assumptions against that base. Keep minor implementation
adjustments inside acceptance. Scope or acceptance drift requires checkpoint
and planner return, not another hidden branch in this worker.
4. Run tool/configs session start <plan-path-or-> <lane> in the worktree.
Use a stable runtime session ID when available. Never invent a resume ID.

## Implement and deliver

Make the coherent same-scope change; internal steps may branch conceptually
without producing separate PRs. Run narrow relevant checks before broader
checks and preserve unavailable versus failed evidence. Record actual evidence
in the report with the change that produced it. Do not change planner-owned
priorities opportunistically.

Commit and push the feature branch. Prefer an early Draft PR after the first
useful push; PR creation only at the end remains valid for a small task.
Use gh pr create --draft --base dev and a body file with scope, result,
verification, limitations and Refs issue links. Do not use commit --publish:
that human convenience helper arms auto-merge and exceeds worker responsibility.
Once work is complete, required checks have passed on the current head and
required reviews/blockers are accounted for, use gh pr ready. Record handoff
and checkpoint as handed-off. Ready is a candidate, not integration approval.

Never push/merge dev, arm auto-merge, choose other workers' merge order, or
use local branches/worktrees to find integration candidates. Do not eagerly
merge each dev change. On a real conflict or integration-requested update,
resume the worker, fetch, merge the needed dev base into the owned feature
branch, resolve, revalidate and hand off again. Do not rewrite published work.
Native stacks require the explicit supported stack procedure; otherwise wait
for a prerequisite to merge before starting its dependent lane.

## Interrupt, replan, resume

Before changing role or ending an unfinished session, checkpoint suspended
with goal, diff/commit, verification, missing work, reason and concrete next
step. Suspension satisfies the worker's handoff obligation; it is not success.
For replanning, keep the worktree and Draft PR; return with the same checkpoint.
The planner decides whether to resume, split, supersede or abandon. On resume,
inspect Git status and current remote PR/head before session checkpoint active.
After an approved replan, while suspended, run session replan <spec-path> with
a handoff naming the amendment, its new revision and continuation owner; then
resume. A scope change starts a new scope-owned lane/worktree instead.
Do not replay a stale command or overwrite a server-updated branch.

An abandoned task records disposition of every useful/unpushed change. A
handed-off worker may release its worktree after reclaim review once the remote
branch and PR preserve all deliverable work; PR review can recreate a worktree.
The ignored session note is local recovery help, not durable integration state.
If feedback arrives after reclamation, verify PR/head and continuation assignment,
recreate from that remote feature branch, then use session recover <plan|->
<lane> [verified-original-base]. It records the recovered head separately and
leaves the original base unknown unless verified. Continue the existing PR;
do not invent a start base or try checkpoint active on a missing note.

If checkpoint writing was hard-killed, inspect .work-session.lock owner, note
and body. Confirm no writer owns it with the operator; PID/age alone cannot
prove that. Preserve useful partial handoff outside that lock, remove only the
confirmed stale lock files/directory, and retry. Never remove the workspace or
other ignored data as lock recovery.
