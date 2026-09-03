id: repository/hook-evidence-recorded
statement: A hook's check outcomes are recorded outside the working tree so that what the local gate refused can be counted later.
rationale: docs/architecture.md § Repository governance plane
enforced-by: tool .githooks/pre-commit
enforced-by: fixture tool/version-control/test

The 2026-09-03 review of the verification suite could count every CI
failure and no hook refusal, because hooks left no record. The log is one
line per outcome under the git common directory; it is runtime state and
never desired state, which is why it lives outside the tree.
