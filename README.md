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

The invariants each domain must keep, and how each one is enforced, are
enumerated under `invariants/`. The hooks record every outcome they
produce, refusals included; `tool/doctor.sh` shows the count.

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

A routine desired-state edit whose commit message is a template — a Homebrew
formula or cask, a `flake.lock` refresh — reaches `dev` in one command:

```sh
tool/version-control/commit --dry-run --publish brew add <formula>
tool/version-control/commit --publish brew add <formula>
```

The first shows the edit, the branch, the selected checks, the commit message,
the pull-request body and every command it would run, and writes nothing. The
second asks once, then branches from `origin/dev`, commits with the hooks
enabled, pushes, opens the pull request against `dev` and arms auto-merge, so
the merge happens when `Required checks` pass. There is no unattended mode and
no hook bypass. Drop `--publish` to stop at the commit.

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
reported as unverified rather than failing, and `check-desired-state.ps1` and
`test.ps1` exit 69 to say so, which is why a clone without Lua or Pester can
still push Windows work. CI supplies the missing evidence. A Unix-like home
this repository configures carries Pester itself, so `pre-push` there runs
the suite under the host's own `pwsh` and reports a real result.

`bootstrap.ps1 -Check` has a 69 of its own, and it means something else: a
detection this host could not decide, such as an Appx package whose module will
not load, which is named as unverified instead of read as missing. A
prerequisite this host lacks, WinGet or PowerShell 7, is the other case:
`-Check` reports it as 69 rather than installing anything, and 1 under
`REQUIRE_NATIVE=1`. An unparsed source only appears in its summary and does not
change what it returns. It exits 69 only when nothing else drifted, because
drift outranks an undecided item, so a host with both exits 2 and still names
the undecided items. `REQUIRE_NATIVE=1` turns an undecided item into a failure.
`-Check` never installs or changes anything. Apply is explicit:

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

### `.wslconfig` follows the host's Windows build

Selection is on or off, but `%USERPROFILE%\.wslconfig` has to exist on every
host that selects `wsl` with *different content*, because the options WSL
honours depend on the Windows build. `networkingMode=Mirrored` and two
`[experimental]` keys beside it require Windows 11 22H2, build 22621; a host
below that bound — Windows 10, and equally a Windows 11 21H2 host — ignores
them in silence. The manifest therefore declares two payloads for that one
file, and the run picks between them by build:

```text
win-env check summary
  selected: core, wsl
  Windows build 22631: wslConfig from files/wsl/mirrored-networking.wslconfig
```

A host whose build cannot be determined gets the lower payload, which every
supported build honours. The build is the discriminator throughout; the major
version is `10` on Windows 10 and Windows 11 alike and is never compared.

A host that crosses the bound later, because Windows Update moved it, is not
redeployed on its own: the desired state did not change, only the host did.
`-Check` reports it as `wslConfig settings` drift and exits 2, and
`.\windows\bootstrap.ps1 -Force` writes the payload the new build honours.

`.wslconfig` is read by the WSL VM only when it starts, and these commands never
restart it, so a passing check means the file on disk matches the payload this
host's build should have. It is not evidence that mirrored networking is
running. `docs/decisions/wslconfig-selected-by-windows-build.md` records the
per-key gate table behind the split.

### Capture a change made in the application

Apply writes a payload to the host. The other direction has a tool of its own,
so a setting changed through PowerToys, Windows Terminal, WezTerm, the managed
PowerShell profile, `.wslconfig` or Zellij becomes desired state with one
command and one confirmation:

```powershell
.\windows\tools\capture.ps1                          # every feature this host applied
.\windows\tools\capture.ps1 -Feature powertoys       # one feature
.\windows\tools\capture.ps1 -Id windowsTerminal      # one managed file
.\windows\tools\capture.ps1 -Publish                  # commit it and take it to dev
.\windows\tools\capture.ps1 -Branch fix/windows-font # override the branch name below
.\windows\tools\capture.ps1 -WhatIf                  # decide and diff, write nothing
```

Drift is decided by the comparison `-Check` already uses. Each drifted managed
file is copied into the payload this host resolves — the build-selected variant
for a conditional file — with the placeholder Apply expands restored, a JSON
payload pretty-printed to this repository's two-space style regardless of how
the host application wrote it, the diff is shown, and one `[y/N]` commits it:
one `feat(windows):` commit per feature, through the repository's hooks. The
round trip closes, so the check that reported the drift passes afterwards.

`-Publish` carries that same confirmation the rest of the way: change the
setting in the application, run `capture.ps1 -Feature <feature> -Publish`,
answer `y`, and the run branches, commits, pushes, opens one pull request
against `dev`, arms auto-merge and prints the pull-request URL. Nothing else is
needed unless CI fails. The pull request's title is the commit's own subject —
a run that captured several features titles it `feat(windows): capture settings
from the host` and lists them — and its body carries the captured managed-file
ids, the feature selection, this host's Windows build and the commit output the
hooks produced here. It never waits on CI and never merges: `Required checks`
and an up-to-date base still decide that, and a push the pre-push hook or the
remote rejects leaves every commit local on the named branch, with no retry and
no bypass. `-Publish` needs `gh` authenticated for github.com (`winget install
GitHub.cli`) and `Allow auto-merge` on in the repository settings; it refuses
before writing anything if either is missing, if an open pull request from the
same branch targets a base other than `dev`, or if the remote already has the
branch this run would create. A pull request already open against `dev` from
this branch is armed as it is, title and body untouched. Because a push carries
a branch rather than a commit, anything the branch already holds beyond `dev`
is listed before the `[y/N]`. `-WhatIf -Publish` prints the branch, the title,
the body and every command, and writes nothing.

A `JsonSubset` payload — most of the PowerToys inventory — is captured by
projecting the host file onto the keys the payload declares. The payload gains
the host's value for every key it already owns and gains no member it did not,
so a version stamp, a timestamp or a window position the application keeps in
the same file cannot reach desired state. Widening what a capture picks up is
therefore an edit to the payload, not to a list of exceptions.

That holds for the members of a declared object. A declared *list* is exact —
the comparison matches it by position and requires equal length — so declaring
one is a claim to own the whole list, and declaring an empty list means
capturing whatever the host happens to hold there. Declare a list only when
there is content to declare; a key left undeclared owns nothing, which is what
an empty list cannot express.

It refuses instead of guessing, and says which rule it refused under:
a file the suite already names as runtime state; a `JsonSubset` payload whose
declared key the host file no longer holds, or whose host value is no longer
the shape the payload declares, both named by key path; content
that still holds an absolute account path, this host's account name, or a
`.wslconfig` `firewall` key; and a build-conditional file on a host whose
Windows build is undetermined. Windows Terminal profiles the application
generated are dropped rather than captured, so a fragment profile from one
host's Git for Windows never reaches another host. Like the Unix-like commit
helper it refuses when the index already holds staged changes or a payload it
would write has uncommitted changes, and never bypasses a hook. Its branch rule
is the same helper's, too: on `master` it refuses outright; on `dev` it
branches to `feature/windows-capture-<feature>` from a freshly fetched
`origin/dev` (or `-Branch <name>`), reported before the `[y/N]`, so `dev` never
carries the commit; on any other branch it commits where it is. Nothing on the
host is written: the managed targets are read and nothing else.

## Deployment

Unix-like activation and Windows Apply are separate deployments. A common
release deploys nothing; each platform adopts it later through an explicit
change. Domain tags and evidence requirements are defined in
`CONTRIBUTING.md` and `docs/definition-of-done.md`.

No activation or Apply is a routine check. Perform either only deliberately on
the matching host.
