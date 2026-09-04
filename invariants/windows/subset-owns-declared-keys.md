id: windows/subset-owns-declared-keys
statement: A subset-compared file drifts only on a property its payload declares; whatever else the host keeps in that file is runtime and is never reported as drift.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/decisions/jsonsubset-captured-by-projection.md § A JsonSubset payload is captured by projection

A subset payload declares the keys it owns and tolerates every other key the
application keeps in the same file. Reporting an undeclared key as drift
would make every application write a drift; failing to report a declared
key's change would make the payload decorative. The fixture holds both
directions on the comparison function: a runtime property beside the
declared ones passes, a changed declared property fails. Capture relies on
the same rule from the other side, projecting the host's values onto the
declared shape.
