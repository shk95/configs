id: repository/no-cross-domain-dependency
statement: No domain's checks, tests or payloads read another domain's tree; similarity between independently owned copies is never a failure.
rationale: docs/architecture.md § Change and dependency rules
enforced-by: tool tool/version-control/domain-reads
enforced-by: fixture tool/version-control/test

Two violations were known: the Windows Pester suite byte-compared
`assets/wezterm/fonts.json`, and the Windows CI job parsed every PowerShell
file in the checkout, reaching `assets/powershell/profile.ps1`. Both made a
Unix-like edit fail Windows evidence. The Windows domain removed the first
from its own suite (`INV windows/no-unix-host-required`); the merge-gate job
dropped its parse loop, because `windows/tools/test.ps1` already parses the
Windows tree. The tool scans the code of each domain in the index — comments
stripped, payload trees excluded, since a payload reads nothing — for a path
that names the other domain's tree, and the fixture runs it over a throwaway
repository that reads across the boundary in each direction and over one
that only mentions the other tree in a comment (#124).
