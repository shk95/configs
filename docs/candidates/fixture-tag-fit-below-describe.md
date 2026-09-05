# Fixture tags are checked at Describe granularity; several tags name invariants their case cannot fail on

kind: addition
scope: windows
first-observed: 2026-09-05
target: windows/tests/WinEnv.Tests.ps1 (retag or untag the cases below); invariants/README.md § Fixture units name invariants (a negative case that proves the scanner is not tagged with the statement's id); tool/version-control/test (the 1,081 lines before its first banner hold 13 tags in no unit, a known limit in docs/decisions/fixture-tags-name-proven-invariants.md with no issue or owner)
promote-when: a tagged case is found passing on a violation of its statement during any other change, or the suite is reorganised anyway
drop-when: no new occurrence by 2027-03-05

## Observation

C10 treats a top-level `Describe` as the unit and C5 searches the whole file for the tag, so a case's fit with the statement it names is checked by nobody. Verified samples: the case at the top of `Describe 'win-env manifest'` pins `SchemaVersion` to 4 under `schema-version-refused` (a legitimate bump fails it, an accepted unsupported schema does not); a case in `Describe 'terminal delegation boundary'` asserts delegation matching under `check-exit-contract` and computes no status. The entry-point fixture added by #170 asserts a verb count of 7 and a terminal `exit`, which its statement does not name. The format contract's "positive and negative case" and the tag rule pull in opposite directions for scanner-enforced invariants.

## Evidence

- `tool/version-control/invariants` C5 and C10; `docs/decisions/fixture-tags-name-proven-invariants.md` ("Known limit").
- `grep -n -m1 '^# ----' tool/version-control/test` is line 1082; 13 `INV` tags precede it.

## Occurrences

- 2026-09-05: audit after #170; samples verified by the controller.
