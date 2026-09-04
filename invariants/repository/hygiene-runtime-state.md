id: repository/hygiene-runtime-state
statement: Runtime state is observed, never committed; a tracked path that an ignore rule covers is runtime state that escaped the ignore file.
rationale: docs/architecture.md § Desired-state hygiene
enforced-by: tool tool/version-control/hygiene
enforced-by: fixture tool/version-control/test
decision: docs/decisions/hygiene-tool-owns-enforcement.md § The hygiene tool owns desired-state hygiene

Axis 3 of the hygiene scan, plus a basename denylist for artefacts no ignore
rule covers.
