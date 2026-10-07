# Local completion with protected master
date: 2026-10-07
scope: repository
status: accepted
supersedes: docs/policy/decisions/repository/github-agent-workflow.md
source: docs/work/repository/local-development-workflow/spec.md

## Decision

Dev continues from reset 0fc573e and master from 81229c1, keeping the accepted
input patch at 60bcd46 without inheriting the cancelled backup implementation.
Local dev is the development basis and integration authority. Worktrees isolate
topic authoring; final combined candidates are checked and integrated sequentially
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

The initial cutover prepared candidate N on master M0 and replaced remote
dev/master with N/M0 under separate one-time authorization. Protected PR #546
accepted that source. This initial topology is superseded by the lane
correction below; its evidence remains historical.
No reset/force option is added to ordinary tools. Agent Rack and its existing
extraction are independent follow-up work.

## Amendment 2026-10-07: preserve branch lanes

The maintainer requested separate first-parent paths rooted at dev 0fc573e
and master 81229c1. Reconstruct the dev-side master synchronization with dev
as its first parent, retain the published master patch at 60bcd46, and replay
the existing source changes unchanged. Protected PR #547 accepted the corrected
promotion after exact-source CI; both branch trees were preserved at transition.

For subsequent work, master synchronization is a dev-based merge that keeps
the development lane as its first parent even when fast-forward is possible.
Verified topic-to-dev integration remains exact-SHA fast-forward. Master
promotion remains a protected merge-commit PR; dev continues on its own lane
afterward. Reflect master at the next explicit work/promotion synchronization.
