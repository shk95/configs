id: repository/promotion-source
statement: master accepts only a same-repository dev promotion preserving accepted input patch history or a current-master-based single-commit permitted Unix-like input patch, through a merge-commit pull request with at most one master pull request open.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool tool/version-control/check-promotion
enforced-by: fixture tool/version-control/test
enforced-by: fixture tool/version-control/test-release.py
decision: docs/policy/decisions/repository/master-input-patch-releases.md § Decision

General promotion is source acceptance, not release. The independent input
patch lane publishes only Unix-like. The CI promotion job runs the
source check and the one-open-promotion check on every pull request against
master.
