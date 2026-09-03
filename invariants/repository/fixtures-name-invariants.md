id: repository/fixtures-name-invariants
statement: Every fixture unit names an invariant it proves, and a unit that proves none is removed.
rationale: AGENTS.md § Governance design
enforced-by: tool tool/version-control/invariants
enforced-by: fixture tool/version-control/test
decision: docs/status.md § Invariant registry
owner: repository maintainer

Report mode until the Unix-like and Windows migrations have mapped their
suites; the flip to enforcement is recorded in the decision section.
