id: repository/conventional-subject
statement: A non-merge commit subject is a Conventional Commit of at most seventy-two characters.
rationale: docs/architecture.md § Version control and releases
enforced-by: tool .githooks/commit-msg
enforced-by: fixture tool/version-control/test

The commit-message hook is the owner of the grammar, including which
subjects Git writes itself and are exempt. `tool/version-control/audit`
carries a second copy of the pattern for history audit; where the two
disagree the hook is the rule and the audit is a defect to align.
