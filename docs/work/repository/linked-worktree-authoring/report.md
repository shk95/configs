# Report: require linked worktrees for source authoring
kind: report
spec: docs/work/repository/linked-worktree-authoring/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review: Codex and an independent Astra reviewer inspected the linked-worktree procedure and decision on 2026-09-25. Read-only inspection, primary-checkout integration and a separate native Windows check clone remain available; a pinned base is verified before attaching its task branch. |
| AC2 | verified | Fixtures: `tool/version-control/test` passed on 2026-09-25, including primary-checkout hook and helper refusal, linked-worktree acceptance, primary help and prune, and linked-caller worktree creation and cleanup of a nonstandard pinned path. |
| AC3 | verified | Fixtures: the pre-commit and helper entry points select `require-linked-worktree`; `tool/version-control/test` passed. Policy checks: `tool/version-control/invariants` and `tool/version-control/work --working-tree docs/work/repository/linked-worktree-authoring` passed on 2026-09-25. The Windows capture writing path has its own Windows-scope change and native CI lane. |

## Evidence lanes

- Review: Codex reconciled the independent review against the current `origin/dev` tree on 2026-09-25. The repository guard can detect a linked worktree; task dedication and the editor location remain reviewer evidence.
- Fixtures: `tool/version-control/test` passed on 2026-09-25 after the follow-up changes.
- Policy checks: `tool/version-control/invariants`, the work-item check and `git diff --check` passed locally. Native Windows execution is not repository-scope evidence.
