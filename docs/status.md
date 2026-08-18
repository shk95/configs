# Status and decisions

## Three-domain direction

The repository now treats `unixlike`, `windows`, and `common` as independent
configuration domains. This supersedes the initial goal of using the flake as
the composition authority for native Windows.

The decision is driven by the evaluation boundary: Linux and macOS can consume
Nix configuration directly, while Windows previously depended on a Unix-like
host to render its committed desired state. That dependency forced platform
differences into shared modules, made Windows compatibility a foreign-host
concern, and coupled otherwise independent development and release work.

The durable direction is:

- the flake remains authoritative for Unix-like hosts;
- Windows owns a native source manifest, payloads, tests, and deployment flow;
- common material exists only inside an explicit `common/` domain;
- common is exceptional, independently versioned, and never deployed directly;
- platforms adopt common work asynchronously, preferably by copying it and
  taking local ownership;
- similar platform implementations may diverge without creating drift debt.

The complete model is in `docs/architecture.md`.

## Unix-like Home Manager and package ownership

Every current Unix-like home imports `homeManager.shared`: standalone Home
Manager on Ubuntu WSL, Home Manager embedded in NixOS-WSL, and Home Manager
embedded in nix-darwin. Shared modules own portable shell behavior, configured
programs, and interactive command-line packages. The platform classes are
overlays, not parallel implementations:

- `homeManager.wsl` contains behavior required by both WSL flavours;
- `homeManager.wslStandalone` supplies the account and Nix settings that a
  system integration would otherwise supply;
- `homeManager.desktop` contains graphical Unix-like programs;
- `homeManager.darwin` contains macOS-only user behavior.

Packages with Home Manager options are owned by their `programs.*` feature
modules. Unconfigured portable CLI packages are owned by
`homeManager.shared`. A package belongs in a system module only when a service,
activation script, or root/system account needs it; installing the same
interactive package into both HM and `environment.systemPackages` is not a way
to make it more available. The Darwin system `EDITOR` therefore uses an
absolute Neovim store path while the user-facing Neovim package remains
HM-owned. The only identical derivations remaining in both final profiles are
`zsh` and `nix-zsh-completions`: nix-darwin contributes them for the global
shell initialization while HM contributes them for the portable per-user zsh
configuration. They are evaluator-owned requirements rather than duplicate
package-list entries.

SDKMAN is adopted but not owned. `homeManager.shared` sources
`$HOME/.sdkman/bin/sdkman-init.sh` only when that file exists, last in the zsh
`initContent`, because SDKMAN rewrites PATH and declarative packages must keep
precedence. Installing it stays with the user; there is deliberately no package,
activation script, or generated payload for it, and no bash or PowerShell
equivalent of the hook. The JVM toolchain is split on purpose: `gradle` is a
shared Nix package, while JDK distributions and their version switching belong
to SDKMAN. Declaring a JDK in Nix as well would put two version authorities on
one PATH, and the later SDKMAN initialization would win. The Windows domain has
no SDKMAN equivalent and needs none — SDKMAN is a POSIX shell-function
installer, so JVM work on a Windows host happens inside a WSL Unix-like home.
Its absence from `windows/desired/manifest.json` is a decision, not a gap.

Homebrew owns Mac App Store applications, macOS GUI applications, and the few
command-line tools that cannot use the shared Nix package. In the current lock,
`bettercap` is broken on Darwin, so Homebrew owns it on macOS while shared HM
installs it on Linux. Ghostty is another intentional split: Homebrew owns the
macOS application and HM owns its cross-Unix configuration with
`programs.ghostty.package = null` on Darwin. `homebrew.onActivation.cleanup` is
explicitly `"none"`; the generated Brewfile is an install/upgrade inventory,
not an exclusive declaration that removes manually installed items.

The typed identity contract and its values are separate. `identity.nix`
declares the flake-parts options, while `inventory.nix` contains the tracked,
non-secret usernames, Git identity, host name, and target system needed for
pure and reproducible flake outputs. Moving those values to environment
variables would require impure evaluation and would make output names depend on
the invoking shell.

## Unix-like desktop boundary

`homeManager.shared` contains portable command-line behavior, not every program
that happens to run on more than one Unix-like kernel. Graphical terminal
emulators belong to `homeManager.desktop`, which Darwin consumes and both WSL
outputs omit. A future graphical Linux configuration can adopt the same class
without turning WSL into a desktop host by implication.

