id: repository/scope-ownership
statement: Every tracked path has exactly one owning scope, and a path with none is refused before it is committed.
rationale: AGENTS.md § Domain boundaries
enforced-by: tool tool/version-control/classify
enforced-by: fixture tool/version-control/test

Ownership decides domain release scope and which domain may change a path.
The classifier is the only ownership map; hooks and CI refuse an
`unclassified` answer. Check selection follows change effect through
`tool/dispatch/select`, independently of ownership.
