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
evidence. Documentation and release declarations retain the global policy checks
without selecting a provider suite independently. CI wiring exercises every
hosted lane. Repository Git for Windows fixtures, Windows desired state and
CI runtime-control fixtures are individually selected. Changes to the runtime
declaration, reader or controller can affect both Windows units. History
diagnostics require no dev ref and never fetch implicitly. Incoming source
ranges receive the same ownership audit in local delivery and CI.
