# Recover Unix-like provider features
kind: spec
date: 2026-10-05
scope: unixlike
status: approved
review-by: 2026-10-20

## Implementation

Recover U1 from 50444ef/a69dd58/0530f7c, local refresh from 4497764/bb67173, and U2 from 26b6d39/66ab190/e71ed4a with the needed fixes and contracts. Preserve the dependency lock commit boundary. Keep donor runtime/tests/current usage, not their large work documents.

Required evidence is limited to provider fixtures, external consumer evaluation and selected matching-system builds, capture/refresh refusal cases and changed CI calls. Personal host combinations and activation are outside scope. Repository orchestration is linked from the repository minimal-reconstruction spec. Report unavailable native evidence honestly.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | External consumers use typed constructors and host-owned overrides. | evaluation, build |
| AC2 | Supported Darwin capture writes host originals and preserves the retired publication boundary. | fixtures, evaluation |
| AC3 | Local refresh preserves source bytes/modes and bounds changes to selected inputs and the lock. | fixtures |
| AC4 | Independent suites execute once while coverage fixtures exercise the evaluation/build core. | fixtures |
