---
name: plan-work
description: Plan work from a request or roadmap, maintain roadmap priorities and actionable docs/work plans, and route genuinely simple changes directly to a worker.
---

# Plan work

Read AGENTS.md, CONTRIBUTING.md "Plan and verify work", docs/work/README.md,
the owning scope's current state and the task-linked work items. Inspect the
roadmap and generated work index before creating a duplicate plan. Do not
load every historical report as instructions.

## Route the request

- An explicit role is intent, not permission to ignore its entry conditions.
- For "I want to do X", first match existing work. A clear, single-scope,
single-acceptance-criterion change with known verification and no unresolved
design or dependency may go directly to execute-work. Explain the choice.
- Otherwise establish or amend a plan before implementation. A roadmap entry
is optional. The planner may derive a plan from the roadmap or plan directly.
- Read-only exploration may end without a worker or worktree. Before tracked
planning edits, create a dedicated linked worktree under the normal Git
permission boundary. Do not hold a worker lane while merely surveying work.

## Produce work that can be picked up

Create spec.md and pending report.md together and run the work preflight.
Use the format in docs/work/README.md. For each executable lane state the
outcome, owning scope, inputs and dependencies, intended PR boundary,
acceptance criteria, required evidence and stop/replan conditions. Steps and
test environments do not individually require branches or PRs. Cross-scope
outcomes have scope-owned specs; link the dependency rather than copying it.
Keep ready-to-pick-up lanes distinct from unresolved design. The execution
issue's checklist names the lanes and links active PRs; it stores no evidence
or copies of PR state. Re-query it and open PRs before assigning a lane. A
single planner assigns each lane; GitHub issue edits are not an atomic claim.
If competing claims appear, stop duplicate implementation and resolve ownership.

The plan records assumptions, not a frozen execution base. At pickup the
worker pins current origin/dev and the reviewed plan revision independently.
A worker can adjust implementation details within acceptance; changed scope,
acceptance or dependencies returns to planning after checkpoint. Amend criteria
with the dated rule, never silently rewrite the original bar.

## Maintain roadmap and receive handoffs

Manage docs/work and docs/work/roadmap.md. Other documentation is updated by
the owner of the implementation it describes, not automatically by this role.
Keep roadmap priorities, deferred work and historical outcomes separate.
A roadmap outcome may be planned, deferred, cancelled or completed with a
reason/reference; it does not mirror Draft, Ready or merged PR status.
Preserve item identities and historical evidence when priorities change.

For an incomplete worker return, read its checkpoint and actual diff first.
Decide resume same lane, split remaining work, supersede plan or abandon.
Preserve useful commits and evidence; do not mark unmet acceptance verified.
Name which worker owns continuation before allowing implementation to resume.
Planner may initialize reports; workers write their actual verification rows.
The maintainer accepts roadmap priorities and final completion.
