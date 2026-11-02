id: repository/required-checks-gate
statement: The stable CI result fails unless classification and global scans passed, each selected job succeeded and every unselected job skipped.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/required-checks
enforced-by: fixture tool/version-control/test
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Decision

Master pushes, optional topic PRs and candidate dispatch produce this evidence.
Ordinary direct writes have no remote status admission prerequisite.
