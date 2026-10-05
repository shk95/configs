id: repository/flake-lock-isolated
statement: A dependency lock refresh is its own commit and may carry only its Unix-like release declaration alongside the lock.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test

A lock refresh changes every derivation hash in the Unix-like domain; mixed
with a source change it hides which of the two moved an output.

The automatic patch declaration is publication input, not a configuration
implementation change. The bounded release writer validates its fixed content.
