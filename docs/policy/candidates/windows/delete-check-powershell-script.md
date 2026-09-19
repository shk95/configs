# windows/tools/check-powershell.ps1 is referenced by nothing

kind: deletion
scope: windows
first-observed: 2026-09-05
target: windows/tools/check-powershell.ps1
promote-when: it is still unreferenced when the next change touches windows/tools/
drop-when: a caller appears

## Observation

A one-file parser wrapper that `tools/test.ps1` superseded with its own parse loop. Nothing under the tree names it; it ends without an explicit `exit`, and it sits where the next author would wire it into the verb table.

## Evidence

- `git grep -n check-powershell` returns only the file itself.

## Occurrences

- 2026-09-05: observed by two audits.
