# configs

A personal configuration monorepo with independent Unix-like, native Windows,
and explicitly common domains.

The repository is shared for discovery and history. It is not one
cross-platform build graph:

- Nix is the composition authority for Linux, WSL, NixOS, and macOS.
- Native Windows owns its desired state and must be verifiable on Windows.
- Truly platform-neutral material may live in `common`, but common code is the
  exception rather than the default.

See `docs/architecture.md` for the domain and release model.

## Architecture

```text
unixlike
  flake.nix
  modules/                    flake-parts and host composition
  assets/                     Unix-like source payloads

windows
  windows/desired/            native manifest and owned payloads
  windows/src/                PowerShell reconciliation engine
  windows/tests/              native Windows tests

common
  common/                     explicit, independently versioned material only
                              (created only when sharing is justified)
```

The current Unix-like outputs are:

- `homeConfigurations.user1`: standalone Home Manager for WSL.
- `nixosConfigurations.wsl`: NixOS-WSL configuration.
- `darwinConfigurations.shk-macbook`: nix-darwin configuration.

Graphical Unix-like applications are a separate Home Manager composition
class. Darwin currently consumes it; both WSL outputs deliberately do not, so
they use a Windows-owned terminal without also building a Linux GUI terminal.
Ghostty is installed by Homebrew on Darwin while Home Manager owns its shared
Unix-like configuration.

Windows desired state is declared directly in
`windows/desired/manifest.json`. Its payloads, including the Windows-owned
WezTerm and Zellij copies, live below `windows/desired/files/`. Neither requires
Nix to author, validate, or consume.

## Develop

Prepare the clone and inspect available host capabilities:

```sh
tool/setup
tool/setup --fix
tool/doctor.sh
```

Run checks for the domain you changed. `CONTRIBUTING.md` lists the workflows.

## Windows

From native Windows:

```powershell
.\windows\tools\check-desired-state.ps1
Invoke-Pester .\windows\tests
.\windows\bootstrap.ps1 -Check
```

The desired-state check requires `zellij.exe` and a `luac` compiler so KDL and
Lua are validated by their native tools. `-Check` never installs or changes
anything. Apply is explicit:

```powershell
.\windows\bootstrap.ps1
```

Apply remains idempotent, preserves first-original-file backups under
`%LOCALAPPDATA%\win-env\backups\original`, and records successful state under
`%LOCALAPPDATA%\win-env\state.json`.

## Deployment

Unix-like activation and Windows Apply are separate deployments. A common
release deploys nothing; each platform adopts it later through an explicit
change. Domain tags and evidence requirements are defined in
`CONTRIBUTING.md` and `docs/definition-of-done.md`.

No activation or Apply is a routine check. Perform either only deliberately on
the matching host.
