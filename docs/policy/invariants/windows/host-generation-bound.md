id: windows/host-generation-bound
statement: Explicit versioned host declarations select one complete supported source per managed unit, materialize only the selected dependency closure with exact provider and input identities, refuse stale or incompatible generations before reconciliation writes, preserve unmanaged application state, and distinguish success from partial failed generation attempts.
rationale: docs/policy/architecture.md § Windows domain
enforced-by: schema windows/src/WinEnvGeneration.psm1
enforced-by: schema windows/src/WinEnv.psm1
enforced-by: fixture windows/tests/Generation.Tests.ps1
decision: docs/policy/decisions/windows/host-generation-owns-selection.md § Host declarations own selection and complete unit sources
