# Terminal delegation is unverified below the documented boundary

date: 2026-08-30
scope: windows
status: accepted
issue: #53
issue: #54
source: 9f1e8ce:docs/status.md § Windows 10 support boundary

Windows 10 was two reported symptoms rather than a recorded boundary. A sweep
over three items of the manifest surface — the default terminal delegation
and the two `Appx` items — assigns each exactly one of the evidence states
defined in `docs/architecture.md`. All three are unverified on Windows 10,
for two different reasons.

The default terminal delegation is a read-back, not a behavior
check. `Set-WinEnvTerminalDelegation` writes `DelegationTerminal`
and `DelegationConsole` under `HKCU:\Console\%%Startup`, and
`Test-WinEnvTerminalDelegation` reads those two values back from the same key
and compares them to `manifest.Terminal`. Microsoft states the condition under
which the setting is supported: the default terminal application requires
Windows 11 22H2, or Windows 10 22H2 at OS build 19045.3031 with KB5026435,
and Windows Terminal 1.17 or later. The same document names this key, these
two value names, and the two GUIDs this manifest carries for Windows Terminal,
so the values written here are the documented ones. The boundary is therefore
an OS build plus an application version, not a Windows release name. Below
either half of it the host accepts the write, the read-back passes, and the
setting is ignored: `-Check` exits 0 and never reports drift for a setting that
does nothing. That false pass is the one outcome the evidence contract has no
room for, and deciding the item against the documented condition rather than
against the write (#53) is the fix. Above the boundary the read-back still
observes no handoff. No Windows 10 host at build 19045.3031 was available,
so the item is recorded unverified against its documentary source rather
than closed as works.

2026-09-04: `-Check` returns 69 for an undecidable item and for a missing
prerequisite (`docs/decisions/drift-outranks-unverified.md`); #54 remains
open for the terminal item's own conversion.

2026-09-05: `-Check` decides the item against the condition (#53, #54).
`Test-WinEnvTerminalDelegation` answers two things apart: `Matches`, the
read-back, and `Unverified`, the boundary. The build comes from
`Get-WinEnvWindowsBuild`; at build 19045 only, the revision comes from the
registry's `UBR`, because the documented condition names it (KB5026435 is
19045.3031) and no other build needs it, which is why this differs from the
`.wslconfig` bound that is stated in builds alone; the Windows Terminal
version comes through the same Appx route the package detection uses, so a
host whose module will not load reports the item undecided rather than
passing. Below the boundary a matching read-back is unverified, and a
mismatch is drift on either side, since Apply writes the values regardless.
Observed the same day on the maintainer's host, Windows 10 21H2 build
19044.7663 under PowerShell 7.6.5 with every feature selected: `-Check`
named the item "default terminal delegation: Windows build 19044 is below
the documented boundary" under its undecided detections, beside the Appx
route's, and exited 2 for an unrelated `windowsTerminal settings` drift, so
the 69 itself was not observable there (`drift-outranks-unverified.md`).
The native Pester suite passed (219, 11 skipped) and
`check-desired-state.ps1` was valid. A host at or above 19045.3031 has not
been observed; the issue's upper-side evidence is still owed.
