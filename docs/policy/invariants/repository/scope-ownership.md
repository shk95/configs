id: repository/scope-ownership
statement: Each tracked path has one owning scope, and each ordinary source commit carries paths from at most one owning scope.
rationale: AGENTS.md § Domain boundaries
enforced-by: tool tool/version-control/classify
enforced-by: tool .githooks/pre-commit
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test
enforced-by: fixture tool/version-control/test-workflow.py
enforced-by: fixture tool/version-control/test-staged-checks.py

Ownership decides domain release scope and which domain may change a path.
The classifier is the only ownership map; hooks and CI refuse an
`unclassified` answer. A rename counts as a change to both owned paths.
Merge commits may combine histories from several scopes. Check selection
follows change effect through `tool/dispatch/select`, independently of
ownership.
