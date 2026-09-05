# Every composed home renders in a terminal the repository declares

date: 2026-09-05
scope: unixlike
status: accepted
issue: #156
reopen-when: A home is composed whose terminal no repository file declares, or a declaring terminal payload selects a dark scheme.

Every home `modules/flake/configurations.nix` composes renders inside a
terminal whose colour scheme a file of this repository declares. The graphical
Unix-like homes declare theirs in the Unix-like domain, in
`assets/wezterm/config/appearance.lua` and `modules/ghostty.nix`: WezTerm on
Flexoki Light outright, Ghostty on `light:Flexoki Light,dark:Flexoki Dark`,
which is the same family and is the one terminal here that reports which half
it is on. The WSL homes declare theirs in the Windows domain, in
`windows/desired/files/terminal/settings.json`, which has selected
`"colorScheme": "Flexoki Light"` with `"theme": "light"` since #97. Those
three files cover every home `modules/flake/configurations.nix` assembles
today: every terminal this repository declares for a composed home is light.

Reading that Windows payload is a cross-domain read by a person, not by code.
No Unix-like module imports it, opens it, or derives a value from it — that is
the boundary `tool/version-control/domain-reads` enforces — so the fact stated
here is a reviewed observation with a date, not a dependency. A change to the
Windows payload that turned the scheme dark would therefore break no
evaluation and fail no check; it would reopen this record, which is what
`reopen-when` above says.

The consequence is a rule for colour in `homeManager.shared`, and it cuts both
ways. A tool that can defer to the terminal's sixteen ANSI colours still
should, because deferral cannot disagree with any declared terminal and needs
no theme at all: `modules/bat.nix` keeps `theme = "ansi"`, `modules/skim.nix`
keeps `--color=16` and `modules/eza.nix` keeps eza's ANSI default. A tool that
cannot defer — zellij, whose pane frames, tab bar and status line are
backgrounds rather than foregrounds, and btop, whose themes are full palettes
— may now name the light member of the Flexoki family in `homeManager.shared`
rather than in a class that excludes the WSL homes. #156 is the first use:
`assets/zellij/config.kdl` carries a static `theme "flexoki-light"` for every
class, because Windows Terminal 1.23.20211.0 was probed on 2026-09-05 and does
not answer the colour-scheme query the `theme_dark`/`theme_light` pair depends
on.

What was rejected is keeping `shared` colour-neutral and pinning per class,
mirroring the existing `homeManager.desktop` block into `homeManager.wsl`.
Both classes would have carried the same line for the same reason, and the
asset is the one place the keymap and the palettes already live, so the
per-class form would have bought a second copy and no additional truth. The
cost of the form chosen is stated so it is not discovered later: if a class is
ever composed into a home whose terminal no repository file declares, this
record is reopened. What the repository does not choose is the terminal a
shell is attached from — VS Code's integrated terminal, conhost, an SSH
client — and a home reached from one of those now gets this static light line
where it used to get zellij's dark fallback; that is accepted as the
repository's light default and is not a reopen condition.
