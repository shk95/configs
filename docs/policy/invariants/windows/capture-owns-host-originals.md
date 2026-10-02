id: windows/capture-owns-host-originals
statement: Capture observes only explicitly selected and enabled supported units, previews host originals and saves them only explicitly with chosen-source projection, refuses changed identities and conflicting pending documents, reports recoverable per-file outcomes, and never writes provider source, generated bundles, app state or Git history.
rationale: AGENTS.md § Goal and authority
enforced-by: schema windows/src/WinEnvCapture.psm1
enforced-by: fixture windows/tests/Capture.Tests.ps1
decision: docs/policy/decisions/windows/host-capture-owns-originals.md § Capture saves explicit host originals
