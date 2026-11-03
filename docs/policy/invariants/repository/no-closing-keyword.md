id: repository/no-closing-keyword
statement: No incoming source commit message or master topic pull request body carries a GitHub closing keyword before an issue reference.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/closing-keywords
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/work-planned-and-verified-in-documents.md § Work is planned and verified in documents, and a branch is one increment

Commit-message hooks reject closing keywords before source is committed. History
audit applies the same checker to direct master commits and topic commits;
master PR CI also reads its current body. Issue management is explicit and
not implied by source acceptance. Historical dev-era operation remains in
decision history; it is not a current range exemption.
