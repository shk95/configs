# Current state

This file states what is observably true of the repository today: hosts and
classes in use, schema and version facts, and open conditions. Every decision
is recorded under `docs/decisions/` (`docs/decisions/README.md` is the
index); the model those decisions implement is `docs/architecture.md`, and
the three-domain direction is `docs/architecture.md` § Decision.

## Unix-like

Unix-like Home Manager hosts are standalone Ubuntu WSL, NixOS-WSL, and
nix-darwin, each importing `homeManager.shared`. `homeManager.wsl`,
`homeManager.wslStandalone`, `homeManager.desktop`, and `homeManager.darwin`
are the platform classes layered on top, as overlays rather than parallel
implementations.

SDKMAN is adopted but not owned
(`docs/decisions/sdkman-adopted-not-owned.md`).

WezTerm and Ghostty are the desktop terminals; Home Manager installs the
D2Coding Nerd Font package and configures `D2KodingLigature Nerd Font Mono`
for both. On Darwin, WezTerm also reads Home Manager's nested font directory
explicitly, and Home Manager state version 25.11 uses
`targets.darwin.copyApps`, so the WezTerm bundle sits under `~/Applications/
Home Manager Apps` as a Spotlight-compatible copy rather than a Nix-store
symlink. Alacritty is fully inactive: there is no Alacritty package, Home
Manager module, or generated configuration.

## Windows

`windows/desired/manifest.json` is at schema 4; `windows/state.json` is at
schema 2; `ProjectVersion` is 0.6.0. Schema 4 declares seven features —
`core`, `font`, `zellij`, `terminal`, `wezterm`, `powertoys`, `wsl` — and
`terminal` depends on `zellij`, `wezterm` depends on `font`
(`docs/decisions/feature-selection-closed.md`).

As of 2026-09-04, `bootstrap.ps1 -Check` returns 69 when WinGet or
PowerShell 7 is missing, or 1 under `REQUIRE_NATIVE=1`
(`INV windows/check-exit-contract`).

### Windows 10 support boundary

| Item | Documented boundary | Evidence state | Source |
| --- | --- | --- | --- |
| Default terminal delegation (`HKCU:\Console\%%Startup`) | Windows 11 22H2, or Windows 10 22H2 build 19045.3031 with KB5026435, plus Windows Terminal 1.17+ | Unverified: the read-back passes below the boundary although the setting does nothing (#53) | Group Policy for Windows Terminal; Windows Terminal installation |
| PowerToys `Microsoft.CommandPalette` precondition (`Get-AppxPackage`) | Windows 11, or Windows 10 2004 (build 19041) or later | Unverified: `Appx` needs the PowerShell 7.1 compatibility layer this domain does not use (#37) | How to Install PowerToys; PowerShell 7 module compatibility |
| Windows Terminal `Microsoft.WindowsTerminal` Appx detection | Windows 10 2004 (build 19041) or later | Unverified: same undetectable `Appx` route (#37) | Windows Terminal installation; PowerShell 7 module compatibility; Windows Terminal product repository |

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

The `.wslconfig` runtime effect is permanently unverifiable on this host:
only the deployed file's content and its agreement with the host's Windows
build can ever be checked
(`docs/decisions/wslconfig-selected-by-windows-build.md`).

Two hygiene gaps touch Windows payloads: a bare account name in free prose
has no naming context to classify by and stays a manual invariant with named
evidence, and the Windows-side hygiene assertion still matches one literal
path inside one directory; generalising it is separate, planned work.

No explicit `common/` component has yet been justified or created.

## Repository

Branch protection is enabled on both `dev` and `master`: pull requests and
current-branch checks are required, administrators are enforced,
conversations must be resolved, force pushes and deletions are disabled, and
both branches require only the `Required checks` gate.

Only same-repository `dev` may open a pull request against `master`; the
result is a merge commit. `dev` uses strict status checks, `master` uses
non-strict, and the remote allows merge commits while disabling squash and
rebase merging.

The merge gate is CI's `Required checks`, demanded whenever a change falls
in a domain that check covers.

The invariant registry holds 49 entries: 9 pending
(`repository/no-cross-domain-dependency` #124,
`unixlike/composition-in-one-place` #127, `unixlike/eval-covers-every-host`
#131, `unixlike/import-order-independence` #128,
`unixlike/package-ownership` #130, `unixlike/version-manager-last` #129,
`windows/no-unix-host-required` #124, `windows/parser-declared` #135,
`windows/unique-ids` #134), 0 fixture units untagged, and
`tool/version-control/invariants` enforces C10 (no untagged fixture unit) by
default.

Content before a shell suite's first banner is in no fixture unit and
invisible to C10 (`docs/decisions/fixture-tags-name-proven-invariants.md`).

## Common

No `common/` component exists.
`docs/decisions/powershell-copied-per-domain.md` names what would justify
one: both the PowerShell and the Zellij keymap copies showing stable
semantics across independent platform validation and release cycles.

## Open conditions

- `docs/decisions/ci-evidence-without-hosted-runners.md`: reopens when a
  defect class a hosted runner would have caught occurs twice, or a NixOS
  host configuration exists for VM tests to target.
- `docs/decisions/powershell-copied-per-domain.md`: reopens when both
  implementations show stable semantics that would justify a common
  component.
- Milestone naming, issue membership, and closure stay a manual maintainer
  review; automated remote enforcement is deferred until that workflow shows
  a recurring failure.
- The Windows 10 support boundary is a manual invariant with no registry
  entry; #54 owns converting `-Check`'s exit status to express it, and a
  windows pending/manual entry is separate work.
- Unix-like import-order independence is pending (#128).

## Pending invariants

- `repository/no-cross-domain-dependency` — #124
- `unixlike/composition-in-one-place` — #127
- `unixlike/eval-covers-every-host` — #131
- `unixlike/import-order-independence` — #128
- `unixlike/package-ownership` — #130
- `unixlike/version-manager-last` — #129
- `windows/no-unix-host-required` — #124
- `windows/parser-declared` — #135
- `windows/unique-ids` — #134
