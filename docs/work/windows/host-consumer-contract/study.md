# Windows host-input and capture investigation
kind: study
date: 2026-09-27
scope: windows
status: open

The initial section records read-only source observations from the 2026-09-26/27 planning session at
provider e11bd1368d2f5138ad0f9b7017040b2b76e055e6; not native Windows evidence.

`windows/desired/manifest.json` declares seven features: core, font, zellij,
terminal, wezterm, powertoys and wsl. Core is required; terminal requires font
and zellij, wezterm requires font. The manifest is more current than the
status prose that omits terminal's font dependency.

`windows/src/WinEnv.psm1` Get-WinEnvHostPath obtains USERPROFILE, LOCALAPPDATA,
APPDATA and the current account. Resolve-WinEnvPath expands target tokens;
Expand-WinEnvTemplate handles the NewPlus LOCALAPPDATA JSON placeholder.
Windows build selects the WSL payload variant; WSL/application versions are
observed for support checks. No computer name or fixed account needs to be
introduced as mandatory host input.

Current Get-WinEnvRequestedFeature selects all on first use and thereafter
retains recorded selection. It supports Feature/Add/Minimal/All rather than
the proposed host-owned declarative opt-in contract. A new optional feature
must remain unselected under the agreed new model. Runtime selection evidence
lives under LOCALAPPDATA/win-env/state.json, as setup.ps1 shows; the status
document's windows/state.json wording is not the current runtime path.

Keyboard mappings, fonts, colours, window behavior and generic FancyZones
layouts are presently provider preferences, not machine identity. WezTerm
loads optional local.lua but no host-generation contract currently supplies
it. Current WSL payloads declare networking and memory-reclaim policy, not
host RAM/CPU allocation. Additional host fields were explicitly deferred.

Current capture writes windows/desired source and has provider publication
behavior. The planned host model must replace that destination/ownership,
not merely copy files before invoking the unchanged capture command. Existing
compare modes/projection are useful input to the design, but do not prove a
future layered merge. workspaces.json and applied-layouts.json are excluded
runtime state. Preserve that boundary and externally managed profile blocks.

Current source has no independent local deployment-generation verb. Its public
entry and existing native apply/check engine should be reused. Do not describe
the proposed generation or host-capture pipeline as already available.

## Read-only native inventory, 2026-09-27

The maintainer authorized SSH inventory of the available Windows client.
Version, OS, Appx and existing state observations returned:

| Item | Observed value |
| --- | --- |
| OS | Windows 10 IoT Enterprise LTSC, IoTEnterpriseS, 21H2 |
| Build and architecture | 19044.7725, AMD64/x64 |
| Windows PowerShell | 5.1.19041.7725 |
| PowerShell | 7.6.6 |
| WinGet / Desktop App Installer | 1.29.380 / 1.29.380.0 |
| Windows Terminal | 1.24.11911.0 |
| Command Palette | 0.12.12365.0 |
| WSL / kernel | 2.7.13.0 / 6.18.33.2-2 |

Appx presence/version queries used Windows PowerShell 5.1; they do not prove
the provider's PowerShell 7 detection or fallback path. Existing
LOCALAPPDATA/win-env/state.json reports schema 2 and the recorded selection
core,font,zellij,terminal,wezterm,powertoys,wsl. This historical selection
does not prove current desired-state convergence.

WinGet list/install help exited 0 and advertised --id, --exact, --source,
--accept-source-agreements and --disable-interactivity; install help also
advertised --version and --accept-package-agreements. Help and version probes
do not exercise package registration detection or installation. WinGet
1.29.380 is an observed candidate verification pin, not an accepted minimum
consumer version or completed compatibility test.

No provider source was executed on this host: no generation, native suite,
Check, capture or Apply. No installation or host setting was changed. These
observations are planning inputs, not candidate-SHA release evidence.

## Accepted LTSC capability boundary, 2026-09-27

The maintainer accepted this LTSC edition/build family as the initial client
baseline and excluded default terminal delegation from its guarantee while
retaining Windows Terminal settings, fonts and profiles; see the dated AC5
amendment in spec.md.

At the inspected provider SHA, Get-WinEnvTerminalDelegationSupport uses the
documented Windows 10 threshold 19045.3031 and Terminal 1.17. The installed
Terminal meets the application threshold, but OS build 19044 does not meet
the OS threshold. This is a known support boundary, not a newly observed
console handoff failure. The official source is
[Microsoft's default terminal application policy](https://learn.microsoft.com/en-us/windows/terminal/group-policy#default-terminal-application).

The current accepted decision remains
docs/policy/decisions/windows/terminal-delegation-unverified-below-boundary.md:
below-boundary read-back does not certify behavior, and REQUIRE_NATIVE rejects
unverified evidence. Implementing the new capability contract must reconcile
the declared exclusion with check/gate selection through the Windows lane and
its repository dependency. It cannot silently convert current unverified
results to success, discard unrelated failures, or remove the whole terminal
feature. This planning amendment does not change that policy or runtime code.
