# Observe whether a Windows host can run the VMware guest

kind: spec
date: 2026-09-20
scope: windows
status: approved
review-by: 2026-11-15

Agreed with the maintainer in the session of 2026-09-20. The Windows half of
the VMware order of `docs/work/roadmap.md`: the guest itself is a Unix-like
spec, and nothing here reads or depends on it.

## Problem

1. **The guest needs a hypervisor the Windows domain does not know about.**
   The roadmap's x86_64 NixOS guest runs on VMware Workstation, on this
   Windows host beside WSL 2. The domain declares packages, files, a font and
   terminal delegations; it has no way to say that a host is, or is not,
   ready to run a virtual machine.
2. **The domain's only installation route cannot install it.** A package is
   installed through WinGet. Observed on 2026-09-20 from the maintainer's
   Windows 10 host (build 19044), with WinGet unable to refresh its source and
   answering from the index it held: a search of the `winget` source for the
   publisher's identifiers lists no VMware Workstation package. The
   installer is downloaded from the vendor's portal under an account.
3. **Coexistence with WSL 2 rests on Windows optional features.** VMware
   Workstation runs beside WSL 2 only through the Windows hypervisor
   interface, which the `HypervisorPlatform` and `VirtualMachinePlatform`
   optional features provide. The same observation found both enabled on
   that host, read through CIM from a shell that was elevated; whether an
   unelevated shell can read them is not yet observed. The domain has no
   model of an optional feature, and enabling one needs an administrator and
   a restart.

## Decisions

### The maintainer installs; the domain observes

Installing VMware Workstation and enabling a Windows optional feature are the
maintainer's manual steps, written as a procedure. The domain declares an
optional feature of its own, `vmware`, that owns no package and no file. For
a host that selects it, the read-only check reports whether the host is ready
to run the guest, and Apply installs nothing, enables nothing and changes no
registry value for it.

Rejected: Apply installing from an installer path the maintainer supplies
and enabling the optional features, because it puts elevation, a restart and
a licence acceptance inside Apply and needs a local-installer model the
domain has no other use for; documentation alone, because then nothing says
whether the host can run the guest.

### Readiness is a set of preconditions with two new types

A feature's `Preconditions` already carry a typed probe and a message, and
already answer in three states. Two types join `Appx`:

- `OptionalFeature`, naming a Windows optional feature that must be enabled.
  `vmware` names `HypervisorPlatform` and `VirtualMachinePlatform`.
- `InstalledProgram`, naming a program by the registry key its installer
  writes and the value that carries its version. `vmware` names VMware
  Workstation's.

Each probe is read-only and answers present, absent, or undecidable on this
host — a query that needs elevation the shell does not have, or a provider
that will not load, is undecidable and never absent. An absent precondition
is reported with the manual step that satisfies it and ranks as drift in the
check's status, as an item an Apply cannot settle; an undecidable one ranks
as unverified, as every other undecidable item does
(`INV windows/check-exit-contract`). An unknown type is still refused at
load.

The exact registry key, the value names and whether the optional-feature
query answers without elevation are facts of the host, and the implementation
takes them from an observation on the maintainer's host after the manual
installation, not from memory: the key is recorded in the report with the
build it was read on before it is written into the manifest.

Rejected: a `Packages` entry with `Detection: Command`, because VMware puts no
command on `PATH` and a package is something Apply installs; a new top-level
manifest section for host capabilities, because one feature does not justify
a schema version.

### No minimum version is declared yet

The check reports the installed version it read and compares it with
nothing. A minimum is declared when a guest feature is found to need one, in
the change that finds it.

### The Windows 10 support boundary is named

The observation is evidence for the build it ran on. `docs/status/windows.md`
gains the two optional features and the installed program as items of the
support boundary table, each in its boundary state
(`INV windows/support-boundary-named`).

## Increments

1. This spec and its report.
2. The two precondition types, the `vmware` feature, Pester cases in both
   directions, and the status text — none of which needs VMware installed.
3. A `repository` increment: the manual procedure in `CONTRIBUTING.md` —
   where the installer comes from, the optional features, the restart, and
   what the check then reports.
4. After the maintainer installs VMware Workstation: the registry facts read
   on the host and written into the manifest, the native check observed with
   `vmware` selected, and the end of the report.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The manifest declares a feature `vmware` that owns no package, file, font or delegation and carries `OptionalFeature` and `InstalledProgram` preconditions; a precondition of an unknown type, or one missing a field its type requires, is refused at load; every existing feature validates unchanged. | evaluation, native runtime |
| AC2 | Each new probe answers present, absent and undecidable, proved by Pester with injected queries in all three directions, and an undecidable answer is never reported as absent. | native runtime |
| AC3 | With `vmware` selected, the read-only check reports each absent precondition with its manual step and returns the drift status, reports an undecidable one as unverified under the existing status contract, and returns 0 for those items when all are present; with `vmware` not selected it reports them as not selected. | native runtime |
| AC4 | Apply with `vmware` selected installs nothing, enables no optional feature and writes no registry value for it; a Pester case proves no installing or enabling command is reached. | native runtime |
| AC5 | The Windows checks and suite still read only the Windows tree, and the desired-state hash changes only by the manifest's new content. | evaluation, native runtime |
| AC6 | `CONTRIBUTING.md` states the manual installation and what the check reports before and after it. | review |
| AC7 | On the maintainer's host, named by its Windows build, after the manual installation: `windows/win-env.ps1 check` with `vmware` selected reports the optional features and the program as present with the version it read, and the registry facts in the manifest are the ones recorded from that host. | native runtime |
| AC8 | `docs/status/windows.md` states the feature, the two precondition types and the support boundary items in their boundary state. | review |
| AC9 | `Required checks` passes on the head of every pull request of this work before it merges. | native runtime |
