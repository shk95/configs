# Undecidable Appx detection is unverified, not absent

date: 2026-08-30
scope: windows
status: accepted
issue: #37
issue: #38
source: 9f1e8ce:docs/status.md § Windows 10 support boundary
source: 9f1e8ce:docs/status.md § Check evidence states

The two `Appx` items are supported on Windows 10 and undetectable there by the
route this domain uses. Those are different statements and the record keeps them
apart. PowerToys, which contains Command Palette, requires Windows 11 or Windows
10 version 2004 (20H1, build 19041) or newer; Windows Terminal requires Windows
10 2004 (build 19041) or later. Both therefore run on a supported Windows 10
host, and neither item is absent or unsupported there. What does not work is the
question. `Get-AppxPackage` backs both the `powertoys` feature's
`Microsoft.CommandPalette` precondition and the `Microsoft.WindowsTerminal`
package's `Appx` detection, and Microsoft's Windows module compatibility table
footnotes `Appx` with "Must use Compatibility Layer with PowerShell 7.1". This
domain runs PowerShell 7 and both call sites pass `-ErrorAction
SilentlyContinue`, so a route that cannot answer returns nothing and is read as
absence. The precondition then reports the package missing and Apply refuses the
feature; the package either reports missing, so Apply reinstalls an installed
Windows Terminal, or disagrees with the WinGet registration and reports a
detection conflict that blocks Apply. An unavailable route must report
unverified, never absence.

2026-08-30: `setup.ps1` reports the undecidable case as unverified (#37 closed).

Windows version detection (#38) owns the mechanism the delegation condition
needs, and this record builds none of its own. That mechanism now exists as
`Get-WinEnvWindowsBuild`
(`docs/decisions/wslconfig-selected-by-windows-build.md`); #53 decides the
delegation item against it.

The sweep is deliberately narrow and its edge is part of the record. It did not
examine the `WinGet` and `Command` detections, the font download and its
registry registration, the PowerToys lifecycle, the managed-file targets and
their packaged `LocalState` paths, an unpackaged Windows Terminal installation,
or PowerShell 7 itself
(`docs/decisions/wslconfig-selected-by-windows-build.md`). Windows releases
older than 10, Windows Server, and non-x64 hosts stay out of scope. Those items
are not known to be safe on Windows 10; they are unexamined.

One Windows 10 sub-case survives that, and it is not Appx silence read as
absence. When the module cannot answer, package detection keeps the WinGet
registration as its answer, so a package WinGet's configured source does not
report is still recorded missing — the same claim a `WinGet`-detected package
already makes, drawn from a route that did answer. A Store-installed Windows
Terminal reaches it. Apply then attempts an install, and `Install-WinEnvPackage`
accepts WinGet's documented "no applicable update" status as success so a run is
not aborted mid-deployment over a package that is present; post-apply validation
still asks the same undecidable question and refuses to record state. Deciding
that item needs detection independent of the registration query, which belongs
with the general unverified state rather than with the Appx route.
