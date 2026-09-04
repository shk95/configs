id: repository/required-checks-gate
statement: Branch protection requires one stable gate, which fails unless classification and the repository-wide scans passed and every selected domain job succeeded, and no unselected job ran.
rationale: docs/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/required-checks
enforced-by: fixture tool/version-control/test

Conditional job names are not protection contexts: a skipped domain must
neither weaken nor deadlock the gate.
