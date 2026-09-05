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
are the platform classes layered on top
(`docs/decisions/home-manager-platform-classes.md`).

SDKMAN is adopted but not owned
(`docs/decisions/sdkman-adopted-not-owned.md`). Its hook is the last
thing the generated zsh initialisation runs: since 2026-09-04 it sits after
Home Manager's own late pieces (starship, direnv, syntax highlighting),
where before it ran inside the repository's default-order block ahead of
them, and an assertion refuses a PATH assignment placed later.

Three other generated things changed on 2026-09-04 and reach a home on its
next activation: `~/.config/zellij/config.kdl` is Home Manager's rendering
of the asset (a blank line and an `// extraConfig` marker, then the keymap,
plus the theme node in the desktop class) rather than a link to it; every
home carries Pester 5.7.1 under `~/.local/share/powershell/Modules`, fetched
from the PowerShell Gallery at build time, so `pre-push` can run the Windows
suite from a Unix-like clone; and every generation's hash moved once,
because the fragments a class collects are now imported in the order of
their defining files rather than the directory walk
(`INV unixlike/import-order-independence`). `flake.lock` is unchanged.

WezTerm and Ghostty are the desktop terminals; Home Manager installs the
D2Coding Nerd Font package and configures `D2KodingLigature Nerd Font Mono`
for both. On Darwin, WezTerm also reads Home Manager's nested font directory
explicitly, and Home Manager state version 25.11 uses
`targets.darwin.copyApps`, so the WezTerm bundle sits under `~/Applications/
Home Manager Apps` as a Spotlight-compatible copy rather than a Nix-store
symlink. Alacritty is fully inactive: there is no Alacritty package, Home
Manager module, or generated configuration. A future adoption should add its
package, configuration, and Dock ownership together.

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

This table is the evidence record `INV windows/support-boundary-named`
names; a reviewer reports each item in the state below, against the build
the observation ran on.

| Item | Documented boundary | Evidence state | Source |
| --- | --- | --- | --- |
| Default terminal delegation (`HKCU:\Console\%%Startup`) | Windows 11 22H2, or Windows 10 22H2 build 19045.3031 with KB5026435, plus Windows Terminal 1.17+ | Unverified: the read-back passes below the boundary although the setting does nothing (#53) | Group Policy for Windows Terminal; Windows Terminal installation |
| PowerToys `Microsoft.CommandPalette` precondition (`Get-AppxPackage`) | Windows 11, or Windows 10 2004 (build 19041) or later | Reported unverified by `-Check` since #37 | How to Install PowerToys; PowerShell 7 module compatibility |
| Windows Terminal `Microsoft.WindowsTerminal` Appx detection | Windows 10 2004 (build 19041) or later | Reported unverified by `-Check` since #37 | Windows Terminal installation; PowerShell 7 module compatibility; Windows Terminal product repository |

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
path inside one directory; generalising it is separate work.

## Repository

Branch protection is enabled on both `dev` and `master`: pull requests and
current-branch checks are required, administrators are enforced,
conversations must be resolved, force pushes and deletions are disabled, and
both branches require only the `Required checks` gate.

`dev` requires a pull request and an up-to-date base; `master` accepts only
`dev` through a pull request with a merge commit; squash and rebase merges
are disabled.

The merge gate is CI's `Required checks`, demanded whenever a change falls
in a domain that check covers.

The invariant registry holds 50 entries, none pending and no fixture unit
untagged, and `tool/version-control/invariants` enforces C10 (no untagged
fixture unit) by default. Enforced is not the same as held: the manual
`INV windows/support-boundary-named` records that the terminal delegation
item still passes its read-back below the Windows 10 boundary (#53).

Content before a shell suite's first banner is in no fixture unit and
invisible to C10 (`docs/decisions/fixture-tags-name-proven-invariants.md`).

`tool/version-control/domain-reads` runs on every commit and in CI beside
the hygiene scan; the Windows CI job no longer walks the checkout for
PowerShell files, and `windows/tools/test.ps1` is the one place every script
under the Windows tree is parsed for syntax (`check-desired-state.ps1`
still parses the PowerShell payload it validates). `pre-push` audits the
pushed history only.

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
- The Windows 10 support boundary is registered as the manual
  `INV windows/support-boundary-named`; its evidence is the reviewer's
  naming of the build and of each item's boundary state. #53 owns deciding
  the terminal delegation item against the boundary so `-Check` can report
  it unverified there, and #54 stays open for that conversion.
- One real-host capture run is still owed as evidence
  (`docs/decisions/capture-moves-host-changes.md`).
- `docs/decisions/hygiene-tool-owns-enforcement.md`: reopens when the same
  four axes are decided from a typed declaration rather than from text.
- `docs/decisions/annotated-tag-is-the-release-record.md`: reopens when a
  consumer needs a release artifact or a note the tag annotation cannot
  carry.

## Pending invariants

None since 2026-09-04. The registry summary above is the count.
