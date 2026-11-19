id: repository/provisional-registry-coverage
statement: Every temporary measure in the tree is registered with an exit condition and a review date, every registration has a tagged measure in the tree, and overdue registrations are reported as warnings.
rationale: docs/policy/architecture.md § Provisional registry
enforced-by: tool tool/version-control/provisional
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/provisional-registry-created.md § The provisional registry records what must become false
owner: repository maintainer

A temporary measure with no registration is indistinguishable from a
permanent one, and a registration with no measure is a promise about a tree
that has moved on. The check enforces both directions. It warns after the
review date so the owner can revisit the measure separately from unrelated
source work.
