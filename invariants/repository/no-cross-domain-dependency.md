id: repository/no-cross-domain-dependency
statement: No domain's checks, tests or payloads read another domain's tree; similarity between independently owned copies is never a failure.
rationale: docs/architecture.md § Change and dependency rules
enforced-by: pending #124
owner: repository maintainer

Two violations are known: the Windows Pester suite byte-compares
`assets/wezterm/fonts.json`, and the Windows CI job parses
`assets/powershell/profile.ps1`. Both make a Unix-like edit fail Windows
evidence. The issue owns the fix; this entry owns the statement.