WezTerm and Ghostty are the desktop terminals. Home Manager installs the
D2Coding Nerd Font package and configures its internal
`D2KodingLigature Nerd Font Mono` family for both terminals. On Darwin, WezTerm
also reads Home Manager's nested font directory explicitly because CoreText
does not discover that copied hierarchy recursively. Home Manager state version
25.11 uses `targets.darwin.copyApps` instead of the legacy `linkApps`, so the
Home Manager-owned WezTerm bundle remains under `~/Applications/Home Manager
Apps` but is a Spotlight-compatible copy rather than a Nix-store symlink.
Alacritty is fully inactive: there is no Alacritty package, Home Manager module,
or generated configuration. The stale Darwin Dock entry was removed; a future
adoption should add its package, configuration, and Dock ownership together.

Ghostty keeps its native `xterm-ghostty` terminfo locally. Its shell integration
tries to install that entry on SSH destinations and falls back to
`xterm-256color` only when the destination cannot accept it. Globally
downgrading `TERM` would hide capabilities on every host to accommodate the
few that need a fallback.

## Windows authority split

The Windows domain is independent:

- `windows/desired/manifest.json` is its single source manifest.
- `windows/desired/files/` contains Windows-owned payloads.
- PowerShell reads and hashes that desired-state tree directly.
- Native desired-state validation, Pester, and `bootstrap.ps1 -Check` provide
  Windows evidence.
- Nix has no Windows options, package output, renderer, or generated consumer.
- Unix-like and Windows WezTerm and Zellij payloads are independent copies and
  may diverge.
- Hooks and CI no longer make a Windows artifact depend on Unix-like evaluation.

Windows desired state is selectable. Manifest schema 2 declares seven features
(`core`, `font`, `zellij`, `terminal`, `wezterm`, `powertoys`, `wsl`) and every
package, managed file, the font, and the terminal delegation is owned by exactly
one of them. `bootstrap.ps1 -Minimal` deploys `core` alone, which installs
PowerShell 7 and the managed profile and touches no font, registry value, or
application setting. State schema 2 records the selection; a schema 1 state is
read as a full deployment, so a host that applied before this change keeps
exactly what it has.

Two boundaries are decisions rather than accidents. `terminal` requires `zellij`
because `files/terminal/settings.json` is owned whole under `ExactJson` and
carries a profile that launches `zellij.exe`; splitting that payload or adding a
merge comparison mode was rejected as more expensive than installing one small
package. `wezterm` requires no font feature because `files/wezterm/fonts.json`
asks for JetBrainsMono, which this manifest does not install, and never for
D2Koding. PowerToys stays one feature because
`files/powertoys/settings.json` already owns the per-module enable map; a
second selection axis over the same modules would have two sources.

The desired-state hash is scoped to the selected features plus `manifest.json`.
A whole-tree hash reported drift for payloads a host never deploys and forced an
Apply that could not change anything on it.

No explicit `common/` component has yet been justified or created.

Local hooks are not a Windows evidence source. `modules/powershell.nix` installs
a Unix-like `pwsh` into every home this repository configures, so a Linux or
macOS clone always has one. Treating it as the Windows shell ran the Windows
scripts under foreign tooling, and because `check-desired-state.ps1` requires
`zellij.exe` and `test.ps1` requires Pester 5.7.1, it also made the hook's own
"CI must supply evidence" branch unreachable and left Windows work unpushable
from the hosts where it is most often authored. `pre-push` therefore accepts
only `pwsh.exe` and otherwise reports the Windows checks as unverified.

The merge gate is CI. The `windows-latest` job installs Pester, Lua, and Zellij,
then runs the desired-state check and the Pester suite, and `Required checks`
demands success whenever the change is in Windows scope. A Windows change
authored on Linux or macOS is therefore verified natively at the pull request
rather than locally. `bootstrap.ps1 -Check` stays outside CI because a fresh
runner has no host state to observe; it is host evidence for a `windows-v...`
tag, not a merge condition.

Windows tests target Pester 5.7.1 through `windows/tools/test.ps1`. The exact
version is shared by local native verification and CI so Pester discovery,
scope, and assertion behavior cannot silently change with a runner image. Test
setup runs in `BeforeAll`, and assertions use the parameterized Pester 5 syntax.

## PowerShell 7 ownership

PowerShell 7 is configured in both deployable domains without a cross-domain
runtime dependency. The Unix-like Home Manager feature owns the package and
the CurrentUserAllHosts profile for Linux, WSL, and macOS. Windows continues to
own its WinGet package declaration, managed profile payload, and profile hook.

The two profiles independently adopt the same small, platform-neutral
interactive policy: PSReadLine suppresses duplicate history entries, moves the
cursor to the end of a recalled history match, and uses history prediction when
the installed PSReadLine supports it. The policy runs only in an interactive,
non-redirected ConsoleHost and produces no output, because profiles may also be
loaded by SSH, Git, scp, and other protocols.

