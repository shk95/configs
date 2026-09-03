id: repository/conventional-subject
statement: A non-merge commit subject is a Conventional Commit of at most seventy-two characters.
rationale: docs/architecture.md § Version control and releases
enforced-by: tool .githooks/commit-msg
enforced-by: fixture tool/version-control/test

The commit-message hook is the owner of the grammar, including which
subjects Git writes itself and are exempt. `tool/version-control/audit`
asks the hook rather than keeping a pattern of its own, so history audit and
the commit gate cannot disagree.
