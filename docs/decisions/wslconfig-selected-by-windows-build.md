# `.wslconfig` content is selected by the host's Windows build

date: 2026-08-30
scope: windows
status: accepted
source: 9f1e8ce:docs/status.md § `.wslconfig` content is selected by the host's Windows build

`.wslconfig` is host-global: one file per machine, read by the WSL VM for every
distribution on it, so a wrong value is not scoped to one distro. The option set
it may carry is not the same on every Windows build, and the boundary is not
where "Windows 10 versus Windows 11" puts it. Microsoft's `.wslconfig` reference
footnotes each key — footnote 1 means "only available on Windows 11", footnote 2
means "require Windows 11 version 22H2 or higher". Against the four keys this
repository sets:

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

Because three of the four keys share one bound, the payloads are named after the
capability they assume rather than after a Windows release. A Windows 11 21H2
host — build 22000, unmistakably Windows 11 — honours none of the three 22H2
keys and belongs on the same side as Windows 10, so a release name would encode
a boundary the option set does not have. The two payloads are
`files/wsl/mirrored-networking.wslconfig`, which is the previously deployed
content unchanged, and `files/wsl/nat-networking.wslconfig`, which carries only
`autoMemoryReclaim` and leaves the host on WSL's default NAT networking.

The manifest expresses this with **one entry and alternative sources**, not two
entries with mutually exclusive conditions. A single `ManagedFiles` entry keeps
one `Id`, one `Target`, one `Compare` mode and one owning feature, so drift,
backup, and deselection continue to reason about one logical file; the cost is
that `Source` stops being a scalar and every consumer must go through the
resolver. Two entries would have kept a scalar `Source` everywhere, at the price
of two `Id`s competing for one `Target` and a new invariant nothing enforces
today: exactly one entry must select on any host. A manifest whose conditions
overlapped would deploy twice, and one whose conditions all failed would deploy
nothing, and neither failure is visible in the file the manifest declares. The
chosen shape makes that invariant structural instead: a conditional entry
declares `Sources` as an ordered list whose bounds descend strictly and whose
**last variant carries no condition**, so resolution is a total function and
"exactly one variant applies" cannot be violated by editing the manifest.
`Get-WinEnvManifest` rejects a `Sources` list that breaks either rule, so the
invariant fails at load rather than at deployment.

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
Microsoft's footnote links the 22621.2359 release announcement, but the revision
is a servicing level rather than an OS version: pinning it would classify a
22621 host that is merely behind on cumulative updates as below the bound, and
this source carries no UBR, so a revision comparison would need a second and
more failure-prone source to decide a boundary the documentation states in
builds.

When the build cannot be determined — the platform is not `Win32NT`, or the
reported build is not a positive number — the resolver selects the unconditional
last variant, the lower payload. That is the documented behaviour rather than an
arbitrary default: it is the only payload whose every key is honoured on every
supported build, so a key is never deployed to a host that was not shown to
honour it. `setup.ps1` reports the build it resolved against, or `undetermined`,
in its summary whenever a conditional payload is selected.

The desired-state hash covers **every** declared variant of a selected managed
file, not the variant this host resolved. Hashing only the resolved one would
make the hash depend on host state, so two hosts of different build classes
would disagree about the same desired state and a host that crossed the bound
would report drift it could not clear.

This is a `SchemaVersion` bump, 2 to 3, and `ProjectVersion` moves 0.3.0 to
0.4.0 the way the schema 1 to 2 bump moved 0.2.0 to 0.3.0. **No `state.json`
schema changes.** State schema 2 records the applied feature set, project
version, and desired-state hash, none of which describe managed-file sources, so
an existing schema 1 or schema 2 state stays readable and keeps its recorded
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
this change.** `.wslconfig` takes effect only when the WSL VM starts,
`AGENTS.md` forbids `wsl --shutdown` without an explicit request, and an
unhonoured key produces no error. The only thing any check in this domain can
ever assert is the deployed file's content and its agreement with the host's
build. A passing managed-file assertion is not evidence that mirrored networking
is active.

The per-distribution `/etc/wsl.conf` is a different file with a different option
set and a different owner — on this host inventory it is generated by NixOS-WSL
in the Unix-like domain — and is out of scope for this decision.

Sources for the claims above:

- Advanced settings configuration in WSL —
  https://learn.microsoft.com/en-us/windows/wsl/wsl-config
- WSL 2.0.0 release notes —
  https://github.com/microsoft/WSL/releases/tag/2.0.0
- `Environment.OSVersion` —
  https://learn.microsoft.com/en-us/dotnet/api/system.environment.osversion
