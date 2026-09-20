# Install a headless x86_64 NixOS guest on VMware Workstation

kind: spec
date: 2026-09-20
scope: unixlike
status: approved
review-by: 2026-11-15

Agreed with the maintainer in the session of 2026-09-20. Lane `vm` of
`docs/work/roadmap.md`, its order 6; it carries issue 23 as the roadmap
re-scoped it. The spec was written on the x86_64 WSL host, which evaluates
and builds an x86_64 system and can neither boot nor activate one; the
installation and every lane past build are the maintainer's, in VMware
Workstation.

## Problem

1. **The `vm` host is a placeholder.** The typed inventory declares it and
   `modules/host/placeholder.nix` gives it a boot loader, two labelled file
   systems and the VMware guest tools. It creates no account, runs no
   service and has no home, so nothing could log into it, and it has been
   evaluated and nothing else.
2. **The choice of hypervisor is recorded nowhere that carries authority.**
   The roadmap argues VMware Workstation over Hyper-V and QEMU/KVM, and a
   roadmap states order, not decisions. The inventory's `vmware` value rests
   on that paragraph.
3. **There is no procedure for installing this guest.** The UTM one names an
   aarch64 ISO, a VirtIO disk and a serial console, none of which is true of
   a VMware machine.

## Decisions

### `nixos.vmware` leaves the placeholder for a file of its own

`modules/host/vmware.nix` holds what is true of a NixOS guest under VMware
Workstation and of no particular disk: systemd-boot on EFI, the root and
boot file systems by label (`nixos`, `boot`), the VMware guest tools in
their headless form, and DHCP on the hypervisor's network. The tools module
of the pinned nixpkgs already puts the LSI Logic and paravirtual SCSI
drivers in the initrd, and the NVMe and SATA drivers are in every NixOS
initrd, so whichever disk controller the machine is created with is found
and no module list is written here. Nothing detected on a machine — a UUID,
a MAC address, a generated `hardware-configuration.nix` — is stored. The
`vmware` entry leaves `modules/host/placeholder.nix`, which keeps `orbstack`
and `desktop`.

The console is the machine's own screen in VMware. No serial console is
declared: a VMware machine has no serial port unless one is added by hand,
and the screen is there on both hosts.

Nothing in the class depends on the host's operating system. The guest is
one profile on the Linux and the Windows host, which is what the hypervisor
was chosen for.

Rejected: sharing the boot loader and file system lines with `nixos.utm`
through a common fragment, because two hosts that agree today are not a
contract and the desktop will differ; a BIOS boot with GRUB, because the
UTM guest and the desktop are EFI and one procedure for the disk serves all
three.

### `nixos.headless` is reused as it is

The class written for the UTM guest reaches `vm` unchanged: the entry's
account without a tracked password, key-only sshd on 22, the firewall that
opens that port alone (`INV unixlike/headless-key-only`). If the guest needs
something the class does not give, the class is changed for every host of it
or the need is a fact about VMware and belongs in `nixos.vmware`; the class
gains no parameter for one host.

### The home is `home.shared`

As on the UTM guest: the shared class alone, composed into the system, so a
dotfile change is a system switch. No graphical class reaches it until the
roadmap's GNOME order, and the coding agents stay on NixOS-WSL.

### The hypervisor is a decision record

`docs/policy/decisions/unixlike/` gains a record of the choice the roadmap's
order 6 paragraph argues: VMware Workstation, so that one guest profile
serves a Linux and a Windows host and carries the later GNOME stage;
Hyper-V and QEMU/KVM rejected with their reasons; VMware Workstation itself
installed by the maintainer by hand and managed by neither domain. The
record names this spec as its source and lands with the class, because the
class is what rests on it. The roadmap paragraph then shrinks to the order
and a pointer, in the `repository` increment.

### The inventory entry is confirmed at installation

`identity.nixosHosts.vm` keeps its name. Its `user` and its `stateVersion`
are provisional; the maintainer confirms or corrects both before anything
is installed, and the state version is the release of the installation
medium's NixOS, not of the pinned nixpkgs if the two differ.

