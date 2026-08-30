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

`windows/desired/files/terminal/settings.json` and
`windows/desired/files/wezterm/config/appearance.lua` adopted the Unix-like
light-theme decision (#35) by copying: both now select the light member of the
same Catppuccin family, `Catppuccin Latte`, the WezTerm payload as its built-in
scheme name and the Windows Terminal payload as an inline `schemes` entry using
the published `catppuccin/windows-terminal` port, because Windows Terminal does
not ship Catppuccin as a built-in scheme. As with the other rows in this list,
each copy is Windows-owned from the moment it lands and may diverge from the
Unix-like source without that being a failure. The adoption also re-judged
`useAcrylic` and `useAcrylicInTabRow`, which the prior dark scheme left `true`,
and turned both off: acrylic blends the window with whatever sits behind it, so
its result is inherently unpredictable, and Catppuccin Latte's foreground
already runs a moderate ~7:1 contrast against its background (`#4C4F69` on
`#EFF1F5`) with less margin than the dark scheme it replaced to spend on an
unpredictable blend. `windows/desired/files/terminal/settings.json` is plain
JSON and carries no comment syntax, so this reasoning is recorded here rather
than beside the setting.

Windows desired state is selectable. Manifest schema 4 declares seven features
(`core`, `font`, `zellij`, `terminal`, `wezterm`, `powertoys`, `wsl`) and every
package, managed file, the font, and the terminal delegation is owned by exactly
one of them. `bootstrap.ps1 -Minimal` deploys `core` alone, which installs
PowerShell 7 and the managed profile and touches no font, registry value, or
application setting. State schema 2 records the selection; a schema 1 state is
read as a full deployment, so a host that applied before this change keeps
exactly what it has.

Three boundaries are decisions rather than accidents. `terminal` requires
`zellij` because `files/terminal/settings.json` is owned whole on
write and carries a profile that launches `zellij.exe`; splitting that
payload or adding a merge comparison mode was rejected as more expensive than
installing one small package. `wezterm` requires `font` because
`files/wezterm/fonts.json` leads with `D2KodingLigature Nerd Font Mono` for
Hangul coverage: the list names only D2Koding families, and the concrete
alternative already on a default Windows install, Malgun Gothic, is not
fixed-pitch and would misalign any line mixing Korean and Latin.
Declaring the dependency, the same way `terminal` already does, was cheaper
than that misalignment; a host selecting `wezterm` alone now installs `font`
too, reported as `added by dependency`. PowerToys stays one feature because
`files/powertoys/settings.json` already owns the per-module enable map; a
second selection axis over the same modules would have two sources.

The read side of that one file carries a tolerance the write side does not.
Windows Terminal materialises the profiles its fragment extensions and dynamic
generators discover back into `settings.json` so they can be edited: on the
maintainer's host it added a `Git Bash` profile carrying `"source": "Git"`
beside the two the payload declares, seconds after Apply had overwritten the
file. Under `ExactJson` that reserialisation was drift, so post-apply
validation threw before `Write-WinEnvState` ran and left a fully deployed host
unrecorded, and every later `-Check` reported the same drift on any host that
actually runs Windows Terminal. The entry now declares
`ExactJsonWithGeneratedProfiles`: everything outside `profiles.list` is still
compared exactly, each declared profile is matched by `guid` and must be equal,
and an undeclared entry is accepted only when it carries a non-empty `source`,
which is how Windows Terminal records that a generator produced it. An
undeclared profile without a `source` remains drift, because a person or
another tool wrote it. This does not reopen the merge decision above. Apply
still writes the whole payload, the payload still declares neither `Git Bash`
nor `disabledProfileSources`, and nothing merges the host's file on write; the
tolerance is a read-side statement about one application co-owning one file,
which is why it is a declared comparison mode on a single manifest entry that
the loader refuses on an entry whose parser is not `Json`. Declaring a mode no
earlier loader can honour is a manifest shape change, so this is a
`SchemaVersion` bump, 3 to 4, with `ProjectVersion` moving 0.4.0 to 0.5.0 the
way the schema 2 to 3 bump moved 0.3.0 to 0.4.0. Without it a manifest paired
with an older module would load as schema 3 and then fail at comparison time
as an unknown mode, rather than saying the schema is unsupported. **No
`state.json` schema changes**: an applied host keeps its recorded selection,
sees a changed desired-state hash and a higher project version, and redeploys.

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

## Windows 10 support boundary

Windows 10 was two reported symptoms rather than a recorded boundary. A sweep
over three items of the manifest surface — the default terminal delegation and
the two `Appx` items — assigns each exactly one of the evidence states defined
in `docs/architecture.md`. All three are unverified on Windows 10, for two
different reasons, and `bootstrap.ps1 -Check` reports none of them that way
today.

The default terminal delegation is a read-back, not a behavior check.
`Set-WinEnvTerminalDelegation` writes `DelegationTerminal` and
`DelegationConsole` under `HKCU:\Console\%%Startup`, and
`Test-WinEnvTerminalDelegation` reads those two values back from the same key
and compares them to `manifest.Terminal`. Microsoft states the condition under
which the setting is supported: the default terminal application requires
Windows 11 22H2, or Windows 10 22H2 at OS build 19045.3031 with KB5026435, and
Windows Terminal 1.17 or later. The same document names this key, these two
value names, and the two GUIDs this manifest carries for Windows Terminal, so
the values written here are the documented ones. The boundary is therefore an
OS build plus an application version, not a Windows release name. Below either
half of it the host accepts the write, the read-back passes, and the setting is
ignored: `-Check` exits 0 and never reports drift for a setting that does
nothing. That false pass is the one outcome the evidence contract has no room
for, and deciding the item against the documented condition rather than against
the write (#53) is the fix. Above the boundary the read-back still observes no
handoff. No Windows 10 host at build 19045.3031 was available, so the item is
recorded unverified against its documentary source rather than closed as works.

The two `Appx` items are supported on Windows 10 and undetectable there by the
route this domain uses. Those are different statements and the record keeps
them apart. PowerToys, which contains Command Palette, requires Windows 11 or
Windows 10 version 2004 (20H1, build 19041) or newer; Windows Terminal requires
Windows 10 2004 (build 19041) or later. Both therefore run on a supported
Windows 10 host, and neither item is absent or unsupported there. What does not
work is the question. `Get-AppxPackage` backs both the `powertoys` feature's
`Microsoft.CommandPalette` precondition and the `Microsoft.WindowsTerminal`
package's `Appx` detection, and Microsoft's Windows module compatibility table
footnotes `Appx` with "Must use Compatibility Layer with PowerShell 7.1". This
domain runs PowerShell 7 and both call sites pass
`-ErrorAction SilentlyContinue`, so a route that cannot answer returns nothing
and is read as absence. The precondition then reports the package missing and
Apply refuses the feature; the package either reports missing, so Apply
reinstalls an installed Windows Terminal, or disagrees with the WinGet
registration and reports a detection conflict that blocks Apply. An
unavailable route must report unverified, never absence. The open
Appx-detection change (#37) owns that fix and moves both items to unverified;
Windows version detection (#38) owns the mechanism the delegation condition
needs, and this record builds none of its own. That mechanism now exists as
`Get-WinEnvWindowsBuild`, recorded under "`.wslconfig` content is selected by
the host's Windows build" below; #53 decides the delegation item against it.

Declining `terminal` and `powertoys` at selection time removes all three items
from a host's check: `setup.ps1` evaluates the delegation only when `terminal`
is selected and a feature's preconditions only when that feature is selected,
so `-Minimal` reaches none of them. That is a mitigation available today rather
than a fix, and a `-Minimal` run is evidence for none of these three items.

The sweep is deliberately narrow and its edge is part of the record. It did not
examine the `WinGet` and `Command` detections, the font download and its
registry registration, the PowerToys lifecycle, the managed-file targets and
their packaged `LocalState` paths, an unpackaged Windows Terminal installation,
or PowerShell 7 itself; `.wslconfig` is recorded separately below. Windows releases older
than 10, Windows Server, and non-x64 hosts stay out of scope. Those items are
not known to be safe on Windows 10; they are unexamined.

The repository maintainer owns this boundary. It is a manual invariant: no
check can produce the record, and `-Check` has no way to express its conclusion
today — the Windows half of the staged migration declared in "Check evidence
states" below — because it exits 0 or 2 and reports its `unverified` list
without letting it affect the status. #54 owns that conversion.

Sources for the claims above:

- Group Policy for Windows Terminal —
  https://learn.microsoft.com/en-us/windows/terminal/group-policy
- Windows Terminal installation —
  https://learn.microsoft.com/en-us/windows/terminal/install
- How to Install PowerToys on Windows 11 and Windows 10 —
  https://learn.microsoft.com/en-us/windows/powertoys/install
- PowerShell 7 module compatibility (Windows) —
  https://learn.microsoft.com/en-us/powershell/windows/module-compatibility
- Windows Terminal product repository — https://github.com/microsoft/terminal

## `.wslconfig` content is selected by the host's Windows build

`.wslconfig` is host-global: one file per machine, read by the WSL VM for every
distribution on it, so a wrong value is not scoped to one distro. The option
set it may carry is not the same on every Windows build, and the boundary is
not where "Windows 10 versus Windows 11" puts it. Microsoft's `.wslconfig`
reference footnotes each key — footnote 1 means "only available on Windows 11",
footnote 2 means "require Windows 11 version 22H2 or higher". Against the four
keys this repository sets:

| Key | Section | Gate | Payload |
| --- | --- | --- | --- |
| `networkingMode=Mirrored` | `[wsl2]` | Windows build, 22H2 or later | 22H2 payload only |
| `hostAddressLoopback=true` | `[experimental]` | Windows build, 22H2 or later; also requires `networkingMode=mirrored` | 22H2 payload only |
| `bestEffortDnsParsing=true` | `[experimental]` | Windows build, 22H2 or later; also requires `dnsTunneling=true` | 22H2 payload only |
| `autoMemoryReclaim=Gradual` | `[experimental]` | WSL **application** version, not the Windows build | **both** payloads |

`autoMemoryReclaim` arrived with the Microsoft Store WSL 2.0.0 release in
September 2023 alongside `sparseVhd` and carries no footnote, so it is gated by
the installed WSL application and works on Windows 10 with a recent WSL.
Dropping it from the lower payload would remove a setting that host honours,
which is a regression dressed as a version fix. Every key in either payload
traces to a row above; no `firewall` value appears in either, which `AGENTS.md`
forbids without explicit direction.

Because three of the four keys share one bound, the payloads are named after
the capability they assume rather than after a Windows release. A Windows 11
21H2 host — build 22000, unmistakably Windows 11 — honours none of the three
22H2 keys and belongs on the same side as Windows 10, so a release name would
encode a boundary the option set does not have. The two payloads are
`files/wsl/mirrored-networking.wslconfig`, which is the previously deployed
content unchanged, and `files/wsl/nat-networking.wslconfig`, which carries only
`autoMemoryReclaim` and leaves the host on WSL's default NAT networking.

The manifest expresses this with **one entry and alternative sources**, not two
entries with mutually exclusive conditions. A single `ManagedFiles` entry keeps
one `Id`, one `Target`, one `Compare` mode and one owning feature, so drift,
backup, and deselection continue to reason about one logical file; the cost is
that `Source` stops being a scalar and every consumer must go through the
resolver. Two entries would have kept a scalar `Source` everywhere, at the
price of two `Id`s competing for one `Target` and a new invariant nothing
enforces today: exactly one entry must select on any host. A manifest whose
conditions overlapped would deploy twice, and one whose conditions all failed
would deploy nothing, and neither failure is visible in the file the manifest
declares. The chosen shape makes that invariant structural instead: a
conditional entry declares `Sources` as an ordered list whose bounds descend
strictly and whose **last variant carries no condition**, so resolution is a
total function and "exactly one variant applies" cannot be violated by editing
the manifest. `Get-WinEnvManifest` rejects a `Sources` list that breaks either
rule, so the invariant fails at load rather than at deployment.

Windows build detection reads `[Environment]::OSVersion.Version.Build` and
compares the **build alone**, not the build and revision.
`[Environment]::OSVersion.Version.Major` is `10` on Windows 10 and Windows 11
alike, so a major-version comparison would silently classify every Windows 11
host as Windows 10; the build is the discriminator, Windows 11 begins at build
22000, and the bound for this option set is Windows 11 22H2, build 22621. The
source is in-process and cannot be blocked by a stopped WMI service or a
restricted registry hive, which `Get-CimInstance Win32_OperatingSystem` and
`HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion` respectively can be;
PowerShell 7 runs on .NET 5 or newer, where `OSVersion` is taken from
`RtlGetVersion` and is not capped by the Win32 compatibility-manifest shim.
Microsoft's footnote links the 22621.2359 release announcement, but the
revision is a servicing level rather than an OS version: pinning it would
classify a 22621 host that is merely behind on cumulative updates as below the
bound, and this source carries no UBR, so a revision comparison would need a
second and more failure-prone source to decide a boundary the documentation
states in builds.

When the build cannot be determined — the platform is not `Win32NT`, or the
reported build is not a positive number — the resolver selects the
unconditional last variant, the lower payload. That is the documented behaviour
rather than an arbitrary default: it is the only payload whose every key is
honoured on every supported build, so a key is never deployed to a host that
was not shown to honour it. `setup.ps1` reports the build it resolved against,
or `undetermined`, in its summary whenever a conditional payload is selected.

The desired-state hash covers **every** declared variant of a selected managed
file, not the variant this host resolved. Hashing only the resolved one would
make the hash depend on host state, so two hosts of different build classes
would disagree about the same desired state and a host that crossed the bound
would report drift it could not clear.

This is a `SchemaVersion` bump, 2 to 3, and `ProjectVersion` moves 0.3.0 to
0.4.0 the way the schema 1 to 2 bump moved 0.2.0 to 0.3.0. **No `state.json`
schema changes.** State schema 2 records the applied feature set, project
version, and desired-state hash, none of which describe managed-file sources,
so an existing schema 1 or schema 2 state stays readable and keeps its recorded
selection. What an applied host does see is a changed desired-state hash and a
higher project version, both of which are true — the payload it deployed is no
longer the payload this repository declares for it — so the next `-Check`
reports `desired state changed` and the next Apply redeploys the file its build
actually honours.

A host that later **crosses the bound** — Windows Update carrying it from 22000
to 22621 — is a different case and is deliberately left where every other
content change already sits. Nothing the Apply trigger reads has changed: the
hash covers both variants by design, and the project version and feature set are
untouched, so `$shouldApply` stays false and the host keeps the payload it has.
`-Check` does report it, as `wslConfig settings` drift with exit status 2, and
`bootstrap.ps1 -Force` is what redeploys the payload the new build honours.
Making drift itself trigger an Apply would change the exit contract, which is
#54's to decide, not this record's.

This mechanism is deliberately not the one #37 uses for Appx detection, and the
two must not be merged. Whether the `Appx` module loads is a question a probe
can ask the host directly, so a build comparison there would be a worse proxy
for an answer already available; #37's constraint "no version number appears in
the implementation" is about that capability probe. Here no probe exists:
`.wslconfig` is read by the WSL VM only after a restart this domain deliberately
does not perform, and an unhonoured key is ignored silently rather than
reported, so the build is the only thing left to ask. Two issues, two
mechanisms, one motivation.

**The runtime effect is permanently unverifiable here, not merely unverified in
this change.** `.wslconfig` takes effect only when the WSL VM starts, `AGENTS.md`
forbids `wsl --shutdown` without an explicit request, and an unhonoured key
produces no error. The only thing any check in this domain can ever assert is
the deployed file's content and its agreement with the host's build. A passing
managed-file assertion is not evidence that mirrored networking is active.

The per-distribution `/etc/wsl.conf` is a different file with a different
option set and a different owner — on this host inventory it is generated by
NixOS-WSL in the Unix-like domain — and is out of scope for this decision.

Sources for the claims above:

- Advanced settings configuration in WSL —
  https://learn.microsoft.com/en-us/windows/wsl/wsl-config
- WSL 2.0.0 release notes —
  https://github.com/microsoft/WSL/releases/tag/2.0.0
- `Environment.OSVersion` —
  https://learn.microsoft.com/en-us/dotnet/api/system.environment.osversion

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

The Windows check now carries the third state itself, and its ranking is a
decision rather than a derivation. `windows/setup.ps1` reports a detection its
host could not decide — today an Appx package whose module will not load — as
unverified instead of as absence, and `Get-WinEnvCheckStatus` is the one place
that ranks the run. The architecture settles only half the question: a failure
outranks an unverified result, and it says nothing about drift, which is
neither. The recorded answer is that drift outranks unverified.
`bootstrap.ps1 -Check` returns 2 whenever anything drifted, 69 only when the
sole open question could not be decided on that host, and 1 under
`REQUIRE_NATIVE=1`, which promotes an undecided item into the failure that
outranks both. The reason is what the command is for: it answers whether an
Apply is needed, drift is the actionable half of that answer, and a known 2
must not collapse into a 69. The cost, which the decision accepts, is that 69
is observable only on a host that has already converged — a host that has never
applied reports `state missing` drift and returns 2, naming the undecided items
in its summary but not in its status. The repository maintainer owns the
decision and it is recorded on the issue that introduced it; the evidence is
the Pester fixture over the whole ranking plus a native `-Check` on an
already-applied Windows 10 host.

One Windows 10 sub-case survives that, and it is not Appx silence read as
absence. When the module cannot answer, package detection keeps the WinGet
registration as its answer, so a package WinGet's configured source does not
report is still recorded missing — the same claim a `WinGet`-detected package
already makes, drawn from a route that did answer. A Store-installed Windows
Terminal reaches it. Apply then attempts an install, and
`Install-WinEnvPackage` accepts WinGet's documented "no applicable update"
status as success so a run is not aborted mid-deployment over a package that is
present; post-apply validation still asks the same undecidable question and
refuses to record state. Deciding that item needs detection independent of the
registration query, which belongs with the general unverified state rather than
with the Appx route.

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

## Desired-state hygiene had no enforcement owner

`AGENTS.md` has asked since the three-domain split that secrets, undeclared
usernames, absolute home paths, and snapshots of runtime state stay out of
every domain's committed desired state. Only the first quarter of that sentence
was enforced. `gitleaks` covers secrets from the pre-commit hook and the CI
secret job; one Pester assertion covered a single literal user path inside one
directory of the Windows payloads. Nothing looked at the rest, and the
2026-08-29 audit found the gap had already been used: two absolute home paths
sat in `docs/troubleshooting.md` for the document's whole history. A rule with a
policy owner and no enforcement owner is exactly what the governance
decomposition says must not exist.

`tool/version-control/hygiene` is that enforcement owner now. It scans the
index along four axes — absolute home paths, undeclared user and host names,
tracked runtime state, and machine-unique identifiers — needs nothing beyond a
POSIX shell and Git, and runs unconditionally beside the secret scan instead of
through `tool/dispatch/select`, because it is repository-wide and
domain-agnostic in the same way the secret scan is. Routing it through dispatch
would also have pulled an unrelated domain's checks into a governance-only
commit. Its fixtures are folded into `tool/version-control/test` rather than
given a runner of their own, because that script is the only thing the
`repository:fixtures` unit and the CI repository job invoke, and a check whose
fixtures nothing runs is not enforced.

Axis 2 reads `modules/flake/inventory.nix` by extracting its double-quoted
literals rather than evaluating it. A structured read does work, but it needs
an impure evaluation and would make Nix a prerequisite for a governance check,
which the three-state contract would then have to report as unverified on every
host without one. Literal extraction keeps the requirement at a POSIX shell and
Git and stays correct when the inventory grows fields. It over-accepts, which
is the safe direction for an allowlist, and it fails closed when the extraction
comes back empty, so a reformat cannot retire the axis quietly.

Two gaps are current and deliberate. A bare account name in free prose has no
naming context to decide it by and is a manual invariant with named evidence
rather than a silent hole. The Windows-side assertion still matches one literal
path inside one directory; generalising it is separate work, because
classification maps the Windows tree to the Windows domain unconditionally and
the two guards are meant to stay independent — `docs/architecture.md` requires
the Windows domain to remain testable without a Unix-like host.

This implementation is superseded when the same four axes are decided from a
typed declaration rather than from text. The condition for removing it is the
one the payload declaration already sets: coverage enforced in both directions,
positive and negative fixtures for every axis, and no host prerequisite beyond
those the governance plane already has.
