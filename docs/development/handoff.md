# Continue and preserve work

## Local work and handoff

When continuing planned work, read its relevant record; use
`tool/configs records --table work` only when discovery is needed. Small clear
tasks need no work inventory or role handoff. Define acceptance using "Plan
and verify work" when a durable plan is useful. Record exact base/head at
verification, integration or handoff rather than requiring a separate planning
ritual before every edit. Use the agreed workspace and applicable checks.

Before interruption, leave the goal, exact base/head, evidence, unfinished
work and next step as plain handoff text. Optionally save it with
`tool/configs session save < handoff.md` and read notes from registered
workspaces with `tool/configs session inspect`. Save atomically replaces the
ignored `.work-session.md` only on explicit invocation, refuses empty or unsafe
writes, and preserves old-format notes until explicitly replaced. No lifecycle
state, agent identity or model-specific resume command is maintained.
Tracked policy and work documents remain the source of project context;
local notes supply no policy, approval, heartbeat or delivery proof.
Amend changed acceptance before relying on it; no separate planner role is
required. Uncertain liveness does not authorize cleanup.

Use session inspection and read-only Git state for requested local
handoffs. Remote status is optional and must be relevant to an explicit remote
operation or preservation review. Review unpushed/unique commits and tracked,
untracked and ignored data before any requested non-force removal. Do not read
notes/ content. Keep useful old worktrees; a clean diff is not preservation
evidence. No automatic pruning.

## Workspace preservation

`tool/configs worktree review <path-or-topic-name>` reports the exact head,
commits absent from master, tracked/untracked/ignored data and Git operations.
The exact topic ref retained in this clone preserves source when only the
worktree is removed; the tool checks it against registered metadata and HEAD
before removal and confirms the ref remains afterward. Unique commits are
reported without requiring an extra archive. Branch or clone deletion is a
separate preservation decision and is never part of worktree removal.
For additional external preservation, supply `--preserved-bundle <path>`.
The bundle must be outside the workspace and have no missing prerequisites.
The tool restores it into an independent disposable Git store and verifies
object integrity before accepting it as preservation evidence.
Ignored and untracked data still require separate preservation.
It never reads notes content or queries remote status. Primary checkout and
unsafe workspaces cannot be removed. Preserve reported data and source first;
then explicitly request removal with `tool/configs worktree done <path-or-name>
--expect-head <full-reviewed-SHA>`. Removal rechecks all blockers and retains
the branch. No force/remove-ignored override exists. This is not a liveness test.

## Plan and verify work

Use a spec/report pair when planning, decisions or sustained verification
need a durable record. A small unambiguous change may use its commit body and
concise result instead. An issue and roadmap entry are optional.

1. Classify the outcome and read relevant current work. Create the owning
   `docs/work/<scope>/<slug>/spec.md` and pending `report.md` together in a
   user-selected workspace. State acceptance, evidence lanes and dependencies.
2. Use `tool/configs work --working-tree docs/work/<scope>/<slug>` for feedback
   before staging, or `work --staged` for the index. These are alternatives
   for the state being checked.
3. Work and record evidence with the source change that produced it. Keep
   unavailable/failed evidence distinct. Change existing criteria only through
   dated amendments. Remote Actions evidence stays in Actions/PR records.
4. Mark implementation done when its criteria are verified. A later push or
   operational cutover can have its own pending record without undoing local
   completion. Issues are handled explicitly; use Refs links in source.
5. Retire obsolete active references with the adopted replacement. Do not
   rewrite historical failures as success or make all old report cleanup a
   prerequisite for current development. Archive paired records when their
   relevant preservation and reference review is complete.

The format remains `docs/work/README.md`; a work document is not policy.
