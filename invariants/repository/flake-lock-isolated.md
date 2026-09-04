id: repository/flake-lock-isolated
statement: A dependency lock refresh is its own commit and touches nothing else.
rationale: docs/architecture.md § Version control and releases
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test

A lock refresh changes every derivation hash in the Unix-like domain; mixed
with a source change it hides which of the two moved an output.
