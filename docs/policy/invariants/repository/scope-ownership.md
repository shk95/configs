id: repository/scope-ownership
statement: Every tracked path has exactly one owning scope, and a path with none is refused before it is committed.
rationale: AGENTS.md § Domain boundaries
enforced-by: tool tool/version-control/classify
enforced-by: fixture tool/version-control/test

Ownership decides which release tag certifies a path, which CI job runs, and
which domain may change it. The classifier is the only map; the hooks and
CI refuse an `unclassified` answer rather than guessing.
