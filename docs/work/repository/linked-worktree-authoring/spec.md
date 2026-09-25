# Require linked worktrees for source authoring
kind: spec
date: 2026-09-25
scope: repository
status: approved
review-by: 2026-10-25

The maintainer requires source changes and commits to take place in a task's
linked worktree. Reading, checking and native Windows verification in a
separate clone may still use their existing locations.

## Problem

The worktree helper creates task branches, and the agent skill says to keep a
worktree through review. Neither requires the worktree before an edit. The
routine commit helper can edit and commit from the primary `dev` checkout, and
the pre-commit hook does not distinguish primary and linked worktrees.

## Decisions

The primary checkout is for inspection and integration. A source change
starts in a task-dedicated linked worktree with a topic branch. The normal
helper starts from `origin/dev`; a user-pinned commit is verified exactly
before work and reconciled with `origin/dev` before publication.

A guard detects whether Git's current directory is a linked worktree.
Pre-commit refuses primary-checkout commits, and the routine commit helper
refuses there before writing. The agent skill and contributor procedure state
the editing rule; a reviewer confirms it because Git cannot intercept file
edits. Separate native Windows clones may inspect and test the branch.

Rejected: filesystem permissions on the primary checkout; integration writes
there. Rejected: claiming CI can prove the editor's directory from a commit.

## Increments

1. Repository fixtures and policy checks verify the local guard, hook and
   helper refusal and the linked-worktree path.
2. Review verifies the start procedure, authority, and Windows check boundary.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The authoritative rule and start procedure require a dedicated linked worktree for source edits while keeping inspection, integration and Windows native checks available. | review |
| AC2 | A primary checkout is refused before a commit or routine helper edit, and a linked worktree is accepted. | fixtures |
| AC3 | The guard is selected by pre-commit and the helper, and repository policy checks accept the new invariant and work item. | fixtures, policy checks |
