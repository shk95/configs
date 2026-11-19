id: repository/required-checks-gate
statement: The stable CI result requires successful classification and incoming policy checks, and successful execution or qualified reuse of every selected check.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/required-checks
enforced-by: tool tool/version-control/verify-policy
enforced-by: fixture tool/version-control/test
enforced-by: fixture tool/version-control/test-workflow.py
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Decision

Master pushes, optional topic PRs and candidate dispatch produce this evidence.
Local candidate verification and CI use the same fail-fast incoming policy
runner with the reviewed range and candidate index.
Ordinary direct writes have no remote status admission prerequisite.
Unselected results do not affect admission.
