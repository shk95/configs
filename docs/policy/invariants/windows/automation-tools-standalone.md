id: windows/automation-tools-standalone
statement: The Windows validation and test implementations preserve success, unavailable and required-native failure results when automation runs them directly, independently of the operator entry point.
rationale: docs/policy/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/policy/decisions/windows/automation-uses-internal-tools.md § Keep automation on the Windows implementation contract

The native Windows CI job runs both implementation scripts directly under PowerShell 7 and requires complete evidence. The fixture hides optional tools from child processes and checks both unverified and required-native failure statuses. The entry point's separate fixture keeps its forwarding contract.
