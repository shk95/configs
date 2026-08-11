# configs

A single dendritic configuration repository for WSL, NixOS-WSL, macOS, and
native Windows.

The flake is the source of composition truth. Unix-like systems consume its
Home Manager, NixOS, and nix-darwin configurations directly. Native Windows
does not run Nix; it consumes the deterministic bundle rendered and committed
under `windows/generated/`.

## Architecture

```text
modules/                    feature-oriented flake-parts modules
modules/flake/              module classes, inventory, host composition
assets/                     source payloads referenced by modules
windows/generated/          committed Windows bundle; never hand-edited
windows/src/                PowerShell reconciliation engine
tool/                       render and verification entry points
```

The current outputs are:

- `homeConfigurations.user1`: standalone Home Manager for WSL.
- `nixosConfigurations.wsl`: NixOS-WSL using the same WSL Home Manager
  fragments.
- `darwinConfigurations.shk-macbook`: the migrated Darwin configuration.
- `packages.<system>.windows-bundle`: native-Windows desired state.

## Develop

```sh
nix develop
tool/doctor.sh
tool/render-windows
tool/checks/test
```

The Windows render command materialises the flake output into
`windows/generated/`. The pre-commit hook refuses stale generated content.

## Windows

From native Windows, only the committed bundle and PowerShell engine are
needed:

```powershell
.\windows\bootstrap.ps1 -Check
.\windows\bootstrap.ps1
```

`-Check` never installs or changes anything. Apply remains idempotent,
preserves the first original-file backups under
`%LOCALAPPDATA%\win-env\backups\original`, and records successful state
under `%LOCALAPPDATA%\win-env\state.json`.

The bundle currently covers PowerShell, PowerToys, Windows Terminal, native
Zellij, the Windows-side WSL configuration, the pinned D2Koding font, and the
shared WezTerm configuration. WezTerm is composed internally; the former
cross-repository addon protocol is intentionally absent.

## Activation

Build and evaluation are routine checks. Home Manager, NixOS, nix-darwin, and
Windows activation change external host state and are performed only
deliberately. See `CONTRIBUTING.md` for the evidence boundary.
