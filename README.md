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
  windows/win-env.ps1         inspect, generate, export-selection, check, apply,
                              capture, validate, test, setup-dev, font
  windows/desired/            provider manifest and default payloads
  windows/examples/           external host declaration/settings starting point
  windows/src/                PowerShell reconciliation engine
  windows/tests/              native Windows tests

common
  common/                     explicit, independently versioned material only
                              (created only when sharing is justified)
```

The Unix-like flake exports typed constructors through `lib.mkNixos`,
`lib.mkDarwin` and `lib.mkHome`. Real host identities and final outputs live in
the private `configs-hosts` repository. It and the public template now use one
root flake and lock, explicit declarations under `flake-modules/hosts/`, and
shared selected inputs. Their current delivered sources both select the repaired
provider revision `c76752dc`; exact provider and companion refs, qualified
evaluation/build evidence and remaining U1/API release work are recorded in
`docs/status/repository.md`. Initial delivery references retain their original
evidence. Source adoption does not activate any host. The
outputs here use synthetic `fixture-*` and `example` identities to exercise
NixOS CLI, Linux graphics, WSL, Darwin and standalone
Home Manager. They are test instances, not deployment targets. The public
input schema and migration guidance are in `unixlike/api/contract.json`;
`unixlike/tool/contract-inspect` compares pinned source contracts and
`unixlike/tool/standalone-readiness` checks selected standalone prerequisites
without applying them (`docs/status/unixlike.md`).

Graphical Unix-like applications are a separate Home Manager composition
class. Both WSL outputs are command-line configurations and deliberately
exclude Linux GUI applications and WSLg integration. They use a Windows-owned
terminal. Adding WSL GUI support requires a Unix-like policy revision before
any implementation is planned.
The Darwin consumer selects whether Homebrew installs Ghostty; Home Manager
supplies its settings only when that app is selected.

Portable interactive programs are declared once in `homeManager.shared` and
reach the consumer outputs through the provider constructors. Platform Home
Manager classes add only
platform-specific behavior. Darwin Homebrew app selection and lifecycle
belong to the consumer; the provider retains shell integration and settings
for selected apps.

Windows provider defaults are declared in `windows/desired/manifest.json` and
`windows/desired/files/`, including independent WezTerm and Zellij copies.
Hosts select fixed provider source and explicit features in external declarations,
connect their own settings documents, and generate a local configuration before
Check or separately authorized Apply. [Windows usage](#windows) describes this
PowerShell-native flow; authoring, validation and consumption require no Nix.

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

The Unix-like provider exposes read-only contract and standalone prerequisite
tools. Run the reader from a provider revision you already trust, against a
separately fetched candidate source. The consumer lock must name its provider
input `configs` and select `dir=unixlike`:

```sh
# Set trusted_ref, candidate_root and consumer_lock to reviewed values first.
# trusted_ref selects dir=unixlike; consumer_lock must bind candidate_root.
nix run "${trusted_ref}#contract-inspect" -- \
  --candidate-tree "$candidate_root/unixlike" \
  --candidate-source-root "$candidate_root" \
  --candidate-lock "$consumer_lock"
```

Use `--current-tree "$current_root/unixlike"` for a current-to-candidate
comparison; add `--current-source-root "$current_root"` and
`--current-lock "$current_lock"` to bind that source to the current consumer
lock as well.
Use `--legacy` if the current pin has no contract. An optional
`--host-declaration` JSON file contains the constructor, explicit `inputs`,
and Boolean `systemModules`/`homeModules` presence flags; it must come from the
current trusted host, and it must not contain module bodies. For a standalone
home, run:

```sh
nix run "${trusted_ref}#standalone-readiness" -- \
  --declaration "$trusted_host_declaration"
```

This checks the selected system conditions without preparing or activating
the host. Missing and unknown conditions require separate resolution;
a satisfied prerequisite result is
not a runtime or activation result.

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
just karabiner-capture # target Mac only; reads the drift back and commits it
just karabiner-test
```