This similarity is not yet sufficient evidence for a `common/` component. The
copies remain locally owned and may diverge. Promotion can be reconsidered only
after their semantics remain stable across independent platform validation and
release cycles.

The Unix-like Zellij keymap was adopted by copying the Windows implementation.
The copies intentionally differ in platform-owned shell and session values and
have no synchronization dependency. Promotion to `common` remains deferred
until both implementations demonstrate stable semantics across independent
version and validation cycles.

## Versioning and deployment decision

The repository retains `dev` and `master` for shared source integration, but a
branch no longer represents simultaneous deployment readiness for all domains.
Releases are identified independently:

- `unixlike-vYYYY.MM.DD[.N]`;
- `windows-vYYYY.MM.DD[.N]`;
- `common-vYYYY.MM.DD[.N]`.

Unix-like activation and Windows Apply consume their respective domain
releases. A common release deploys nowhere and is adopted later by a separate
consumer change. A tag certifies only its domain, even when unrelated domain
history exists at the same commit.

## Version-control workflow ownership

Repository-wide version-control work is a narrow `repository` governance scope
rather than part of one of the three configuration domains. It owns policy
dispatch and agent workflow mechanics, creates no host output, and has no
release tag.

GitHub milestones are now the planning surface for scoped outcomes. They remain
metadata over independently reviewable issues: repository documents own
architecture and current support decisions, domain tags own release
certification, and explicit commands own deployment. The first adoption is the
`unixlike: NixOS GUI host foundation` roadmap. Milestone naming, required
description sections, issue membership, and closure are reviewed manually by
the repository maintainer; automated remote enforcement is deferred until the
manual workflow demonstrates a recurring failure that justifies it.

Durable judgement remains in `AGENTS.md` and the architecture documents. The
repeatable agent procedure is implemented once as an Agent Skills
open-standard skill under `.agents/skills/`. Model-specific skill locations
only provide discovery adapters. Neither Codex nor Claude becomes the workflow
authority.

The initial audit found strong branch and commit adherence but no domain tags,
so the release path remains unexercised. It also found that the existing hooks
and CI invoke Unix-like checks for unrelated changes, which conflicts with
native Windows independence. The governance refactor therefore adds
domain-aware dispatch and a read-only release planner before any real tag is
created.

The follow-up remote audit found protection enabled on both `dev` and `master`:
pull requests and current-branch checks are required, administrators are
enforced, conversations must be resolved, and force pushes and deletions are
disabled. Both branches now require only the stable `Required checks` gate, and
the repository-governance PR and its post-merge `dev` run demonstrated that
selected repository checks pass while unrelated domain jobs skip.

Source promotion is explicitly one-way: only same-repository `dev` may open
against `master`, and the result is a merge commit representing source
acceptance rather than release. `dev` remains strictly up to date for ordinary
integration. `master` uses non-strict status checks so an earlier promotion
merge commit does not force a meaningless `master`-to-`dev` reverse merge. CI
source validation, one open promotion at a time, merge commits, and the
prohibition on direct changes retain the safety boundary. The source gate was
observed on `dev` and `master` before the remote migration was completed.
Repository settings now allow merge commits while disabling squash and rebase
merging, and the remote audit verifies both settings together with branch
protection.

Governance rules now follow an explicit decomposition contract: durable
judgement and invariants, human procedure, agent orchestration, deterministic
enforcement, and execution evidence have distinct owners. The generic
`design-project-governance` skill was extracted into the sibling `skills`
project because it contains no branch names, repository paths, release choices,
or current state from this repository. This repository retains the resulting
policy, procedure, enforcement, migrations, and evidence.

## Payloads were verified by nobody

Twelve files under `assets/` — eight WezTerm Lua modules, a Lua template, a
WezTerm JSON manifest, the Zellij KDL, and the PowerShell profile — were parsed
by nothing, on any host, in any CI job. `modules/zellij.nix`,
`modules/wezterm.nix` and `modules/powershell.nix` deliver them with `.source`,
which copies a file into the store without reading it, so a syntax error
evaluated, built, activated, and failed for the first time when the application
started. `tool/checks/*` ran alejandra, statix, deadnix and `nix eval`, all of
which read only Nix, and the flake declares no `checks` output. Their Windows
counterparts had been parsed by native zellij, luac, jq and the PowerShell
parser the whole time, including the `.lua.example` template.

The cause was structural rather than an oversight. Ownership decomposes by
domain, and the repository used that same partition for verification, which
decomposes by format. Windows noticed because its manifest already had to say
what each managed file was in order to reconcile it, so a `Parser` field was
natural there. Nix never had to know, so nothing on the Unix-like side was ever
in a position to ask. The validators were present the entire time: `lua5_4` and
`stylua` sit in `modules/flake/dev-shell.nix`, and every configured host
installs Zellij.

