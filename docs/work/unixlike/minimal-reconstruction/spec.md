# Recover Unix-like provider features
kind: spec
date: 2026-10-05
scope: unixlike
status: approved
review-by: 2026-10-20

## Implementation

Provide typed external constructors, independent WSL/graphical selection and native host overrides. Capture previews and explicitly saves host-owned settings. Local refresh changes only selected inputs and the lock. Independent checks execute once. Preserve the dependency lock commit boundary.

Required evidence is limited to provider fixtures, external consumer evaluation and selected matching-system builds, capture/refresh refusal cases and changed CI calls. Personal host combinations and activation are outside scope. Repository orchestration is linked from the repository minimal-reconstruction spec. Report unavailable native evidence honestly.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | External consumers use typed constructors and host-owned overrides. | evaluation, build |
| AC2 | Supported Darwin capture writes host originals and preserves the retired publication boundary. | fixtures, evaluation |
| AC3 | Local refresh preserves source bytes/modes and bounds changes to selected inputs and the lock. | fixtures |
| AC4 | Independent suites execute once while coverage fixtures exercise the evaluation/build core. | fixtures |
