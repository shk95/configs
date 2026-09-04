id: repository/hooks-are-the-tracked-ones
statement: A clone that opted into local hooks runs the tracked hooks directory of one of its worktrees, however the setting is spelled.
rationale: docs/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test

The setting is compared as a directory, not as a string: an absolute value,
a relative one, and a linked worktree's shared value all name the same
tracked hooks. A value that resolves elsewhere, or none, is the local gate
being absent, which the audit reports and the doctor names.
