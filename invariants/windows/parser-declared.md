id: windows/parser-declared
statement: A managed file's parser names a validator the domain has, and an unknown value is refused at load.
rationale: docs/architecture.md § Windows domain
enforced-by: schema windows/src/WinEnv.psm1
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

The parser is validated against the declared list the way the comparison
mode is, so a misspelled or missing value names its entry while the manifest
loads. The validator's switch also has a default arm that refuses any name
outside its cases, because before #135 an unknown parser fell through and
the source counted as parsed: a silent acceptance, not a missing check. The
fixtures hold both refusals and accept each declared name.
