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

The separate sibling `skills` project provides `design-project-governance` for
introducing a project rule. It separates durable policy, human procedure, agent
orchestration, executable enforcement, current adoption, and per-run evidence
before implementation while this repository retains authority for the result.
Source promotion uses `tool/version-control/plan-promotion` before a
`dev`-to-`master` pull request; promotion is not a release or deployment.

The Justfile exposes the same checks and target-specific runners without
duplicating the configured user or host name:

```sh
just doctor
just format-check
just lint
just payloads
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

### Git commands that get no alias

`modules/git.nix` declares this repository's `programs.git.settings.alias`
set and, beside it, a comment naming the Git commands that deliberately stay
unaliased because knowing them is more useful than shortening them:

- `git show` for the last commit with its patch, `git show --stat` for just
  the summary, and `git show <ref>` for any other commit.
- `git diff` (unstaged) versus `git diff --cached` (staged, aliased `dc`)
  versus `git diff HEAD` (both at once) — the three-way distinction behind
  most "the diff looks wrong" confusion.
- `git log -p -1`, and `git log -p -- <path>` to follow one file.
- `git show HEAD@{1}` with `git reflog` to recover a previous position.
- `git range-diff` to compare two versions of a series.

See the comment in `modules/git.nix` for the reasoning; this list only
repeats the names so a maintainer can find them without opening a Nix module.

## Windows

From native Windows:

```powershell
.\windows\tools\setup-dev.ps1
.\windows\tools\check-desired-state.ps1
.\windows\tools\test.ps1
.\windows\bootstrap.ps1 -Check
```

`setup-dev.ps1` installs the contributor toolchain once, from
`windows/toolchain.json`. CI installs from the same declaration, so local
verification and the merge gate agree on the versions. Zellij is not part of it
because the manifest already installs the application itself.

The checks run without that toolchain. A source whose parser is missing is
reported as unverified rather than failing, and the commands exit 69 to say so,
which is why a clone without Lua or Pester can still push Windows work. CI
supplies the missing evidence. `-Check` never installs or changes anything.
Apply is explicit:

```powershell
.\windows\bootstrap.ps1
```

Apply remains idempotent, preserves first-original-file backups under
`%LOCALAPPDATA%\win-env\backups\original`, and records successful state under
`%LOCALAPPDATA%\win-env\state.json`.

### Feature selection

A host does not have to take the whole manifest. `windows/desired/manifest.json`
declares features, every package and managed file belongs to exactly one of
them, and a host picks how many it deploys:

```powershell
.\windows\bootstrap.ps1 -Minimal              # core only: PowerShell 7 and the managed profile
.\windows\bootstrap.ps1 -Feature terminal     # exactly this set, plus what it declares it needs
.\windows\bootstrap.ps1 -Add powertoys        # union with what this host already applied
.\windows\bootstrap.ps1 -All                  # everything the manifest declares
.\windows\bootstrap.ps1 -Check                # verify the selection this host recorded
```

The features are `core` (required), `font`, `zellij`, `terminal`, `wezterm`,
`powertoys`, and `wsl`. `terminal` requires `font` and `zellij` because it owns
`files/terminal/settings.json` whole, and that file pins the D2Koding face and
launches `zellij.exe` from a profile. Dependencies are resolved and reported
rather than refused:

```text
win-env check summary
  selected: core, font, zellij, terminal
  added by dependency: font, zellij
  not selected: wezterm, powertoys, wsl
```

With no selection argument an applied host keeps the selection it recorded and a
host that has never applied takes everything, so an existing deployment does not
change because selection exists. The selection lives in `state.json`, not in the
repository: the manifest declares what exists, the host records how much of it
it took.

Deselecting stops management. It does not uninstall a package or delete a file
that a previous Apply deployed; removing those is a separate manual decision.

## Deployment

Unix-like activation and Windows Apply are separate deployments. A common
release deploys nothing; each platform adopts it later through an explicit
change. Domain tags and evidence requirements are defined in
`CONTRIBUTING.md` and `docs/definition-of-done.md`.

No activation or Apply is a routine check. Perform either only deliberately on
the matching host.
