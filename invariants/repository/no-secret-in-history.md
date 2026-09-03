id: repository/no-secret-in-history
statement: Committed content carries no credential, and the staged state is scanned before it becomes history.
rationale: docs/architecture.md § Desired-state hygiene
enforced-by: tool .githooks/pre-commit
enforced-by: fixture tool/version-control/test

The secret scan owns detection; the hygiene scan deliberately does not
duplicate it. The hook runs the scanner on the staged state and CI runs it
on history. The fixture proves the hook's wiring — that a scanner refusal
blocks the commit — with a stand-in scanner; what counts as a secret is the
scanner's rule set, not this repository's.
