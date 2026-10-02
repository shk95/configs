---
name: reclaim-workspaces
description: Assess whether worker worktrees can be reclaimed, preserve unfinished and unpushed work, and recommend safe cleanup or session resumption.
---

# Reclaim workspaces

Begin with inspect-work. Default to a read-only recommendation, not deletion.
Never decide from age, process absence, PR closure or a clean tracked diff alone.

For each candidate check:

- checkpoint and operator-confirmed ownership/liveness; active or unknown means
retain until ownership is resolved;
- tracked modifications, index, untracked and ignored files (including local
handoff); list paths without reading notes/ content;
- local commits versus a freshly fetched remote branch; all useful commits must
be pushed, intentionally retained elsewhere, or explicitly abandoned;
- GitHub PR and remote branch existence. Closed-unmerged is not delivered;
merged does not prove there are no subsequent local commits;
- resume instructions and whether local-only verification/handoff needs saving.

Report retain/resume, uncertain, or eligible with the concrete reason. A Ready
PR with its pushed branch can preserve integration without a worktree; a merged
PR is not mandatory. Conversely an abandoned exploration may be removable with
no PR when the operator has accepted its disposition.

Only after explicit cleanup authorization, remove the specific eligible
worktree using the normal non-force command. Do not force away dirty/untracked
or ignored data; do not delete the remote feature branch while it is needed
for a PR or dependency. Local branch deletion is separate from workspace
removal. The older worktree done helper performs removal but does not prove
eligibility; this review must precede it. Report what was removed and retained.
