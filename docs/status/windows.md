# Current state: Windows

This file states what is observably true of the Windows domain today: hosts and
classes in use, schema and version facts, and open conditions. Every decision
is recorded under `docs/policy/decisions/`; the model those decisions implement
is `docs/policy/architecture.md`. The other scopes' state is in the files
beside this one.

`windows/desired/manifest.json` is at schema 4; `windows/state.json` is at
schema 2; `ProjectVersion` is 0.6.0. Schema 4 declares seven features —
`core`, `font`, `zellij`, `terminal`, `wezterm`, `powertoys`, `wsl` — and
`terminal` depends on `zellij`, `wezterm` depends on `font`
(`docs/policy/decisions/windows/feature-selection-closed.md`).

Since 2026-09-05 the three terminal payloads — Windows Terminal's
`settings.json`, WezTerm's `appearance.lua` and zellij's `config.kdl` — select
Modus Operandi, copied from the Unix-like domain's adoption of it (#163) and
owned here from that point (`docs/policy/decisions/windows/windows-adopts-modus-operandi.md`,
which supersedes the Catppuccin Latte record). Windows Terminal carries the
scheme as an inline `schemes` entry and keeps `theme` at `light`; zellij pins
the static `modus-operandi` theme rather than the `theme_light`/`theme_dark`
pair, because Windows Terminal 1.23, probed on 2026-09-05, does not answer the
colour-scheme query that pair depends on, so this copy carries the light member
only. Acrylic stays off and the font stays `D2KodingLigature Nerd Font Mono` at
size 13, unchanged from the superseded record.

