id: repository/promotion-source
statement: master accepts only a same-repository dev pull request, merged with a merge commit, with at most one such pull request open.
rationale: docs/architecture.md § Version control and releases
enforced-by: tool tool/version-control/check-promotion
enforced-by: fixture tool/version-control/test

Promotion is source acceptance, not release. The CI promotion job runs the
source check and the one-open-promotion check on every pull request against
master.