Host-specific Justfile recipes refuse to use the provider's synthetic
outputs. Evaluate or build a real host from its explicitly selected final
output in the private `configs-hosts/` root flake. Activation follows that
consumer's reviewed procedure and requires an explicit request.

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

From native Windows, `windows\win-env.ps1` is the domain entry point. Each verb
runs one script and returns its status unchanged; `win-env.ps1 help` lists
the targets and their help commands. Windows authoring and use require no Nix.

### Choose source and generate a host configuration

Use a clean local provider checkout at a fixed full commit. Copy
[the host declaration example](windows/examples/README.md) to a separate
host-owned directory, inspect the selected checkout, and set
`environment.json`'s `provider.commit` to the returned commit. The example's
zero commit is a placeholder and is refused for a real checkout.

Run inspect and generation under PowerShell 7 with that checkout's own tools:

```powershell
pwsh -NoProfile -File C:\provider\windows\win-env.ps1 inspect -SourceRoot C:\provider
pwsh -NoProfile -File C:\provider\windows\win-env.ps1 generate -SourceRoot C:\provider -Environment C:\host\environment.json -Output C:\generated\current
pwsh -NoProfile -File C:\generated\current\windows\win-env.ps1 check -Generation C:\generated\current
```

The provider owns defaults in `windows/desired/manifest.json` and
`windows/desired/files/`. The host owns its external declaration and connected
settings documents. Generated configuration and runtime observations are
separate from both. These commands do not fetch or update source.

`features` is an explicit opt-in array. An empty list selects only required
`core`; selected features bring their dependencies, and a new optional feature
is not adopted automatically. The provider declares `core`, `font`, `zellij`,
`terminal`, `wezterm`, and `powertoys`. `terminal` requires `font` and `zellij`;
`wezterm` requires `font`. Unknown features are refused.

Each unit may use provider defaults (`source: configs`, `settings: null`) or
complete host content (`source: host`, a JSON object for JSON units or a string
for text/script units). Host content is not merged with provider defaults.
Connections are explicit relative paths under the host directory; units cannot
share a settings document. `enabled: false` stops managing that unit and its
related profile hook without removing an existing file or hook. Deselecting a
feature does not uninstall software or restore settings.

Generation requires the selected payloads' native parsers and source-bound,
clean Windows tools. Environment/settings JSON must be strict UTF-8; an optional
UTF-8 BOM is accepted. Duplicate or case-ambiguous keys, malformed input and
hidden source-index changes are refused. Disabled or unselected documents
retain structural checks and receive active validation when reselected.

Keep output outside provider source and host originals. Run the generated
entry point with `-Generation`; the declaration owns its selection, so
`-Feature`, `-Add`, `-Minimal` and `-All` cannot accompany `-Generation`.
Changing source, selection, originals, payloads or tools requires regeneration.
A failed generation publishes no first result and preserves a previous result,
which still refuses verification against changed inputs. Generation does not
Apply.

### Read-only verification and explicit deployment

`check` never installs or writes host desired state. It returns 0 for
converged, 2 for drift, 69 for unavailable evidence and 1 for failure.
Drift outranks unavailable evidence; `REQUIRE_NATIVE=1` turns unavailable
evidence into failure. Known support limits and unavailable observations remain
distinct in the output.

The initial client baseline is Windows 10 IoT Enterprise LTSC 21H2 x64,
build 19044. Default terminal delegation is explicitly outside its guarantee;
Terminal settings, profiles and fonts remain separately checked. Current
source/runtime evidence and remaining acceptance are in
[Windows status](docs/status/windows.md). A generation or successful Check
does not authorize Apply. Deploy only on an explicit request:

```powershell
pwsh -NoProfile -File C:\generated\current\windows\win-env.ps1 apply -Generation C:\generated\current
```

The entry point/bootstrap also run under inbox Windows PowerShell 5.1.
Management uses PowerShell 7; generation requires it already available.
Generated integrity checks occur before bootstrap installation. When
PowerShell 7 cannot load Appx, package observation uses a limited, no-profile
inbox 5.1 child with a 15-second limit and validated UTF-8 JSON; it imports no
compatibility module or persistent session. Missing WinGet, PowerShell or
parsers remains read-only unavailable evidence under Check.

