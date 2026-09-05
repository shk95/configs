id: windows/support-boundary-named
statement: A host observation names the Windows build it came from and is evidence only for the builds the documented support boundary covers; an item the host accepts but does not honour below that boundary is reported unverified, never verified.
rationale: docs/architecture.md § Windows domain
enforced-by: manual the reviewer names the Windows build under a -Check or Apply observation and reports each item of the Windows 10 support boundary table in its boundary state
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
owner: repository maintainer
decision: docs/decisions/terminal-delegation-unverified-below-boundary.md § Terminal delegation is unverified below the documented boundary
decision: docs/decisions/appx-detection-unverified-not-absent.md § Undecidable Appx detection is unverified, not absent

The boundary is a documentary one — an OS build and revision plus an
application version for the terminal delegation, a PowerShell module route
for the two Appx items — and a host below it accepts the write and answers
the read-back as if the setting worked. The check decides what it can: the
two Appx items report unverified when the module will not load, and the
terminal delegation is decided against the documented condition rather than
the write, which the fixtures hold on every side of it. What no check
decides is the build an observation ran on: that stays the reviewer's,
named beside the observation, with the state of each item in the
`docs/status.md` table, required by `docs/definition-of-done.md`.
