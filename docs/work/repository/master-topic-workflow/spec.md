# Master and topic workflow
kind: spec
date: 2026-11-02
scope: repository
status: approved
review-by: 2026-11-16

## Goal

Use master as the release and ordinary authoring branch. Group a coherent
outcome requiring multiple logical commits on a topic merged with no-ff.
Ask the user whether to use a linked worktree. Keep project operation usable
through tracked tools without private agent environment or plugin state.

## Boundary

Prepare and stage source only. Do not commit, merge this topic, push, alter
remote settings, delete dev, publish a tag or activate a host. Preserve
existing history. Remote adoption is reported separately from local proof.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Tracked tools support master direct work and master-based topics with an explicit current/linked workspace choice and no implicit remote writes. | fixtures, review |
| AC2 | Integration verifies the exact clean candidate and unchanged master base and creates a no-ff merge; invalid, stale or conflicting input refuses without discarding work. | fixtures |
| AC3 | Hooks, history audit, CI and remote audit support direct master commits and topics without a dev dependency; bounded patch publication retains exact CI and immutable-tag proof. | fixtures, affected dispatch |
| AC4 | Policy, procedure, invariants, adapters and status agree; deterministic rules and check selection live in tracked tooling. | policy checks, review |
| AC5 | The final result is staged without a commit or remote mutation and records unavailable evidence and remote migration steps. | review |
| AC6 | Mechanical values have one tracked declaration at their owning execution boundary; shared branch/workspace/merge/remote values are validated and agents need no private operating state. | fixtures, policy checks, review |
| AC7 | Worktree removal reviews exact head, unique commits, tracked/untracked/ignored data and refuses unsafe removal; start state is inspectable. | fixtures |
| AC8 | Manual candidate CI and merge support live successful exact base/head/tree evidence without a general PR; stale, wrong or failed evidence refuses. | fixtures, affected dispatch |
| AC9 | Ordinary force pushes refuse locally; an isolated maintenance App can execute only a fresh explicit protected-environment approval, exact old/new lease and verified recovery while leaving protection unchanged. | fixtures, affected dispatch, review |
| AC10 | Current documents, invariants, tests and remote adoption instructions agree; all source remains staged without commits or remote writes. | policy checks, review |
| AC11 | Remove unused push selection, duplicate workspace creation and persisted verification receipts; preserve start records, exact-source verification and approval/recovery boundaries. | fixtures, review |
| AC12 | Checkpoints support only atomic nonempty handoff save and inspection without model-specific identity or lifecycle state; invalid writes preserve existing data. | fixtures, policy checks, review |
| AC13 | Repository declarations, procedure and remaining tests describe the simplified operation; independent review informs the change and source remains staged only. | fixtures, policy checks, affected dispatch, review |
| AC14 | Agent guidance requires only task-relevant reading and operations; same-task workspace choices and explicit authorization remain valid, with no mandatory role/plugin/startup recital. | policy checks, review |
| AC15 | Current context accurately describes isolation topics, classifier/evidence limits, permission adapters and master-based audit; unaccepted observations do not delay explicit maintainer decisions. | policy checks, review |
| AC16 | Procedure and scoped review checklists agree with the minimal agent contract while retaining manual invariant evidence, approval and preservation boundaries; executable behavior and permission allowlists are unchanged and all changes remain staged only. | policy checks, review |
| AC17 | Local and CI paths share topic ownership and source-range checks; Windows runtime-governance changes require exact hosted native proof, and candidate execution has explicit read-only token permissions without persisted checkout credentials. | fixtures, affected dispatch, review |
| AC18 | Growth from direct master work to a topic preserves staged/unstaged changes and any already accepted master commits through an explicit authorized transition procedure. | fixtures, review |
| AC19 | The approved maintenance contract uses a personal/public-repository-supported isolated App exception with exact effective-rule verification and documented minimum API permissions; missing capability refuses and no remote setting is changed. | fixtures, affected dispatch, review |
| AC20 | Workspace removal accepts an exact retained topic ref as source preservation, keeps dirty/ignored/operation/head protections, verifies retention and optional external recovery, and the complete result remains staged only. | fixtures, policy checks, review |

## Amendment 2026-11-02: mechanical operating contract

The maintainer requested the reviewed follow-up in the same checkout, still
staged only. Add acceptance for a single tracked mechanical declaration,
inspectable operation records, preservation-safe workspace removal, exact
hosted candidate evidence without a general PR, and human-approved isolated
history maintenance. No actual remote settings, approvals or pushes are made.

## Amendment 2026-11-02: remove unnecessary mechanics

Amended 2026-11-02 AC6: the maintainer requested implementation of the
simplification investigation with independent subagent judgement. CI YAML is
itself a tracked mechanical declaration; do not mirror workflow-only secret
or concurrency names in JSON. Keep cross-workflow safety checks. Add AC11,
AC12 and AC13 for removing unused paths and redundant state, simplifying
handoff notes and verifying retained safety boundaries. The same current
checkout and staged-only boundary continue. Retain the domain-editing commit
helper and approved-history maintenance capability; neither is redundant Git
operation. Historical execution evidence below is not rewritten as new proof.

## Amendment 2026-11-02: minimal agent context

The maintainer requested simplification of non-mechanical version-control
context, correction of false descriptions and removal of unnecessary agent
policy. Add AC14, AC15 and AC16. Continue the previously selected current
checkout and staged-only boundary. Limit changes to tracked guidance,
procedure, explanatory adapter comments and evidence; preserve executable
mechanics and actual permission allowlists. Independent reviewers identify
duplicate startup/approval obligations, stale role orchestration and incorrect
enforcement claims. Domain configuration and historical execution records are
outside this follow-up.

## Amendment 2026-11-02: final review corrections

The maintainer authorized the five identified final-review improvements in the
same checkout, still staged only. Add AC17-AC20 for check-path consistency,
scope growth, explicit CI token bounds, feasible approved maintenance and
retained-branch preservation. Amended 2026-11-02 AC7: an exact retained branch
is valid source preservation when only its worktree is removed; external
recovery remains optional and validated. Amended 2026-11-02 AC16: its unchanged
executable behavior assertion records the completed minimal-context phase;
the runtime changes now explicitly authorized are assessed by AC17-AC20.
Existing Git history, source commits, remote settings and host deployment
remain outside the preparation boundary. Actual hosted adoption is separate
from API/permission fixtures and official support documentation.

## Amendment 2026-11-02: local acceptance

Amended 2026-11-02 AC5, AC10, AC13, AC16 and AC20: their staged-only evidence
records the completed preparation phases. After accepting that result, the
maintainer authorized its local source commit. This changes the delivery
boundary only; remote integration, push, publication and deployment remain
outside the request.
