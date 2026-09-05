id: windows/pre-bootstrap-shell-compatible
statement: Every Windows script that can run before the domain installs its own shell parses and runs under the shell the host already ships.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

Two scripts can run before pwsh 7 exists on a host: `tools/bootstrap.ps1`,
which installs it, and `win-env.ps1`, which stands in front of bootstrap for
`apply` and `check`. Both therefore carry no `#Requires`, import no module
and use only syntax Windows PowerShell 5.1 accepts. Nothing else asks the
older shell anything: the domain's parse gate runs under whichever shell
runs the suite, which is pwsh 7 on every development host and in CI, so a
newer-only operator in either script would pass every gate and fail on the
one host class bootstrap exists for. The fixtures hold the rule from both
sides: on any host, neither script declares a required version and both
parse; on a Windows host, `help` exits 0 and `check` exits 69 under the
older shell with no prerequisite reachable, and a script carrying a
newer-only operator is refused by that shell. The module's elevated
PowerToys stop also runs under the older shell, as an encoded script inside
the module; it is not held here.
