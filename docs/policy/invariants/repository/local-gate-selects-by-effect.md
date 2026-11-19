id: repository/local-gate-selects-by-effect
statement: Gates select checks by change effect independently of ownership, with conservative coverage for executable inputs and failure on unknown CI inputs.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/dispatch/select
enforced-by: tool tool/dispatch/ci-base
enforced-by: fixture tool/version-control/test
enforced-by: fixture tool/version-control/test-mechanics.py
decision: docs/policy/decisions/repository/local-gate-selects-by-effect.md § The local gate selects checks by effect

Commit uses fast staged checks. Tracked workflow checks and CI select affected
suites through the same dispatcher. Pre-push reads transmitted history and tags
only. Native and fixture checks use the candidate checkout.
Master push and optional topic PR CI fail unknown inputs and missing selected
evidence. Application settings use the owning platform suite in CI and retain
focused checks for local feedback.
Documentation edits, including the repository's root guides, and release
declarations receive incoming policy checks. Changes to the CI definition
exercise the platform contracts and routing fixtures. Unix-like development-tool
fixtures follow their own inputs independently of provider lock updates,
including evaluation-tool and prerequisite fixtures. Repository Git for Windows
fixtures, Windows desired state and CI runtime-control fixtures are individually
selected. Changes to the runtime declaration, reader or controller can affect
both Windows units. History
diagnostics require no dev ref and never fetch implicitly. Incoming source
ranges receive the same ownership audit in local delivery and CI.
