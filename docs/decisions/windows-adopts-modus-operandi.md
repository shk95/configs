# Windows adopts Modus Operandi by copying

date: 2026-09-05
scope: windows
status: accepted
issue: #164
supersedes: docs/decisions/windows-adopts-catppuccin-latte.md

The three Windows terminal payloads — `windows/desired/files/terminal/settings.json`,
`windows/desired/files/wezterm/config/appearance.lua` and
`windows/desired/files/zellij/config.kdl` — select Modus Operandi, copied from
the Unix-like domain's own adoption of it (#163). The copy is the rule this
repository already follows for Unix-like material on Windows rather than a new
one: each payload carries the palette in its own format, in full, and the
Windows domain owns its copy from the moment it lands. The reason the two
domains move together at all is not that they share a source but that they
share a screen. The WSL homes render inside Windows Terminal, so a Windows
payload left on the previous scheme would put two light schemes on one display
— the terminal's frame in one palette and the session inside it in another —
which is exactly the kind of visible disagreement a copy is supposed to avoid
while it is still deliberate.

Each payload adopts the scheme in the shape its own format allows. Windows
Terminal ships no scheme of this name, so `schemes` carries an inline entry
named `Modus Operandi` and the profile default selects it by name; `theme`
stays `light`. WezTerm carries the same palette as an inline table rather than
a preset name, so the rendered result does not depend on which schemes the
installed WezTerm build bundles. Zellij carries the static `modus-operandi`
theme block and pins it with `theme "modus-operandi"`: Windows Terminal
1.23.20211.0 was probed on 2026-09-05 and does not answer the colour-scheme
query that zellij's `theme_light`/`theme_dark` pair depends on, the same probe
`docs/decisions/composed-homes-render-in-declared-terminals.md` rests on. With
no report arriving, the dark half would be state nothing on this terminal could
reach. That is why this copy carries the light member only, where the Unix-like
source carries both.

This record also closes a gap the payloads opened long before this change.
`docs/decisions/windows-adopts-catppuccin-latte.md` stayed `status: accepted`
after pull request #97 (issue #89) replaced Catppuccin Latte with Flexoki
Light in the same payloads on 2026-08-31 (`ba02e55`); that reversal was
recorded only as a dated paragraph inside the record it reversed, which is not what
`docs/decisions/README.md` asks for and left a live-looking record naming a
scheme no payload selected. Superseding it now settles both moves at once: the
Latte record is history from here, and the current scheme is named by a record
whose status can be read without reading its prose to the end.

What the superseded record decided about everything other than the scheme name
is carried unchanged and is not reopened here. `useAcrylic` and
`useAcrylicInTabRow` stay off, because the argument against them was never
about which light scheme sits behind the blend: acrylic mixes the window with
whatever happens to be behind it, so its contrast is not a property of the
configuration at all. Modus Operandi does not weaken that argument; its
foreground on its background is `#000000` on `#FFFFFF`, and spending a maximal
contrast on an unpredictable blend is a worse trade than spending a moderate
one. The font stays `D2KodingLigature Nerd Font Mono` at size 13 for the same
reason it was chosen: a scheme change is not a typography change.

One value is copied without correction. In this port ANSI 15 (`#595959`,
7.0:1 on white) is darker than ANSI 7 (`#A6A6A6`, 2.43:1), which inverts the
usual bright-is-lighter relation. It is transcribed as it stands, because a
local repair would make the Windows payloads disagree with the Unix-like
terminals rendering the same sessions, and because the inversion is the
readable direction here: text in ANSI 7 is close to invisible on white either
way.

The cost is the one every copy carries: the Windows payloads and the Unix-like
assets now hold the same palette in three formats with no mechanism keeping
them equal, so a future Unix-like scheme change is a separate, reviewable
Windows change and not an automatic one. That is the intended cost. Divergence
between the two is a failure only when it is accidental; when it is decided —
as the missing dark member above is — it is the point of owning the copy.
