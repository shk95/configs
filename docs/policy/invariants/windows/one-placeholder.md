id: windows/one-placeholder
statement: Deployment expands exactly one content placeholder and capture restores exactly that one.
rationale: docs/policy/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
enforced-by: fixture windows/tests/Capture.Tests.ps1
decision: docs/policy/decisions/windows/capture-restores-one-placeholder.md § Capture restores exactly one placeholder

Deployment and capture share the single supported content token. Capture
restores its JSON-escaped spelling; other private values remain literal
host-owned data, without inventing additional tokens or claiming portability.
The supported token round-trips through deployment byte for byte.