Since 2026-09-09, Windows Terminal adjusts indistinguishable indexed colors in
every declared profile. PowerShell 7.6.5 emits directory names as intense text
on indexed blue (`SGR 44;1`); under Terminal's default `bright` treatment and
the copied palette, the foreground resolved to bright black `#595959`, only
1.49:1 against `#0031A9`. Stable Terminal 1.24.11911.0's indexed adjustment
makes that pair approximately `#CCCCCC` on `#0031A9`, or 6.50:1, without
altering application truecolor output, the palette, selection, cursor, light
theme, font or acrylic settings (#200).

The same day, on Windows build 19044.7663 and Terminal 1.24.11911.0, the
maintainer temporarily added the setting to the managed host file and inspected
`Get-ChildItem`, ANSI foregrounds 0–15, intense text on indexed backgrounds,
selected text, the cursor, and active/inactive tabs. Directory names and the
indexed samples were readable, selection/current state stayed distinguishable,
and a truecolor control remained unchanged. The original file was then restored
byte for byte from its matching SHA-256 backup; no Apply ran.

As of 2026-09-04, `bootstrap.ps1 -Check` returns 69 when WinGet or
PowerShell 7 is missing, or 1 under `REQUIRE_NATIVE=1`
(`INV windows/check-exit-contract`). Since 2026-09-05 a selected source no
parser here could read, and a default terminal delegation the host is below
the documented boundary for or cannot be decided against it, rank the same
way (#53, #54). Since #208, summaries distinguish a known support limit from
an unavailable observation without changing that rank. Since 2026-09-05 `windows/win-env.ps1` is the domain's one
entry point, and `bootstrap.ps1` and `setup.ps1` sit under `windows/tools/`
(`docs/policy/decisions/windows/windows-entry-point-in-domain.md`).

Since #241, `capture -Publish` on a run that found no drift resumes an earlier
capture's unfinished publish from the topic branch that carries it, for
single-parent commits with the capture subject that change only
`windows/desired/**`, and refuses anything else
(`INV windows/capture-publishes-through-dev`). Module-level fixtures cover the
branch and commit rules and the resumed pull-request body; the `WIN_ENV_E2E`
cases cover a resumed run. The suite's module-level fixtures now capture what
the functions they drive print, and run their `-WhatIf` cases in a runspace
with no host, so the `Windows tests` step of a pre-push no longer shows fixture
pushes, `What if:` lines or fixture glyph lines, and the pull-request body no
longer carries a disclaimer about them.

## Windows 10 support boundary

This table is the evidence record `INV windows/support-boundary-named`
names; a reviewer reports each item in the state below, against the build
the observation ran on.

| Item | Documented boundary | Evidence state | Source |
| --- | --- | --- | --- |
| Default terminal delegation (`HKCU:\Console\%%Startup`) | Windows 11 22H2, or Windows 10 22H2 build 19045.3031 with KB5026435, plus Windows Terminal 1.17+ | Reported as an unverified `known support limit` below the boundary and an unverified `unavailable observation` when the required build, revision or Terminal version cannot be read since #208; observed 2026-09-08 on build 19044.7663 after Appx recovery, launched from both PowerShell 5.1 and 7 with `terminal,powertoys` selected, as the sole remaining evidence reason; above the boundary the pass is a read-back of the documented values, not an observed handoff, and no host at or above 19045.3031 has been observed | Group Policy for Windows Terminal; Windows Terminal installation |
| PowerToys `Microsoft.CommandPalette` precondition (`Get-AppxPackage`) | Windows 11, or Windows 10 2004 (build 19041) or later | PowerShell 7 reports query failure rather than absence and tries one isolated Windows PowerShell 5.1 query since #207; observed present at 0.12.12365.0 on build 19044.7663 on 2026-09-08, removing the precondition's Appx warning; both routes failing remains unverified | How to Install PowerToys; PowerShell 7 module compatibility |
| Windows Terminal `Microsoft.WindowsTerminal` Appx detection | Windows 10 2004 (build 19041) or later | PowerShell 7 reports query failure rather than absence and tries one isolated Windows PowerShell 5.1 query since #207; observed present at 1.24.11911.0 on build 19044.7663 on 2026-09-08, removing the package's Appx warning while leaving the delegation boundary unchanged; both routes failing remains unverified | Windows Terminal installation; PowerShell 7 module compatibility; Windows Terminal product repository |

Sources:

- Group Policy for Windows Terminal —
  https://learn.microsoft.com/en-us/windows/terminal/group-policy
- Windows Terminal installation —
  https://learn.microsoft.com/en-us/windows/terminal/install
- How to Install PowerToys on Windows 11 and Windows 10 —
  https://learn.microsoft.com/en-us/windows/powertoys/install
- PowerShell 7 module compatibility (Windows) —
  https://learn.microsoft.com/en-us/powershell/windows/module-compatibility
- Windows Terminal product repository — https://github.com/microsoft/terminal

## `.wslconfig` prerequisites

The two existing build variants suffice for the declared policy (#198):
`files/wsl/mirrored-networking.wslconfig` at build >=22621 and
`files/wsl/nat-networking.wslconfig` below it, including Windows 11 build
22000. The latter declares only memory reclamation, not an explicit NAT
mode. Application versions validate content; they do not select a third
payload. This table describes the four managed keys and their DNS dependency.

| Key | Accepted section | Minimum WSL application | Windows/dependency condition |
| --- | --- | --- | --- |
| `networkingMode=mirrored` | `[wsl2]`; legacy `[experimental]` | 2.0.5 for `[wsl2]`; 2.0.0 for `[experimental]` | Build >=22621; capture must match the selected source's network policy |
| `hostAddressLoopback=true` | `[experimental]` | 2.0.0 | Build >=22621; active only with mirrored networking |
| `bestEffortDnsParsing=true` | `[experimental]` | 2.0.0 | Build >=22621; active only with DNS tunneling |
| `autoMemoryReclaim=gradual` | `[experimental]` | 2.0.0 | Both build variants; not Windows 11-only |
| `dnsTunneling` (dependency) | `[wsl2]`; legacy `[experimental]` | 2.0.5 for `[wsl2]`; 2.0.0 for `[experimental]` | Build >=22621; independent of mirrored selection |

Sources: [current configuration reference](https://learn.microsoft.com/en-us/windows/wsl/wsl-config),
[WSL 2.0.0 release](https://github.com/microsoft/WSL/releases/tag/2.0.0),
[the accompanying September 2023 documentation of the dependent options](https://github.com/MicrosoftDocs/WSL/commit/7d8758bf79c76d424582e8758dbc04b42118b369),
and [2.0.5 section promotion, retaining legacy aliases](https://github.com/microsoft/WSL/releases/tag/2.0.5).
The 2.0.0 boundary for the dependent options comes from that release's
accompanying documentation, not a claim that today's section layout existed
in every older application release.

Capture and read-only support reporting check the known key/section gates.
An absent or legacy `wsl.exe --version` response leaves application evidence
unknown. Capture refuses it for an application-gated key, including when the
file matches already; ordinary memory/processor tuning alone needs no assumed
modern application version. Supported inactive DNS settings are retained with
an explanation. When `dnsTunneling` is omitted, no default is inferred:
[2.1.0 enabled it](https://github.com/microsoft/WSL/releases/tag/2.1.0),
[2.1.1 disabled it](https://github.com/microsoft/WSL/releases/tag/2.1.1), and
[2.2.1 enabled it again](https://github.com/microsoft/WSL/releases/tag/2.2.1).
Unknown keys are outside this small check and retain their text. Managed
scalars with escapes are reported as undetermined, not known unsupported;
continuations remain outside the existing INI validator's grammar.

Case-insensitive names/values, quoted scalars, unquoted `#` comments and
first-occurrence precedence across aliases follow the
[WSL configuration parser](https://github.com/microsoft/WSL/blob/master/src/shared/configfile/configfile.cpp).
The existing INI syntax validator and Text comparison remain in place; this
check does not reformat or silently remove a key. Network and DNS runtime
behavior remain unverified even when all documentary prerequisites pass.
The current reference documents NAT-to-VirtioProxy fallback since 2.3.25 and
bridged deprecation since 2.4.5; neither changes source selection here.

The lower side was observed for #198 on Windows 10 build 19044.7663 with
WSL application 2.7.13.0 and PowerShell 7.6.5: the native preview selected the
lower source and preserved host tuning; read-only check reported file drift
separately from the supported prerequisites. Both desired payloads and the
host file were unchanged. Native evidence for the >=22621 mirrored file
remains owned by #121; mocks cannot close it. #198 adds prerequisite checks,
not a WSL update, restart, firewall change or a change to Apply triggers.

The `.wslconfig` runtime effect is permanently unverifiable on this host:
only the deployed file's content and its agreement with the host's Windows
build can ever be checked
(`docs/policy/decisions/windows/wslconfig-selected-by-windows-build.md`).

Two hygiene gaps touch Windows payloads: a bare account name in free prose
has no naming context to classify by and stays a manual invariant with named
evidence, and the Windows-side hygiene assertion still matches one literal
path inside one directory; generalising it is separate work.

## Open conditions

- The Windows 10 support boundary is `INV windows/support-boundary-named`.
  Since #53 the terminal delegation item decides itself against the
  boundary and the fixtures hold that; naming the build an observation ran
  on stays the reviewer's manual evidence. The lower side is observed
  (build 19044.7663); no host at or above 19045.3031 has been, so the
  item's evidence above the boundary is still owed.
- One resumed `capture -Publish` for a branch in the stuck state on the
  maintainer's host is still owed as evidence
  (`docs/policy/decisions/windows/capture-moves-host-changes.md`),
  with the pull request it opens or arms and one pre-push log whose
  `Windows tests` step shows no fixture output (#241).
