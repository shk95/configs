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

Portable interactive programs are declared once in `homeManager.shared` and
reach all three Unix-like outputs. Platform Home Manager classes add only
platform-specific behavior. Darwin Homebrew declarations are reserved for
macOS applications, Mac App Store items, and explicit exceptions that the
locked nixpkgs cannot provide on Darwin.

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

Pass a scope such as `tool/doctor.sh repository` when a foreign-platform
capability is irrelevant to the current change.

Allow the repository's committed direnv environment once per clone:

```sh
direnv allow
```

Entering the repository then loads `devShells.default` from the flake. Put
machine-local environment additions in `.envrc.local`; it is sourced when
present and is intentionally ignored by Git.

Run checks for the domain you changed. `CONTRIBUTING.md` lists the workflows.

Codex, Claude Code, and other Agent Skills-compatible tools can use the
project's `run-version-control-workflow` skill to classify a change, audit Git
policy, prepare work, or plan a domain release. The canonical model-neutral
skill lives under `.agents/skills/`; `.claude/skills/` contains only Claude's
discovery adapter. Audit and release planning are read-only by default.

The Justfile exposes the same checks and target-specific runners without
duplicating the configured user or host name:

```sh
just doctor
just format-check
just lint
just test
just check

just home-eval
just home-build
just darwin-eval
just darwin-build
just darwin-check
```

The `*-eval`, `*-build`, and `*-check` commands do not activate a configuration.
Activation remains explicit and host-specific:

```sh
just home-switch       # intended Ubuntu WSL host only
just darwin-switch     # target Mac only; requires sudo
```

## Windows

From native Windows:

```powershell
.\windows\tools\check-desired-state.ps1
.\windows\tools\test.ps1
.\windows\bootstrap.ps1 -Check
```

The desired-state check requires `zellij.exe` and a `luac` compiler so KDL and
Lua are validated by their native tools. The test entrypoint requires Pester
5.7.1; install it with
`Install-Module Pester -RequiredVersion 5.7.1 -Scope CurrentUser`. `-Check`
never installs or changes anything. Apply is explicit:

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
