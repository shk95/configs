# Windows tool cleanup

kind: spec
date: 2026-09-25
scope: windows
status: approved
review-by: 2026-10-25
issue: #395

Give the Windows domain a singular `tool/` directory like the other domains,
remove a script with no caller, and correct the Windows-owned checks and
documentation that still describe old paths or old Unix-like layout.

## Decisions

Rename `windows/tools/` to `windows/tool/` and update the public entry
point's private target path, help, script examples, capture output, and
Windows tests together. Keep `windows/win-env.ps1` as the public interface.
Remove `check-powershell.ps1`, whose deletion candidate records no caller.
Retire that candidate when the deletion is verified.

Update the Windows tree-isolation fixture to cover the current Unix-like
tree, including `unixlike/payloads.json` and `unixlike/tool/install-plan`,
and keep negative fixtures for the paths it must refuse. Revise current
Windows status, invariants and definition of done where the old path is
present. Preserve historical decision records and dated observations.

## Increment

The Windows PR carries the directory, callers, fixtures, current documents
and report together. Its local evaluation and fixtures provide early evidence;
the native Windows CI job and review finish the report in the same PR.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The public Windows verbs reach the renamed tool directory, keep their exit-status contract, and all current help, capture output and tests use the new path. | evaluation, native runtime |
| AC2 | The unused parser wrapper and its candidate are removed, while Windows tree isolation refuses current Unix-like files and accepts Windows-owned files. | fixtures, native runtime |
| AC3 | Windows current-state documentation and invariant explanations describe the resulting interface and preserve historical records. | review |

## Evidence boundary

This change does not alter Windows desired host state. A read-only validate
and Pester run are required; Windows Apply is not authorized or needed.
