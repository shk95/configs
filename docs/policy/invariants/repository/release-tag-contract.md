id: repository/release-tag-contract
statement: A domain release tag is annotated, immutable, prefixed with its domain, and targets a commit reachable from master; it certifies only its domain, with Windows host evidence in labelled blocks and Unix-like provider and common evidence at domain level.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool tool/version-control/plan-release
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test
enforced-by: manual the reviewer reads the annotation for a machine name, an account name or a machine-unique identifier before the tag is created and reports that reading
owner: repository maintainer
decision: docs/policy/decisions/repository/annotated-tag-is-the-release-record.md § The annotated tag is the only release record
decision: docs/policy/decisions/repository/release-annotation-states-each-host.md § The annotation carries a block per host

The annotation is the portable evidence record, and the only one: no GitHub
Release duplicates it. Activation and Apply are later events and never
inferred from the tag. The Unix-like provider and `common` tag state their
three lanes once and certify no private host consumer. Windows states the
lanes per host. The two tags created before the host-block form are excepted
by name. That a label or reference names no machine is the manual half.
