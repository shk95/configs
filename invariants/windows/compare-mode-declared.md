id: windows/compare-mode-declared
statement: A managed file's comparison mode is one the domain declares, and a mode with a parser precondition is refused on any other parser.
rationale: docs/architecture.md § Windows domain
enforced-by: schema windows/src/WinEnv.psm1
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

A misspelled mode would reach a host and fail there as unknown with the file
already written, so the loader validates it against the declared list. The
generated-profiles mode reads both sides as JSON, so it is refused on any
entry whose parser is not JSON.
