id: repository/hygiene-declared-names
statement: An account or host name appears in committed desired state only when the inventory declares it, and an inventory that cannot be read is a failure rather than a permission.
rationale: docs/architecture.md § Desired-state hygiene
enforced-by: tool tool/version-control/hygiene
enforced-by: fixture tool/version-control/test
decision: docs/status.md § Desired-state hygiene had no enforcement owner

Axis 2 of the hygiene scan. Decidable only inside a naming context, so the
axis is defined as one; the bare-name-in-prose half is
`INV repository/hygiene-prose-account-name`.
