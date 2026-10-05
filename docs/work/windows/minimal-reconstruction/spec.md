# Recover Windows host features
kind: spec
date: 2026-10-05
scope: windows
status: approved
review-by: 2026-10-20

## Implementation

Load the domain-owned runtime contract, generate explicitly selected host desired state and capture complete host-owned originals. Capture performs no provider publication. Repository-owned CI consumes the Windows runtime declaration through its own scope.

Native Windows CI is the gate for Windows behavior; macOS PowerShell evidence is not a substitute. Existing external profile blocks remain intact. Apply and host adoption are outside scope. Repository orchestration is linked from the repository minimal-reconstruction spec.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Windows independently loads its runtime contract and generates selected host-owned desired state. | fixtures, native runtime |
| AC2 | Capture produces supported host originals and regenerates them without provider publication. | fixtures, native runtime |
