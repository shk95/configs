# Every payload declares its format and is parsed

date: 2026-08-16
scope: unixlike
status: accepted
source: 9f1e8ce:docs/status.md § Payloads were verified by nobody

Twelve files under `assets/` — eight WezTerm Lua modules, a Lua template, a
WezTerm JSON manifest, the Zellij KDL, and the PowerShell profile — were
parsed by nothing, on any host, in any CI job. `modules/zellij.nix`,
`modules/wezterm.nix` and `modules/powershell.nix` deliver them with
`.source`, which copies a file into the store without reading it, so a
syntax error evaluated, built, activated, and failed for the first time when
the application started. `tool/checks/*` ran alejandra, statix, deadnix and
`nix eval`, all of which read only Nix, and the flake declares no `checks`
output. Their Windows counterparts had been parsed by native zellij, luac,
jq and the PowerShell parser the whole time, including the `.lua.example`
template.

The cause was structural rather than an oversight. Ownership decomposes by
domain, and the repository used that same partition for verification, which
decomposes by format. Windows noticed because its manifest already had to
say what each managed file was in order to reconcile it, so a `Parser`
field was natural there. Nix never had to know, so nothing on the Unix-like
side was ever in a position to ask. The validators were present the entire
time: `lua5_4` and `stylua` sit in `modules/flake/dev-shell.nix`, and every
configured host installs Zellij.

`assets/payloads.json` now declares each payload's format and
`tool/checks/payloads` parses them, with coverage enforced in both
directions so a payload added without a declaration fails rather than
escaping quietly, and a declared format with no validator fails too. It is
an adoption by copying of the Windows manifest's idea, which is the
mechanism the architecture already prescribed; the two declarations stay
independent.
