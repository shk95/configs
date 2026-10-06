# configs

A personal configuration monorepo with independent Unix-like, native Windows,
and explicitly common domains.

The repository is shared for discovery and history. It is not one
cross-platform build graph:

- Nix is the composition authority for Linux, WSL, NixOS, and macOS.
- Native Windows owns its desired state and must be verifiable on Windows.
- Truly platform-neutral material may live in `common`, but common code is the
  exception rather than the default.

See `docs/policy/architecture.md` for the domain and release model.

The invariants each domain must keep, and how each one is enforced, are
enumerated under `docs/policy/invariants/`. The hooks record every outcome they
produce, refusals included; `tool/configs doctor` shows the count.

## Architecture

```text
unixlike
  flake.nix                   flake definition and lock (unixlike/flake.lock)
  payloads.json               the payload declaration
  modules/                    flake-parts modules grouped by concern
  tool/checks/                the Unix-like check suite

windows
  windows/win-env.ps1         the one entry point: check, apply, capture, validate, test, setup-dev, font
  windows/desired/            native manifest and owned payloads
  windows/src/                PowerShell reconciliation engine
  windows/tests/              native Windows tests

common
  common/                     explicit, independently versioned material only
                              (created only when sharing is justified)
```

The Unix-like flake exports typed constructors through `lib.mkNixos`,
`lib.mkDarwin` and `lib.mkHome`. Real host identities and final outputs live in
the private `configs-hosts` repository, where each host pins this provider in
its own flake and lock. The outputs in this repository use synthetic
`fixture-*` names and the `example` account to exercise all five NixOS machine
kinds, Darwin and standalone Home Manager. They are test instances, not
deployment targets (`docs/status/unixlike.md`).

Graphical Unix-like applications are a separate Home Manager composition
class. Both WSL outputs are command-line configurations and deliberately
exclude Linux GUI applications and WSLg integration. They use a Windows-owned
terminal. Adding WSL GUI support requires a Unix-like policy revision before
any implementation is planned.
Ghostty is installed by Homebrew on Darwin while Home Manager owns its shared
Unix-like configuration.

Portable interactive programs are declared once in `homeManager.shared` and
reach the consumer outputs through the provider constructors. Platform Home
Manager classes add only
platform-specific behavior. Darwin Homebrew declarations are reserved for
macOS applications, Mac App Store items, and explicit exceptions that the
locked nixpkgs cannot provide on Darwin.

Windows desired state is declared directly in
`windows/desired/manifest.json`. Its payloads, including the Windows-owned
WezTerm and Zellij copies, live below `windows/desired/files/`. Neither requires
Nix to author, validate, or consume.

## Develop

Prepare the clone and inspect available host capabilities:

`tool/configs help` lists the repository commands intended for direct use.

```sh
tool/configs setup
tool/configs setup --fix
tool/configs doctor
```

Pass a scope such as `tool/configs doctor repository` when a foreign-platform
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
formula or cask, a `unixlike/flake.lock` refresh — reaches `dev` in one
command:

```sh
tool/configs worktree new unixlike-brew-add feature
cd ../configs-wt/feature-unixlike-brew-add
tool/configs commit --dry-run --publish brew add <formula>
tool/configs commit --publish brew add <formula>
```

The first shows the edit, the branch, the selected checks, the commit message,
the pull-request body and every command it would run, and writes nothing. The
second asks once, then branches from `origin/dev`, commits with the hooks
enabled, pushes, opens the pull request against `dev` and arms auto-merge, so
the merge happens when `Required checks` pass. There is no unattended mode and
no hook bypass. Drop `--publish` to stop at the commit.

After the manual workflow reaches `master`, refresh the four automatically
permitted inputs and complete a protected release by opening
**Actions → Manual domain release → Run workflow**, selecting
`master`, and run once. The workflow waits for CI, integrates the refresh,
opens the promotion and publishes changed-domain tags after checks and any
required Environment approval. The same one-call entry is:

```sh
gh workflow run manual-release.yml --ref master
```

This manual path ignores the schedule's time/day limit but retains the release
guards. It performs no host activation or Windows Apply. Manual success does
not prove GitHub's scheduled trigger ran. See `CONTRIBUTING.md` for
prerequisites, wait limits and recovery.

Codex, Claude Code, and other Agent Skills-compatible tools can use the
project's `run-version-control-workflow` skill to classify a change, audit Git
policy, prepare work, or plan a domain release. The canonical model-neutral
skill lives under `.agents/skills/`; `.claude/skills/` contains only Claude's
discovery adapter. Audit and release planning are read-only by default.

