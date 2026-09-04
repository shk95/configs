id: windows/one-placeholder
statement: Deployment expands exactly one content placeholder and capture restores exactly that one.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

The placeholder is the only host-specific spelling a payload may carry.
Capture rewrites that spelling back to the placeholder and refuses every
other one rather than inventing a second placeholder, so a captured payload
round-trips through deployment byte for byte.