`assets/payloads.json` now declares each payload's format and
`tool/checks/payloads` parses them, with coverage enforced in both directions
so a payload added without a declaration fails rather than escaping quietly,
and a declared format with no validator fails too. It is an adoption by copying
of the Windows manifest's idea, which is the mechanism the architecture already
prescribed; the two declarations stay independent.

## Check evidence states

A check has three possible outcomes — verified, failed, and unverified — and
only the first two could be expressed. A shell exit status carries a binary
answer, so every place that needed the third state invented one, and eight call
sites disagreed. `pre-push` reported an unverified Windows check and passed;
`check-desired-state.ps1` and `test.ps1` threw before validating anything;
`Test-WinEnvSourceFile` skipped a missing Zellij silently and so reported
unverified as valid; the Unix-like branch of both hooks had no detection at
all; `doctor.sh` accepted a shell that `pre-push` rejects. This document's own
requirement is unverified rather than valid, and none of those answers were
unverified except the first.

The failure being prevented is a native Windows clone that cannot push its own
domain's work, and its mirror, a clone reporting a payload as verified when
nothing parsed it. The owning scope is `repository`. The architecture already
reserved the position: root tooling may dispatch domain checks without owning
their semantics, and must not turn one domain's success into a prerequisite for
a change in another.

The invariant is tool independent. A prerequisite the host cannot supply is
reported as unverified, never as valid and never as failure. Exit status 69
carries it, a failure outranks it, and `REQUIRE_NATIVE=1` converts it into a
failure. Hooks leave that unset because the local gate is advisory. CI sets it
because the merge gate is the one place where "nobody could check this" must
not pass.

Deterministic enforcement lives in `.githooks/evidence`, which both hooks
source, and in each domain's own checks, which decide what their prerequisites
are. The hooks select which checks run and never decide whether a missing tool
is a failure. Domains do not share an implementation of the probe; each detects
its own tooling in its own language, which is the ordinary duplication this
repository prefers over a cross-domain abstraction.

Evidence is the fixtures in `tool/version-control/test`, which run the real
pre-push hook against a stand-in check and require that 0 passes, that any
other status blocks, that 69 passes while reporting, and that 69 blocks under
`REQUIRE_NATIVE`. Migration is staged: hooks and `doctor.sh` consume the
protocol first, then the Unix-like and Windows checks are converted to emit it.
The superseded behaviour can be removed once no check reports a missing
prerequisite through `throw` or an unguarded command.

## Initial monorepo convergence

The repository originally converged four projects into one flake-composed
configuration model. The dendritic Unix-like structure remains useful:
flake-parts evaluates feature files collected by import-tree, deferred module
classes merge feature contributions, and one composition module assigns those
fragments to Unix-like hosts.

Content and findings came from:

- `nix-wsl`: dendritic Unix-like structure, verification boundaries, and WSL
  findings;
- `term-config`: WezTerm behavior that was initially shared across platforms;
- `win-env`: Windows drift detection, backup, safe Apply, and reconciliation;
- `nix-config`: Darwin setting values, without preserving its prototype wiring.

`win-env` reconciliation semantics remain in the Windows domain. The
cross-domain flake composition introduced during convergence was removed when
Windows desired state became directly owned under `windows/desired/`.

## History boundary

This monorepo started a clean history because convergence changed ownership and
composition rather than merely moving four directory trees. The initial source
revisions were:

- `term-config` `master`: `9282d19`
- `win-env` `master`: `dc5d27d` (`v0.1.0`)
- `win-env` `dev`: `64f0b90`
- `win-env` local `draft`: `dd13282`
- `nix-wsl` `dev`: `1875f8f`
- `nix-config` `master`: `84c05c2`
- `nix-config` remote `darwin`: `5f94d5d`

These identifiers are provenance, not Git parents. The old repository-wide
`vYYYY.MM.DD` release convention is superseded by domain-prefixed tags.

## Verification observed during initial convergence

- The standalone WSL Home Manager activation derivation evaluates.
- The NixOS-WSL system derivation evaluates.
- The nix-darwin system derivation evaluates for `aarch64-darwin`.
- The former Windows bundle built and its JSON/Lua payload was checked in the
  derivation before the authority split.
- No Unix-like configuration was activated.
- No native-Windows Apply was performed; native Pester and `-Check` remain
  required evidence for Windows runtime behavior.

These observations are historical evidence, not certification under the new
domain release model.

## Import-order caveat

Auto-imported deferred Unix-like modules do not preserve the former hand-written
import order. List-valued options can therefore produce different store hashes
even when their element set is unchanged. Features whose list order carries
meaning must use explicit ordering or a keyed attribute model instead of
relying on file collection order.
