id: windows/schema-version-refused
statement: An unsupported manifest or state schema is refused before any comparison.
rationale: docs/architecture.md § Windows domain
enforced-by: schema windows/src/WinEnv.psm1
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

A manifest paired with an older module would otherwise load and then fail
at comparison time as an unknown mode or a missing key, on a host, with a
message about the wrong thing. Both loaders check the schema number first
and say so; the fixtures hold the message to the tag so a refusal for any
other reason cannot pass for this one.
