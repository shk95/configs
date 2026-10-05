# Recover Windows host features
kind: spec
date: 2026-10-05
scope: windows
status: approved
review-by: 2026-10-20

## Implementation

Recover runtime from bbfbe4a/df294c9, W1 from e2005e4/af8732f/d5c1ae7 and W2 from e2c1cc7/67f5065 as needed. Bring the native CI runtime support through the repository scope. Keep generation/capture tests and supported usage, not the old operating controller.

Native Windows CI is the gate for Windows behavior; macOS PowerShell evidence is not a substitute. Existing external profile blocks remain intact. Apply and host adoption are outside scope. Repository orchestration is linked from the repository minimal-reconstruction spec.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Windows independently loads its runtime contract and generates selected host-owned desired state. | fixtures, native runtime |
| AC2 | Capture produces supported host originals and regenerates them without provider publication. | fixtures, native runtime |
