id: repository/required-checks-gate
statement: Master branch protection requires one stable gate, which fails unless classification and the repository-wide scans passed and every selected domain job succeeded, and no unselected job ran.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/required-checks
enforced-by: fixture tool/version-control/test

Conditional job names are not protection contexts: a skipped domain must
neither weaken nor deadlock the gate.

2026-10-07: local-development-workflow.md replaces remote dev admission.
Local combined-result checks precede exact-SHA integration; push only checks
transmitted history, and Required checks applies to master PRs. Concise local
evidence replaces a mandatory PR body. Closing keywords are also checked in
current master incoming history.
