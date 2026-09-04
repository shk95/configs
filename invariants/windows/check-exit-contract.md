id: windows/check-exit-contract
statement: A read-only check returns 0 when converged, 2 when anything drifted, the unverified status only when its sole open question or a missing prerequisite could not be decided on the host, and a failure in place of unverified when native evidence is required.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/status.md § Check evidence states

The ranking is a decision, not a derivation: drift is the actionable half of
"is an Apply needed", so a known 2 never collapses into a 69. The fixtures
hold the ranking function to all four outcomes and run the real entry point
in a child shell with no prerequisites reachable, so the process exit code,
not only the function, is what is proved. The entry-point scripts are not
declared as tool locators because the repository tracks them without the
executable bit; each carries the tag as a comment beside the code that decides its exit,
for the reader.
