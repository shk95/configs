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
the light scheme outright, Ghostty on the `light:…,dark:…` pair of the same
family, being the one terminal here that reports which half it is on. The WSL
homes declare theirs in the Windows domain, in
`windows/desired/files/terminal/settings.json`, which has selected a light
`"colorScheme"` with `"theme": "light"` since #97. Which family those three
files name is a separate question from this record's, and it has been answered
twice: Flexoki Light at #97 and #156, Modus Operandi since #163 on the
Unix-like side and, from #164, on the Windows one (see the dated paragraph at
the end of this record). Those three files cover every home
`modules/flake/configurations.nix` assembles today: every terminal this
repository declares for a composed home is light, whichever family it names.

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
— may now name the light member of the declared family in `homeManager.shared`
rather than in a class that excludes the WSL homes. #156 is the first use:
`assets/zellij/config.kdl` carries a static light `theme` for every class
(`flexoki-light` at #156, `modus-operandi` since #163), because Windows
Terminal 1.23.20211.0 was probed on 2026-09-05 and does not answer the
colour-scheme query the `theme_dark`/`theme_light` pair depends on.

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

On 2026-09-05 the scheme every declaring file selects changed, and the rule
above did not. The maintainer found Flexoki Light's paper background
(`#FFFCF0`) and its low-saturation 600-series accents too close together to
tell apart across the tools, so the family named by
`assets/wezterm/config/appearance.lua` and `modules/ghostty.nix` is now
Modus Operandi, with Modus Vivendi as the dark half where a pair exists.
That is #163, and it is a Unix-like change only: the Windows Terminal
payload adopts the same family by copy in #164, on the Windows domain's own
schedule, which is what the ownership rule in `AGENTS.md` requires and why
this paragraph names two issues rather than one. Modus was chosen over
GitHub Light and One Half Light because it is the one family designed to a
WCAG AAA contrast target, and because its dark half ships beside the light
one, which is what the Ghostty pair and zellij's `theme_dark`/`theme_light`
both need. `assets/zellij/config.kdl` carries `modus-operandi` and
`modus-vivendi` derived from those palettes by the rule that asset states,
its static `theme` now naming `modus-operandi`. Every premise this record
rests on is untouched by that: the declaring files are the same files, every
one of them still declares light, and the tools that defer to the terminal's
own sixteen colours — `modules/bat.nix`, `modules/skim.nix`,
`modules/eza.nix` — needed no edit at all, which is the clearest evidence
the deferral rule was worth writing down. What changes a scheme reaches is
therefore a measure of the rule, not a reopening of it; `reopen-when` above
still names the two conditions that would reopen it, and neither happened.
