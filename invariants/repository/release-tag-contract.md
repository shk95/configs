id: repository/release-tag-contract
statement: A domain release tag is annotated, immutable, prefixed with its domain, and targets a commit reachable from master; it certifies only its domain.
rationale: docs/architecture.md § Version control and releases
enforced-by: tool tool/version-control/plan-release
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test
decision: docs/decisions/annotated-tag-is-the-release-record.md § The annotated tag is the only release record

The annotation is the portable evidence record, and the only one: no GitHub
Release duplicates it. Activation and Apply are later events and never
inferred from the tag.
