id: repository/staged-checks-use-index
statement: Staged domain checks inspect staged source and checker content without including unstaged or untracked files or changing the caller's source, index or references.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool .githooks/pre-commit
enforced-by: fixture tool/version-control/test-staged-checks.py

The materialized source has no Git metadata. Repository-wide scans continue
to read the caller's index directly. Native parser semantics remain owned by
the domain; the fixtures prove orchestration with disposable check doubles.
