# A code comment carries durable rationale that no registry or record holds

kind: addition
scope: repository
first-observed: 2026-09-10
target: AGENTS.md § Governance design (the authority list, which does not mention comments)
promote-when: a second comment is found asserting a rule or a record that exists nowhere else
drop-when: no new occurrence by 2027-03-10

## Observation

`AGENTS.md § Governance design` places durable rationale, invariants,
procedure, orchestration, enforcement, current state and observations, and
says each obligation has one authoritative source. Comments appear in none of
those places, yet the longest prose in the tree sits in file headers, and at
least one of them holds a decision recorded nowhere else while citing a
record that does not exist.

## Evidence

- `modules/flake/module-classes.nix` explains why this repository stores
  module classes in a self-declared option rather than the pattern's usual
  `flake.modules.<class>.<name>`, which is a durable decision with no record
  under `docs/decisions/`. The same comment asserted the repository "has it
  recorded as a cost"; the phrase `unknown flake output` appears nowhere else
  in the tree, so the record it cited did not exist. The unbacked half of the
  sentence was removed on 2026-09-10; the decision it explains is still
  unrecorded.
- Header comments of comparable length carrying rationale rather than
  implementation notes: `tool/version-control/commit`,
  `tool/darwin/karabiner`, `tool/version-control/domain-reads`,
  `modules/flake/module-classes.nix`.

## Occurrences

- 2026-09-10: one comment found asserting a record that does not exist.
