# Index the Git for Windows error from fetching a linked worktree by symptom

kind: addition
scope: repository
first-observed: 2026-09-05
target: docs/troubleshooting.md, a section keyed on the literal error text, pointing at CONTRIBUTING § Windows changes
promote-when: one more session meets the error after this record
drop-when: no new occurrence by 2027-03-05

## Observation

Fetching a branch into the Windows clone from a linked worktree's UNC path fails with "Please make sure you have the correct access rights and the repository exists" and "fatal: invalid reference", because the worktree's `.git` is a file whose `gitdir:` names a Linux path. The procedure is in CONTRIBUTING (PR #169); the symptom is not in the file whose job is symptoms, and an agent meeting the error searches that file.

## Evidence

- `CONTRIBUTING.md § Windows changes` (fetch from the main checkout, never a linked worktree).
- `grep -ni 'access rights\|invalid reference' docs/troubleshooting.md` is empty.

## Occurrences

- 2026-09-05: two sessions independently, the same day (one documented the procedure in #169, one hit it again while verifying #168).