Codex reads `AGENTS.md` as [project instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
and [discovers skills](https://learn.chatgpt.com/docs/build-skills) directly from
`.agents/skills/`. Invoke this workflow in a Codex prompt with
`$run-version-control-workflow`. External plugin distribution and installation
may differ between Codex and Claude Code; this shared workflow needs no
additional plugin.

The separate sibling `skills` project provides `design-project-governance` for
introducing a project rule. It separates durable policy, human procedure, agent
orchestration, executable enforcement, current adoption, and per-run evidence
before implementation while this repository retains authority for the result.
Source promotion uses `tool/configs plan-promotion` before a
`dev`-to-`master` pull request; promotion is not a release or deployment.

The Justfile exposes the provider checks:

```sh
just doctor
just format-check
just lint
just payloads
just test
just check

just zellij-patch-check v0.45.1
just karabiner-check   # target Mac only; compares the Karabiner payloads
just karabiner-test
```

Observed Darwin settings use the pinned host-document preview/review/save
workflow in [CONTRIBUTING.md](CONTRIBUTING.md#capture-darwin-host-documents).

Host-specific Justfile recipes refuse to use the provider's synthetic
outputs. Evaluate, build and activate a real host from its reviewed private
consumer flake under `configs-hosts/hosts/<host>/`.

### Git commands that get no alias

`unixlike/modules/programs/git.nix` declares this repository's
`programs.git.settings.alias` set and, beside it, a comment naming the Git
commands that deliberately stay unaliased because knowing them is more useful
than shortening them:

- `git show` for the last commit with its patch, `git show --stat` for just
  the summary, and `git show <ref>` for any other commit.
- `git diff` (unstaged) versus `git diff --cached` (staged, aliased `dc`)
  versus `git diff HEAD` (both at once) — the three-way distinction behind
  most "the diff looks wrong" confusion.
- `git log -p -1`, and `git log -p -- <path>` to follow one file.
- `git show HEAD@{1}` with `git reflog` to recover a previous position.
- `git range-diff` to compare two versions of a series.

See the comment in `unixlike/modules/programs/git.nix` for the reasoning; this list only
repeats the names so a maintainer can find them without opening a Nix module.

### Markdown and fuzzy search

`glow README.md` renders a document; `glow` opens the Markdown browser (Enter
opens a document, Esc returns, q quits). Both use the bundled `light` style.
The generated `glow/glow.yml` is read-only: edit `unixlike/modules/programs/glow.nix`,
not `glow config`. XDG configuration is installed on every home; Darwin also
gets the native `~/Library/Preferences/glow/glow.yml` fallback.
`GLOW_CONFIG_HOME` can select an alternative config directory. The glow wrapper
clears `GLAMOUR_STYLE` only for glow so the TUI follows the same style setting
as the CLI. Redirected output uses upstream's uncoloured style unless `--style`
is explicitly supplied; it is not a terminal-colour preview. Only the style is
configured: glow's application defaults include hidden and ignored files
(`all=true`) and adapt the width to the terminal (`width=0`, falling back to 80
columns without a terminal). These differ from the `all=false`, `width=80` in
upstream's first-run generated config file.

In the configured zsh, fzf owns Ctrl-R (history into the buffer, without
execution), Ctrl-T (insert paths), and Alt-C (change directory). Enter accepts;
Esc or Ctrl-C cancels. Ctrl-T and fuzzy path completion support Tab/Shift-Tab
to select multiple entries. Type `**` then Tab for fuzzy completion, for
example `cat **`; ordinary Tab completion remains available. `sk` stays
installed as a separate command without zsh shortcut integration.

fzf uses a reverse list, a border and 40% height with terminal ANSI colours.
The current row uses bold default foreground; the border and separator use
ANSI 8. Matching, walkers and other widget behavior retain upstream defaults.
If the terminal intercepts Alt-C, press Esc then lowercase `c` within 200 ms
(`KEYTIMEOUT=20`). After that timeout Esc enters vi command mode, where `/`
and `n`/`N` still provide native history search.

## Windows

From native Windows, `windows\win-env.ps1` is the one entry point. Each verb
runs one domain script and returns that script's exit status
unchanged; `win-env.ps1 help` prints the table.

```powershell
.\windows\win-env.ps1 setup-dev    # install the contributor toolchain
.\windows\win-env.ps1 validate     # parse every declared payload
.\windows\win-env.ps1 test         # run the Pester suite
.\windows\win-env.ps1 check        # read-only, is an Apply needed
.\windows\win-env.ps1 font         # print the glyph check
```

Arguments after the verb reach the script unchanged, so `check -Feature
terminal` and `capture -SourceRoot <provider-checkout> -Environment <environment-file> -Unit <id>` mean what the sections
below say, and a command the script refuses ends the run at 1. A verb it does
not know is refused with exit status 64, which no check outcome uses. CI and
the hooks use these same public verbs.

`setup-dev.ps1` installs the contributor toolchain once, from
`windows/toolchain.json`. CI installs from the same declaration, so local
verification and the merge gate agree on the versions. Zellij is not part of it
because the manifest already installs the application itself.

The entry point and bootstrap run under the Windows PowerShell 5.1 a host
already has. `apply` and `check` then run setup under PowerShell 7; the module
and the other management scripts are not generally 5.1-compatible.
`setup-dev` is separate from that bootstrap path: it installs Pester and the
other contributor tools and does not install or reconcile the declared host
packages. When PowerShell 7 cannot load Appx, package detection alone starts a
limited 5.1 child from the inbox system path, without a profile, elevation or
`-AllUsers`. It has a 15-second limit and exchanges only validated UTF-8 JSON;
no compatibility module or persistent session is imported into PowerShell 7.

The checks run without that toolchain. A source whose parser is missing is
reported as unverified rather than failing, and `check-desired-state.ps1` and
`test.ps1` exit 69 to say so, which is why a clone without Lua or Pester can
still push Windows work. CI supplies the missing evidence. A Unix-like home
this repository configures carries Pester itself, so `pre-push` there runs
the suite under the host's own `pwsh` and reports a real result.

`bootstrap.ps1 -Check` has a 69 of its own, and it means something else. Its
summary labels an Appx query for which both routes failed as an
`unavailable observation`, instead of reading it as missing. A
prerequisite this host lacks, WinGet or PowerShell 7, is the other case:
`-Check` reports it as 69 rather than installing anything, and 1 under
`REQUIRE_NATIVE=1`. A selected source this host has no parser for is the
third case. Default terminal delegation below its documented boundary is a
`known support limit`; an unreadable build, revision or Terminal version is an
`unavailable observation`. Both retain the existing unverified evidence rank,
but only the latter is described as undecided. The check exits 69 only when
nothing else drifted, because drift outranks unverified evidence, so a host
with both exits 2 and still names every reason. `REQUIRE_NATIVE=1` turns any
unverified evidence into a failure.
`-Check` never installs or changes anything. Apply is explicit:

```powershell
.\windows\win-env.ps1 apply
```

Apply remains idempotent, preserves first-original-file backups under
`%LOCALAPPDATA%\win-env\backups\original`, and records successful state under
`%LOCALAPPDATA%\win-env\state.json`.

### Feature selection

A host does not have to take the whole manifest. `windows/desired/manifest.json`
declares features, every package and managed file belongs to exactly one of
them, and a host picks how many it deploys:

```powershell
.\windows\win-env.ps1 apply -Minimal              # core only: PowerShell 7 and the managed profile
.\windows\win-env.ps1 apply -Feature terminal     # exactly this set, plus what it declares it needs
.\windows\win-env.ps1 apply -Add powertoys        # union with what this host already applied
.\windows\win-env.ps1 apply -All                  # everything the manifest declares
.\windows\win-env.ps1 check                       # verify the selection this host recorded
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

### Host-global WSL settings

The provider does not manage `.wslconfig`. The host owns this file, its
networking policy and any WSL restart. Generation and capture do not modify it.

### Capture a change made in the application

Capture reads supported application settings into version-1 host originals.
SourceRoot identifies a clean provider checkout; Environment names the host
environment declaration. Documents are relative to that declaration. Preview
is the default and `-Save` explicitly writes host originals. It does not edit provider
payloads, create branches, commit, push or open a pull request.

```powershell
.\windows\win-env.ps1 capture -SourceRoot C:\provider -Environment C:\host\environment.json -Unit advancedPaste -Document settings/paste.json
.\windows\win-env.ps1 capture -SourceRoot C:\provider -Environment C:\host\environment.json -Unit advancedPaste -Document settings/paste.json -Save
```

First capture requires an explicit relative Document; later capture may omit it
when the unit already has a connection. Capture never selects features or
enables units.

JsonSubset capture projects only declared object members and takes declared
arrays whole. Unmanaged runtime siblings stay outside the captured desired
state. The supported LocalAppData token is restored; other private values stay
literal host-owned content. Review the preview, save explicitly and regenerate
before Check or Apply. See `windows/examples/README.md` for complete examples.

## Deployment

Unix-like activation and Windows Apply are separate deployments. A common
release deploys nothing; each platform adopts it later through an explicit
change. Domain tags and evidence requirements are defined in
`CONTRIBUTING.md` and `docs/policy/definition-of-done/`.

No activation or Apply is a routine check. Perform either only deliberately on
the matching host.

Scheduled releases use domain-owned SemVer declarations and the standard
GitHub PR/CI/Environment path. Initial Unix-like and Windows versions are
independently 1.0.0. Automatic refresh changes only four permitted inputs; host
adoption and deployment remain explicit. See CONTRIBUTING.md, "Bounded scheduled
release", for setup, the 05/06/07 schedule and original-SHA recovery.
