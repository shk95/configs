id: repository/fixtures-name-invariants
statement: Every fixture unit names an invariant it proves, and a unit that proves none is removed.
rationale: AGENTS.md § Governance design
enforced-by: tool tool/version-control/invariants
enforced-by: fixture tool/version-control/test
decision: docs/status.md § Invariant registry
owner: repository maintainer

Enforced since 2026-09-04, when the Unix-like and Windows migrations and the
two pruning changes had mapped every suite; the decision section records the
flip. `INVARIANTS_ENFORCE_C10=0` restores the report mode for a local
survey and is never set by a hook or in CI.
