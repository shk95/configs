# Author source changes in linked worktrees

date: 2026-09-25
scope: repository
status: accepted

The primary checkout is the integration point for this repository. A task that
edits tracked source uses a dedicated linked worktree and topic branch. The
worktree lives until its pull request merges, so review feedback returns to
the same index and dependency directory. Reading, checking and integrating
may happen from the primary checkout. A separate native Windows clone may
inspect an unpublished branch for host evidence without authoring its source.

This is a local authoring rule. A deterministic guard refuses commits from
the primary checkout, including those started by the routine commit helper.
The canonical workflow requires the worktree before editing because Git has
no hook for an editor's file write. CI sees committed content and cannot prove
which directory an editor used, so it does not claim to enforce that part.

A request pinned to a commit is prepared in a linked worktree at that exact
commit; the topic branch is attached there before source edits. The normal
start helper uses the freshly fetched `origin/dev`. Publication still follows
the existing topic-branch-to-`dev` policy and an out-of-date fixed base is
caught up through the documented local merge procedure.

Rejected: making the primary checkout read-only through filesystem modes.
Git updates and integration need to write there, and file modes would affect
those operations without identifying which task owns an edit.

Rejected: treating a CI check as proof of authoring location. The worktree
path is not present in a commit or pull request.

## Amendment 2026-10-07: local completion

The accepted local-development-workflow.md decision replaces conflicting dev
PR admission, remote pickup/delivery, automatic closure and promotion-history
restrictions. Retained domain and publication boundaries remain in force.
The statements above record the earlier operation and its evidence.
