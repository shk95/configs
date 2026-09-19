# A registry entry's rationale section is read to confirm it justifies the statement

kind: addition
scope: repository
first-observed: 2026-09-05
target: docs/policy/definition-of-done/repository.md § Every change, the bullet on registry entries (add: and the cited rationale section was read to confirm it justifies the statement); then per-scope re-fits of the entries listed below
promote-when: a third entry is registered against a section that does not mention its subject, or the definition of done is edited anyway
drop-when: no new occurrence by 2027-03-05

## Observation

`tool/version-control/invariants` verifies that the cited heading exists (C4) and that the file is one of the two permitted (C9); nothing reads the section. Entries whose cited section never mentions their subject exist today: `docs/policy/invariants/unixlike/generated-config-key-in-schema.md` cites § Unix-like domain, which never mentions a pinned tool or a generated configuration (registered by #169 on the day this was first found); `docs/policy/invariants/repository/msys-argument-guard.md` cites § Repository governance plane, which never mentions MSYS or Git for Windows; `docs/policy/invariants/windows/capture-publishes-through-dev.md` cites § Version control and releases, a governance-plane section, for a Windows rule; `docs/policy/invariants/unixlike/composition-in-one-place.md` cites AGENTS.md § Goal and authority while § Unix-like domain carries the whole statement. The definition of done asks that the tagged fixture be read; not the rationale.

## Evidence

- `tool/version-control/invariants`, rules C4 and C9; `CONTRIBUTING.md § Add or change an invariant`, step 3 ("write that section first").
- `grep -ci pinned docs/policy/architecture.md` is 0; `grep -ci msys docs/policy/architecture.md` is 0.

## Occurrences

- 2026-09-05: the entry-point entry cited AGENTS.md § Governance design and was re-pointed after the branch review (c2e7f88).
- 2026-09-05: #169 registered `generated-config-key-in-schema` against a section that does not mention its subject.
