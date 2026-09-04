# Feature selection is closed over declared dependencies

date: 2026-08-18
scope: windows
status: accepted
source: 9f1e8ce:docs/status.md § Windows authority split

Windows desired state is selectable. Manifest schema 4 declares seven features
(`core`, `font`, `zellij`, `terminal`, `wezterm`, `powertoys`, `wsl`)
and every package, managed file, the font, and the terminal delegation is
owned by exactly one of them. `bootstrap.ps1 -Minimal` deploys `core` alone,
which installs PowerShell 7 and the managed profile and touches no font,
registry value, or application setting. State schema 2 records the selection;
a schema 1 state is read as a full deployment, so a host that applied before
this change keeps exactly what it has.

Three boundaries are decisions rather than accidents. `terminal` requires
`zellij` because `files/terminal/settings.json` is owned whole on write and
carries a profile that launches `zellij.exe`; splitting that payload or adding
a merge comparison mode was rejected as more expensive than installing one
small package. `wezterm` requires `font` because `files/wezterm/fonts.json`
leads with `D2KodingLigature Nerd Font Mono` for Hangul coverage: the list
names only D2Koding families, and the concrete alternative already on a default
Windows install, Malgun Gothic, is not fixed-pitch and would misalign any line
mixing Korean and Latin. Declaring the dependency, the same way `terminal`
already does, was cheaper than that misalignment; a host selecting `wezterm`
alone now installs `font` too, reported as `added by dependency`. PowerToys
stays one feature because `files/powertoys/settings.json` already owns the
per-module enable map; a second selection axis over the same modules would
have two sources.

The desired-state hash is scoped to the selected features plus
`manifest.json`. A whole-tree hash reported drift for payloads a host never
deploys and forced an Apply that could not change anything on it.
