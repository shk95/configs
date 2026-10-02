---
name: inspect-work
description: Report worker workspace handoffs and GitHub work status read-only, distinguish uncertain session liveness, and provide verified resume guidance.
---

# Inspect work

Run tool/configs session inspect for local worker checkpoints. Read only the
worktree root's .work-session.md and Git state; notes/ remains out of bounds.
A missing checkpoint is unknown, not idle. A stale timestamp or absent process
is insufficient proof that a worker is finished. An active marker is an intent
record, not a heartbeat. Report contradictions and ask the operator to identify
ownership before another writer enters that worktree.

Query GitHub separately for linked plans/issues/PRs, Draft/Ready, current checks,
reviews, dependencies and merge result. Do not copy these fields into local
session notes. Report two views: recoverable local execution and remote
integration; make missing or inaccessible remote information explicit.

Where a recorded Codex session ID is valid, the command prints codex -C <path>
resume <id>. It is guidance, not evidence the session is running or resumable.
For another client or missing ID, print the worktree path and handoff rather
than inventing a command. Never resume or mutate a worker while only reporting.

For possible cleanup, pass the evidence to reclaim-workspaces. The worktree
inventory is permitted here for execution-space management, never integration
candidate selection.
