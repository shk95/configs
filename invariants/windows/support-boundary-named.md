id: windows/support-boundary-named
statement: A host observation names the Windows build it came from and is evidence only for the builds the documented support boundary covers; an item the host accepts but does not honour below that boundary is reported unverified, never verified.
rationale: docs/architecture.md § Windows domain
enforced-by: manual the reviewer names the Windows build under a -Check or Apply observation and reports each item of the Windows 10 support boundary table in its boundary state
owner: repository maintainer
decision: docs/decisions/terminal-delegation-unverified-below-boundary.md § Terminal delegation is unverified below the documented boundary
decision: docs/decisions/appx-detection-unverified-not-absent.md § Undecidable Appx detection is unverified, not absent

No check decides this: the boundary is a documentary one — an OS build plus
an application version for the terminal delegation, a PowerShell module
route for the two Appx items — and a host below it accepts the write and
answers the read-back as if the setting worked. The evidence is therefore the
reviewer's: the build the observation ran on, named beside it, and the state
of each item in the `docs/status.md` table, required by
`docs/definition-of-done.md`. The two Appx items already report unverified
from the check itself; the terminal delegation still passes its read-back
below the boundary, and #53 owns deciding that item against the boundary
so the check can say unverified there too. Until it does, this entry is what
keeps a passing `-Check` on such a host from being read as verified.
