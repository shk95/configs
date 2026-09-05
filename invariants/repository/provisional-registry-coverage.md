id: repository/provisional-registry-coverage
statement: Every temporary measure in the tree is registered with an exit condition and a review date, every registration has a tagged measure in the tree, and an overdue registration fails only its own scope.
rationale: docs/architecture.md § Provisional registry
enforced-by: tool tool/version-control/provisional
enforced-by: fixture tool/version-control/test
decision: docs/decisions/provisional-registry-created.md § The provisional registry records what must become false
owner: repository maintainer

A temporary measure with no registration is indistinguishable from a
permanent one, and a registration with no measure is a promise about a tree
that has moved on. The check reads both directions and adds time as a third:
an entry carries the date by which someone looks at it again, and letting
that date pass is the failure the registry exists to make visible. The scope
restriction is not a softening — an overdue Windows measure blocks Windows
work — but AGENTS.md forbids requiring an unrelated domain to pass in order
to validate the changed one.
