# Keep Windows operator and automation commands separate
kind: spec
date: 2026-09-26
scope: windows
status: approved
review-by: 2026-10-26
issue: #404

Windows already has one operator entry point, `windows/win-env.ps1`, and implementation scripts under `windows/tool/`. Repository automation currently invokes the operator entry point. Verify that the internal scripts stand alone before automation moves to them.

## Decisions

Keep `windows/win-env.ps1` as the Windows operator interface and `windows/tool/` as the internal implementation location. Verify direct invocation under native PowerShell, including success, unavailable and failure results. Preserve the entry point's own forwarding contract and its ability to bootstrap a host with Windows PowerShell 5.1.

Rejected: putting Windows verbs in the root repository or Unix-like `Justfile`; that would couple deployment to another scope. Rejected: relying on a path substitution in CI without checking direct execution behavior.

## Increments

1. Windows fixtures and native runtime checks verify direct internal script execution and the public entry point contract.
2. Review verifies Windows documentation and the scope boundary after the repository automation routing change.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The Windows internal validation and test scripts return their documented success, unavailable and failure statuses when executed directly, including under required-native mode. | fixtures, native runtime |
| AC2 | The Windows public entry point still forwards commands and statuses, and its documented usage does not expose internal scripts as the normal operator interface. | fixtures, review |