Apply preserves first-original-file backups under
`%LOCALAPPDATA%\win-env\backups\original` and records attempt outcomes under
`%LOCALAPPDATA%\win-env\state.json`. Runtime state is not the host declaration.

### Migrate an earlier selection

Preview the legacy selection without changing originals or deploying:

```powershell
pwsh -NoProfile -File C:\provider\windows\win-env.ps1 export-selection -SourceRoot C:\provider -State C:\host\legacy-state.json
```

The output is a proposal and names migration blockers, not a saved declaration.
Omit `-State` for a first-use core-only proposal. Schema 1 needs its recorded
provider manifest available in the local clone. Earlier direct runner selection
flags still serve the legacy path; use external declarations for generated
configurations.

WSL VM settings (`.wslconfig`), personal custom layouts and layout hotkeys
belong to the host and are no longer provider-managed units. A retired WSL
selection is an explicit migration blocker. Preserve those host files and
manage them separately; exporting or generating never restarts WSL. Generic
FancyZones default layouts can use a complete host document. Runtime/session
files remain outside desired inputs.

### Capture a change made in an application

Capture reads supported app settings into host-owned originals. First select
the feature in the external environment and keep the requested unit enabled.
For this example, select `powertoys` before requesting `advancedPaste`:

```powershell
pwsh -NoProfile -File C:\provider\windows\win-env.ps1 capture -SourceRoot C:\provider -Environment C:\host\environment.json -Unit advancedPaste -Document settings/paste.json
```

This defaults to a JSON preview and writes no original. Review the complete
`source: host` document and first connection. Add `-Save` only to write those
originals explicitly; `-Save -WhatIf` keeps the same prepared preview without
writing. Capture never selects a feature or enables a unit automatically.

`-Unit` uses case-sensitive IDs. First capture requires an explicit relative
`-Document` path. Later capture uses the existing connection, so omit Document;
capture cannot rename it. When capturing multiple units, supplied document
paths align in the same order and must be unique.

`JsonSubset` captures the selected document's object keys and owns arrays whole;
undeclared object keys stay outside desired inputs. Missing keys or incompatible
shapes refuse rather than inventing deletion. Later host capture uses its own
connected source, not newer provider defaults. Generated Terminal profiles and
externally managed PowerShell blocks stay outside capture ownership.

All requested units prepare and validate before Save. A first document is
written before its connection; a connection failure leaves an inert document.
Read each unit's completed, failed, unconnected or pending result. An explicit
retry must name a matching unconnected document; conflicting content refuses
overwrite. There is no multi-file atomicity or automatic rollback.

Save changes neither provider defaults, generated output, observed app files
nor Git state. Legacy `-Feature`, `-Id`, `-Branch` and `-Publish` capture
arguments are unsupported. Host publication follows its own repository
workflow. Private host originals do not become public provider contributions
automatically.

Regenerate after Save before Check or any separately authorized Apply.
The old generation identity becomes stale intentionally. Capture/Save does not
Apply, install software or certify native runtime behavior.

### Contributor commands

```powershell
.\windows\win-env.ps1 setup-dev    # install the contributor toolchain
.\windows\win-env.ps1 validate     # parse provider payloads
.\windows\win-env.ps1 test         # run the Pester suite
.\windows\win-env.ps1 font         # print the glyph check
```

`setup-dev` installs the contributor tools from `windows/toolchain.json`
separately from host bootstrap. CI uses the same declaration. Missing Pester
or a required parser is unavailable evidence (69), or failure when required;
foreign-host checks cannot replace selected native Windows evidence.

## Deployment

Unix-like activation and Windows Apply are separate deployments. A common
release deploys nothing; each platform adopts it later through an explicit
change. Domain tags and evidence requirements are defined in
`CONTRIBUTING.md` and `docs/policy/definition-of-done/`.

No activation or Apply is a routine check. Perform either only deliberately on
the matching host.
