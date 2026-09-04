id: windows/hash-covers-selection
statement: The desired-state hash covers the manifest, the selected features, and every variant of a selected file, and nothing a host did not select.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

A whole-tree hash reported drift for payloads a host never deploys and
forced an Apply that could change nothing; a host-resolved hash would let
the desired state depend on the host. The fixtures show a changed excluded
payload leaves the hash alone, a changed selected one moves it, an
unresolved variant moves it, and a changed manifest moves it with every
payload held still.
