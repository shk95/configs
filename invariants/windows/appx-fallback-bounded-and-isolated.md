id: windows/appx-fallback-bounded-and-isolated
statement: After the default Appx route fails, package presence and version detection makes at most one same-user query through the inbox Windows PowerShell 5.1 executable, bounds and cleans up that isolated process, accepts only a matching validated UTF-8 JSON result, and otherwise leaves the Appx observation undecidable.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/decisions/appx-detection-unverified-not-absent.md § Undecidable Appx detection is unverified, not absent

The fallback is a capability route, not a second management runtime. The
PowerShell 7 query remains first and an empty successful query remains package
absence. Only a failed route starts the child, and no Windows version or
localized error text selects it. The package name crosses stdin as data, while
the child carries only the checked-in Appx payload and returns the requested
name, presence and first package version. A launch failure, timeout, nonzero
exit, stderr, invalid UTF-8, malformed or unexpected JSON, mismatched name or
invalid field leaves both presence and version unknown. The child inherits the
caller's user and privilege level, uses no profile, no interactive input and no
`-AllUsers`, and is killed and disposed when its bound expires.
