---
name: inspect-work
description: Inspect local work and useful handoffs read-only; query remote state when relevant.
---

# inspect work

Read requested worktree Git state and useful checkpoints with session inspect.
Report base/head, tracked/index/untracked/ignored state and unfinished work.
Do not read notes/. A checkpoint is not proof of liveness or integration.

Local completion may be ahead of the remote. Do not turn missing PRs, open
issues or absent remote branches into incomplete local development. Query
GitHub only for requested remote inspection or relevant preservation evidence.
Resume guidance needs verified identity and actual current state; preserve
unknown ownership instead of inferring a live or dead session.
