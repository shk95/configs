# Local completion with protected master
date: 2026-10-07
scope: repository
status: accepted
supersedes: docs/policy/decisions/repository/github-agent-workflow.md
source: docs/work/repository/local-development-workflow/spec.md

## Decision

Reconstruct from reset dev 0fc573e and master 60bcd46, keeping the accepted
input patch without inheriting the cancelled backup implementation. Local dev
is the development basis and integration authority. Worktrees isolate topic
authoring; final combined candidates are checked and integrated sequentially
by exact-SHA fast-forward. Fail on conflicts or unexpected base changes.

Local implementation, required verification and integration complete a task.
Push, master promotion and domain publication are separate operations. Dev
does not require PRs, remote checks or automatic CI. Master keeps strict
Required checks, PR admission, conversation resolution and merge commits;
administrator enforcement and no force/deletion remain for both branches.

Use paired plans where sustained planning has value, concise evidence for
small changes and useful checkpoints for interruption. Issues are optional,
handled explicitly and never prerequisites of local completion. Remove
automatic prune and report-driven issue closure. Retain no-closing-keyword
protection and apply it to the current master PR's incoming range as well.

This replaces the Ready-PR completion, origin/dev pickup and server-side dev
integration portions of old workflow/work-model/linked-authoring decisions.
Keep domain ownership, authoring isolation, truthful evidence, publication
boundaries and useful work preservation. Old results remain historical.

## Input patch

Keep master-only permitted input updates, exact checked source, writer
credential separation, immutable annotated tags and publication recovery.
Read the existing Unix-like allowed-input declaration instead of copying its
list into YAML. Manual waiting and automatic event continuation retain their
existing completion meanings. No domain source or host deployment changes.

## Cutover

Prepare candidate N locally on M0. After reviewing current remote identities
and writer state, replace only remote dev/master with N/M0 under a separate
one-time authorization; preserve tags. Restore everyday protections, adopt N
through normal dev to master PR, verify the actual gate, then resume writers.
No reset/force option is added to ordinary tools. Agent Rack and its existing
extraction are independent follow-up work.
