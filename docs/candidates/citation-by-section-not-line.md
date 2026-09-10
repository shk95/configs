# A citation into a living document names a section, not a line number

kind: addition
scope: repository
first-observed: 2026-09-10
target: AGENTS.md § Governance design (one sentence); a check beside tool/version-control/invariants
promote-when: a third line-number citation appears, or the citation forms are edited anyway
drop-when: no new occurrence by 2027-03-10

## Observation

Every citation form this repository uses was swept and compared. The forms
that resolve through a checked identifier or a path have not drifted; the
form that names a line number had drifted in every instance, including one
that a tool prints to the operator. The difference is not care taken by the
author: it is whether anything can tell that the citation stopped resolving.

## Evidence

- `INV <scope>/<slug>` and `PROV <scope>/<slug>`, 53 occurrences, 0 broken;
  `tool/version-control/invariants` checks both directions on every commit.
- `docs/decisions/…` and `docs/candidates/…` path citations, 28 unique, 0
  broken, with no checker at all.
- `AGENTS.md line 93` (3 occurrences) and `AGENTS.md line 127` (1), 4 of 4
  broken on 2026-09-10: the first sentence had moved to line 104 and the
  second into the `Rules that are expensive to break` table. One of the four
  was the refusal `tool/version-control/commit` prints when it declines a
  hook bypass, so the operator was shown a citation that resolved to an
  unrelated bullet.
- The `§` form the fix uses is not new here: `invariants/*` entries already
  spell `decision: docs/decisions/<slug>.md § <Section>`, and a candidate's
  own `target:` key uses it.

## Occurrences

- 2026-09-10: four broken citations corrected in place; the correction did
  not wait for this candidate, per `docs/candidates/README.md` ("the
  correction of tracked text that is false today").
