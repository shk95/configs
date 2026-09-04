# Windows adopts Catppuccin Latte by copying

date: 2026-08-30
scope: windows
status: accepted
issue: #39
source: 9f1e8ce:docs/status.md § Windows authority split

`windows/desired/files/terminal/settings.json` and
`windows/desired/files/wezterm/config/appearance.lua` adopted the Unix-like
light-theme decision (#35) by copying: both now select the light member of the
same Catppuccin family, `Catppuccin Latte`, the WezTerm payload as its built-in
scheme name and the Windows Terminal payload as an inline `schemes` entry using
the published `catppuccin/windows-terminal` port, because Windows Terminal does
not ship Catppuccin as a built-in scheme. As with every other Windows copy of
Unix-like material, each copy is Windows-owned from the moment it lands and may
diverge from the Unix-like source without that being a failure. The adoption
also re-judged `useAcrylic` and `useAcrylicInTabRow`, which the prior dark
scheme left `true`, and turned both off: acrylic blends the window with whatever
sits behind it, so its result is inherently unpredictable, and Catppuccin
Latte's foreground already runs a moderate ~7:1 contrast against its background
(`#4C4F69` on `#EFF1F5`) with less margin than the dark scheme it replaced to
spend on an unpredictable blend. `windows/desired/files/terminal/settings.json`
is plain JSON and carries no comment syntax, so this reasoning is recorded here
rather than beside the setting.
