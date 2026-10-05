# CI runtime is Windows-owned verification data
date: 2026-10-05
scope: windows
status: accepted
source: docs/work/windows/minimal-reconstruction/spec.md § Implementation

Declare the exact management verification runtime and its official immutable
artifact/hash in the Windows domain, separately from inbox Windows PowerShell
entry/bootstrap coverage. A versioned read-only reader refuses malformed or
unknown contracts before automation consumes them. The initial management
verification baseline is PowerShell 7.6.6 x64; bootstrap coverage remains the
inbox Windows PowerShell 5.1 x64 engine.

Repository CI wiring consumes this declaration rather than owning a second
platform-version choice. The declaration does not install anything, enforce
the current process version or change the minimum runtime of consumer hosts.
Its publication is not evidence that CI already runs the chosen version.
A separate repository change supplies that wiring and actual-version proof.
The upstream Windows x64 ZIP and hash were checked against the official
PowerShell v7.6.6 release on 2026-09-30.

This small prerequisite avoids requiring a not-yet-installed exact runtime
in the CI job that must first admit its version-selection interface.