### Installed by hand from the minimal ISO, rebuilt in place

Partitioning and deployment tooling are the roadmap's last order, so the
guest is installed by hand, as the UTM procedure has it: install VMware
Workstation, create a machine with UEFI firmware that boots the x86_64
minimal ISO, create the two labelled file systems, and run
`nixos-install --flake` against this flake's `vm` output from a clone.
Installing VMware Workstation is one line of that procedure and nothing in
the repository checks or manages it. After the first boot the guest is updated from a
clone inside it with the recipes that act on the output named after the
running host. The procedure is written into `CONTRIBUTING.md` beside the
UTM one and says only what differs from it. A guest that already runs
NixOS is adopted in place by the steps that procedure already states, with
`vm` for the output.

Rejected: building the system here and importing a disk image, because an
image format and its builder are a dependency the last order will choose
once for every host.

### Evidence comes from two places

Evaluation and build are available on this host and in the merge gate's
evaluation. Native runtime and activation are available only inside the
installed guest and are reported as unavailable anywhere else. A build here
proves the closure realises, not that it boots.

The installed guest is an x86_64 NixOS guest that declares an account, a
service and a port, which is the letter of the second `reopen-when`
condition of
`docs/policy/decisions/repository/ci-evidence-without-hosted-runners.md`.
This work does not make that judgement. The `repository` increment that
records the end puts the judgement on the roadmap, before the next order.

## Increments

1. This spec and its report.
2. The evaluation and build lanes, on this host: `nixos.vmware` in a file of
   its own, the composition row, the decision record, the fixtures, the
   status sentence — the toplevel derivations of every other configuration
   unchanged. It verifies AC1 to AC5 and carries their report rows.
3. A `repository` increment: the installation procedure in
   `CONTRIBUTING.md`. It verifies AC6.
4. The guest's lanes: the maintainer installs the guest on one host and
   returns the evidence, and the session records native runtime and
   activation, the confirmed inventory entry, `docs/status/unixlike.md`,
   AC10 for the pull requests before it, and the end of the report. Its body
   names the host the evidence was produced on. The roadmap row, the
   shortened order 6 paragraph and the CI judgement item follow that end in
   `repository`.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | `nixosConfigurations.vm` evaluates with the `nixos.vmware` and `nixos.headless` classes and the `home.shared` home; `modules/host/placeholder.nix` no longer defines `vmware`; the toplevel derivations of every other NixOS output, the standalone home and the Darwin system are unchanged. | evaluation |
| AC2 | On `vm`, the properties of `INV unixlike/headless-key-only` hold and each violation is refused, proved by the fixture that proves them for `utm`, run over both hosts; channels are off; the VMware guest tools are enabled in their headless form. | evaluation |
| AC3 | No graphical program reaches the `vm` home, and no feature file names the host. | evaluation |
| AC4 | No machine-unique identifier and no generated hardware configuration is tracked for the guest; the hygiene scan passes. A decision record under `docs/policy/decisions/unixlike/` states the hypervisor choice and what was rejected, and the records check passes. | evaluation |
| AC5 | The `vm` toplevel builds on the x86_64 host. | build |
| AC6 | `CONTRIBUTING.md` states the installation from the minimal ISO in VMware Workstation, with UEFI firmware named as a requirement, the hand installation of VMware Workstation as a step, and what is the maintainer's to run. | review |
| AC7 | Inside the installed guest: the host answers to `vm`; `systemd-detect-virt` answers `vmware` and the guest tools service is active; `just nixos-generations` lists its generations; the account logs in over ssh with a key and is refused with a password; `sudo` asks for the password; `nix` runs flakes and no channel exists. | native runtime |
| AC8 | `just nixos-test` then `just nixos-switch` from a clone inside the guest activate a generation built from this flake, and `just nixos-rollback` returns to the one before. | activation |
| AC9 | The inventory entry's `user` and `stateVersion` are the installed guest's, and `docs/status/unixlike.md` states the host as installed, on which host operating system, with the evidence of each lane named separately. | review |
| AC10 | `Required checks` passes on the head of every pull request of this work before it merges. | evaluation |
