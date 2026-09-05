# The sentence that CI and the hooks call the Windows scripts directly

kind: deletion
scope: repository
first-observed: 2026-09-05
target: README.md § Windows and CONTRIBUTING.md § Windows changes, the sentence "CI and the hooks call the scripts under windows\tools\ directly"
promote-when: the candidate ci-windows-checks-through-the-entry-point is promoted
drop-when: that candidate is dropped

## Observation

True today and tied to a candidate: if CI is routed through the entry point the sentence becomes false, and it is the kind of operational detail that goes stale silently.

## Evidence

- `README.md § Windows`; `CONTRIBUTING.md § Windows changes`.

## Occurrences

- 2026-09-05: recorded with its sibling candidate.
