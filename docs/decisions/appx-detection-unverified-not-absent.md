# Undecidable Appx detection is unverified, not absent

date: 2026-08-30
scope: windows
status: accepted
issue: #37
issue: #38
issue: #207
source: 9f1e8ce:docs/status.md § Windows 10 support boundary
source: 9f1e8ce:docs/status.md § Check evidence states

Before #207, the two `Appx` items were supported on Windows 10 and undetectable
there by the only route this domain used. Those are different statements and
the record keeps them apart. PowerToys, which contains Command Palette,
requires Windows 11 or Windows 10 version 2004 (20H1, build 19041) or newer;
Windows Terminal requires Windows 10 2004 (build 19041) or later. Both
therefore run on a supported Windows 10 host, and neither item is absent or
unsupported there. What does not work is the question. `Get-AppxPackage`
backs both the `powertoys` feature's
`Microsoft.CommandPalette` precondition and the `Microsoft.WindowsTerminal`
package's `Appx` detection, and Microsoft's Windows module compatibility table
footnotes `Appx` with "Must use Compatibility Layer with PowerShell 7.1". The
domain ran PowerShell 7 and both call sites passed `-ErrorAction
SilentlyContinue`, so a route that could not answer returned nothing and was
read as absence. The precondition then reports the package missing and Apply refuses the
feature; the package either reports missing, so Apply reinstalls an installed
Windows Terminal, or disagrees with the WinGet registration and reports a
detection conflict that blocks Apply. An unavailable route must report
unverified, never absence.

Declining `terminal` and `powertoys` at selection time removes all three items
from a host's check: `setup.ps1` evaluates the delegation only when `terminal`
is selected and a feature's preconditions only when that feature is selected,
so `-Minimal` reaches none of them. That is a mitigation available today rather
than a fix, and a `-Minimal` run is evidence for none of these three items.

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

2026-09-08: the accepted independent detection is one capability fallback
behind the shared default query. PowerShell 7 remains first and uses
terminating errors, so a successful empty query is absence and bypasses the
fallback while any failed query discards partial output. A failure starts one
same-user Windows PowerShell 5.1 child from the inbox system path, with no
profile, interaction, elevation or `-AllUsers`; the package name is JSON data
on UTF-8 stdin rather than interpolated code. The child returns a versioned
record containing the matching name, presence and first package version. The
parent drains stdout and stderr together, stops and disposes the process after
15 seconds, and accepts only exit 0, empty stderr, strict UTF-8 and the exact
validated JSON contract. Every other transport or value failure joins the
PowerShell 7 reason and leaves Appx undecidable. No result cache is kept, since
Apply can change package state between observations.

An explicit `-UseWindowsPowerShell` import was rejected for production because
it creates a proxy command and shared compatibility session and returns
deserialized objects. A global move to 5.1 was rejected because PowerShell 7 is
the management runtime. On the observed build 19044.7663 host, three isolated
queries completed in 604--693 ms; 15 seconds leaves more than twenty times the
slowest observation for startup and Appx loading without permitting an
unbounded check. Terminal 1.24.11911.0 and Command Palette 0.12.12365.0 were
present and the nonexistent control was absent. Checks launched from both 5.1
and 7 then removed the Appx warning while retaining the known build-19044
delegation limitation and exit 2 for independent drift. No Apply ran.
