---
name: reclaim-workspaces
description: Review preservation before explicitly requested workspace cleanup.
---

# reclaim workspaces

Read actual local commits, tracked/index/untracked/ignored data and useful
checkpoints before recommending cleanup. Do not read notes/. A clean diff,
old checkpoint or merged PR does not prove useful data has been preserved.

Check integration into local dev and any relevant explicitly queried remote
copy. Local unpushed dev may preserve a completed candidate; note where its
only copy lives. Retain/resume, uncertain or eligible are review outcomes,
not deletion authorization. With explicit removal authorization use non-force
worktree removal for the named target. Branch deletion needs separate review.
Never invoke automatic prune or force removal to make the review pass.
