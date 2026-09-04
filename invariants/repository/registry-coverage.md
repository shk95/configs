id: repository/registry-coverage
statement: Every registered invariant's declared enforcement exists and names it, and every enforcement that names an invariant is registered.
rationale: docs/architecture.md § Invariant registry
enforced-by: tool tool/version-control/invariants
enforced-by: fixture tool/version-control/test
decision: docs/decisions/invariant-registry-created.md § The invariant registry is created with pending entries
owner: repository maintainer

The registry is only worth having if it cannot drift from the things it
describes. The check reads both directions: a declared locator that no
longer contains its tag, and a tag that names an entry that was deleted, are
both failures. Nothing in the registry is exempt, including this entry.
