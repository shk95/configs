# Keep automation on the Windows implementation contract

date: 2026-09-26
scope: windows
status: accepted
reopen-when: a Windows implementation cannot preserve its evidence status when run directly by automation.

`windows/win-env.ps1` remains the domain's one operator entry point. Its forwarding, parameter binding and exit behavior are a public contract. Windows validation and tests also need an implementation contract independent of that entry point: local hooks and CI select checks as automated evidence, not as an operator command.

The validation and test scripts under `windows/tool/` return 0 for complete success, 69 when optional native tooling prevents a complete local check, and 1 when a check fails or complete native evidence is required. Native CI requires complete evidence and invokes the scripts directly. The entry point's own fixture continues to prove that an operator receives the implementation's status. A test executing the entry point is verification of its public contract, not an operational dependency on it.

The developer-tool setup script also runs directly in CI and returns 0 or fails. CI runs it in a child PowerShell process so a terminating error becomes a nonzero process status; that failure must stop the job.

Rejected: moving the operator entry point into the repository root or Unix-like Justfile. Windows must remain independently operable from a native host. Rejected: changing only the CI path strings without verifying direct invocation statuses and the operator contract.
