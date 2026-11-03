id: repository/local-gate-selects-by-effect
statement: Gates select checks by change effect independently of ownership, with conservative coverage for executable inputs and failure on unknown CI inputs.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/dispatch/select
enforced-by: tool tool/dispatch/ci-base
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/local-gate-selects-by-effect.md § The local gate selects checks by effect

Commit uses fast staged checks. Tracked workflow checks and CI select affected
suites through the same dispatcher. Pre-push reads transmitted history and
tags only; native/fixture execution never depends on an unrelated checkout.
Master push and optional topic PR CI fail unknown inputs and missing selected
evidence. Document-only changes select no platform suite; global index scans
remain required. Known Windows runtime wiring selects the native Windows suite.
History diagnostics require no dev ref and never fetch implicitly.
Incoming source ranges receive the same per-commit ownership audit in local
delivery and CI. Windows runtime-governance inputs add a native proof-only
unit; ordinary local Windows domain tests do not certify CI runtime wiring.
