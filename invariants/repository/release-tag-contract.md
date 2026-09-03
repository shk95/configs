id: repository/release-tag-contract
statement: A domain release tag is annotated, immutable, prefixed with its domain, and targets a commit reachable from master; it certifies only its domain.
rationale: docs/architecture.md § Version control and releases
enforced-by: tool tool/version-control/plan-release
enforced-by: fixture tool/version-control/test

The annotation is the portable evidence record. Activation and Apply are
later events and never inferred from the tag.
