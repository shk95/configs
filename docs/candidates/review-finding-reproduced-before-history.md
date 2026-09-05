# A review finding is reproduced in its framework before it is written into history

kind: addition
scope: repository
first-observed: 2026-09-05
target: docs/definition-of-done.md § Every change (an evidence item with an owner); optionally the Prepare step of the version-control skill
promote-when: a second finding reaches a commit message, record or issue without in-situ reproduction, or the definition of done is edited anyway
drop-when: no new occurrence by 2027-03-05

## Observation

A plan reviewer reproduced a `$LASTEXITCODE` leak with a bare script and concluded that `windows/tools/test.ps1` would return 69 through the entry point. The claim went into a code comment, a decision record, a commit message and an issue comment before the whole-branch review probed the case inside Pester and found it false: Pester keeps an `It`'s child processes out of the runner's scope. `docs/definition-of-done.md` names no reviewer and no standard for a finding entering history, while `invariants/README.md` and `docs/architecture.md` cite it as the reviewer's authority.

## Evidence

- `git show c2e7f88` withdraws the claim; #168 carries the correction.
- `grep -ci review docs/definition-of-done.md` is 0; `invariants/README.md` ("the reviewer's to confirm; `docs/definition-of-done.md` says so").

## Occurrences

- 2026-09-05: #168 / PR #170, one false finding propagated to four surfaces.
