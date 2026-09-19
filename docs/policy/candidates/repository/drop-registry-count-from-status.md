# The registry entry count in the status file rots

kind: deletion
scope: repository
first-observed: 2026-09-05
target: docs/status/repository.md, the sentence stating how many entries the registry holds
promote-when: the count is found stale once more after the 2026-09-05 correction
drop-when: the count is made a checked value

## Observation

`docs/status/repository.md` states the number of registry entries; nothing checks it, and it went stale the day after it was written (51 while the tree held 52, after PR #170 added an entry without updating it). `tool/version-control/invariants --table` prints the live count.

## Evidence

- `grep -c '^id: ' docs/policy/invariants/*/*.md` against the sentence.

## Occurrences

- 2026-09-05: stale by one after PR #170; corrected by the pull request that registers the next entry, which is the only kind of change that can keep it true.
