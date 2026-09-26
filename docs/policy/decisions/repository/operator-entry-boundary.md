# Separate operator and automation dependencies

date: 2026-09-26
scope: repository
status: accepted
reopen-when: a repository operation cannot be exposed without duplicating its implementation policy, or an automation caller needs the operator interface's presentation as part of its contract.

Repository operations had no single operator interface: clone setup, worktree management, commit assistance, audits and planning were documented as separate scripts. Hooks and CI correctly called the implementation scripts, but the user-facing list was indistinguishable from the implementation tree. Windows had a domain entry point, yet CI and pre-push also called it for operational work.

The repository provides one small operator entry point. It selects known commands and forwards their arguments and exit status to the existing scripts. Hooks, CI and implementation scripts depend on internal tools instead. A test may call an entry point to prove the public contract. An agent performing a person's command may use the entry point. Domain host operations stay at their domain entry points; repository governance does not compose deployment.

The domain `tool/` trees remain their implementation boundaries. A user-only operation still has an internal implementation when its entry point calls it. The Unix-like `Justfile` remains the current human interface, including refusal recipes retained for compatibility; moving it is a separate decision. Windows keeps `windows/win-env.ps1` as its one human interface and verifies its forwarding contract separately.

Rejected: a shared root command for Windows and Unix-like host operations, because it would create a repository-owned deployment path across the domain boundary. Rejected: moving every implementation file under new `system/` directories, because the existing `tool/` paths already express ownership and the move would churn enforcement locators without changing dependencies.
