id: repository/change-authoring-in-linked-worktree
statement: A tracked source change is authored and committed from a task-dedicated linked worktree, while the primary checkout is reserved for inspection and integration.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool tool/version-control/require-linked-worktree
enforced-by: tool .githooks/pre-commit
enforced-by: fixture tool/version-control/test
enforced-by: manual The reviewer confirms the task used a dedicated linked worktree before editing
owner: repository maintainer
decision: docs/policy/decisions/repository/linked-worktrees-own-change-authoring.md § Author source changes in linked worktrees

The tool and hook refuse a commit in a primary checkout; the routine commit
helper calls the guard before it writes. The manual evidence covers editing,
which Git cannot intercept. Read-only checks, integration, promotion and
release operations may use the primary checkout. A separate native Windows
clone may check a branch without becoming its source author.
