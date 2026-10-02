# Install a headless aarch64 NixOS guest on UTM

kind: spec
date: 2026-09-20
scope: unixlike
status: approved
review-by: 2026-11-15
issue: #301

Agreed with the maintainer in the session of 2026-09-20. Lane `utm` of
`docs/work/roadmap.md`, the guest the maintainer took before the VMware one;
it carries issue 22 as the roadmap re-scoped it. The spec was written on the
x86_64 WSL host, which can only evaluate an aarch64 system; the
implementation and every lane past evaluation belong to a session on the Mac.

## Problem

1. **The `utm` host is a placeholder.** The typed inventory declares it and
   `modules/host/placeholder.nix` gives it a boot loader, two labelled file
   systems and the QEMU guest agent. It creates no account, runs no service
   and has no home, so nothing could log into it, and it has been evaluated
   and nothing else.
2. **No NixOS class describes a machine that boots itself.** `nixos.wsl` is
   the only class with behaviour, and what it declares — the account, the
   login shell, key-only sshd — is written for a WSL distribution: a UID
   chosen for WSL's shared cgroups, a port chosen for WSL's shared network,
   an account named by `identity.wsl.user`. The VMware guest and the desktop
   will need the same three things under their own names.
3. **There is no procedure for installing a NixOS host from this flake.** The
   WSL one is imported from an archive; a guest with a disk is installed.

## Decisions

### A `nixos.headless` class, written once for every host that boots itself

What a headless NixOS machine needs to be reachable and rebuildable, read
from what `modules.nixos.shared` tells the host about itself and naming no
host:

- the account `host.user`: a normal user in `wheel`, zsh as its login shell
  the way `modules/shell/wsl.nix` selects it, created without a password —
  the installing step sets one — and `sudo` asks for it;
- sshd on port 22, key-only, no root login, keys host-owned in
  `~/.ssh/authorized_keys` and never in tracked state, as
  `modules/sshd.nix` has it for WSL;
- a firewall that admits that port and nothing else.

The WSL class keeps its own account and sshd fragments: their UID and port
are WSL facts. The class reaches `utm` now; the order that installs the
VMware guest and the desktop composes it for them, and until then their
placeholders are unchanged.

Rejected: generalising `nixos.wsl`'s fragments by parameter, because the
values that differ are the point of those fragments and the WSL toplevel
must not move; writing the account and sshd inside `nixos.utm`, because the
next guest would copy them.

### `nixos.utm` replaces the placeholder

A file of its own under `modules/host/`, holding what is true of a UTM guest
of the QEMU `virt` machine and of no particular disk: systemd-boot on EFI,
the root and boot file systems by label (`nixos`, `boot`), the virtio kernel
modules the initrd needs to find them, the QEMU guest agent, and a serial
console so that the guest is reachable before the network is. The module
list is a fact about the hypervisor's machine type, which is a kind; nothing
detected on a machine — a UUID, a MAC address, a generated
`hardware-configuration.nix` — is stored. Networking is DHCP on UTM's shared
network. The `utm` entry leaves `modules/host/placeholder.nix`, which keeps
`vmware`, `orbstack` and `desktop`.

### The home is `home.shared`

The guest's home is the shared class alone, composed into the system as on
NixOS-WSL, so a dotfile change is a system switch. No graphical class
reaches it (`INV unixlike/desktop-not-wsl` states the rule for WSL; the same
holds here until the roadmap's GNOME order), and the coding agents stay on
NixOS-WSL. Whether the Darwin-side terminal definitions a composed home
renders in apply is the implementing session's to check against
`docs/policy/decisions/unixlike/composed-homes-render-in-declared-terminals.md`.

### The inventory entry is confirmed at installation

`identity.nixosHosts.utm` keeps its name. Its `user` and its `stateVersion`
were provisional; the installing session confirms or corrects both before
anything is activated, and the state version is the release of the
installation medium's NixOS, not of the pinned nixpkgs if the two differ.

### Installed by hand from the minimal ISO, rebuilt in place

Partitioning and deployment tooling are the roadmap's last order, so this
guest is installed by hand: boot the aarch64 minimal ISO in UTM, create a GPT
disk with an EFI system partition labelled `boot` and an ext4 root labelled
`nixos`, mount them, and run `nixos-install --flake` against this flake's
`utm` output from a clone. After the first boot the guest is updated from a
clone inside it with the recipes that already act on the output named after
the running host (`just nixos-test`, `just nixos-switch`,
`just nixos-rollback`). The procedure is written into `CONTRIBUTING.md`
beside the NixOS-WSL one.

Rejected: building the closure on the Mac through a Linux builder and
copying it in, because it needs a Darwin configuration change and an
activation before the guest exists; an image built elsewhere, because no
x86_64 host here may emulate aarch64.

### Evidence comes from two places

Evaluation is available on every host and in the merge gate. Build, native
runtime and activation are available only inside the guest, and are reported
as unavailable anywhere else, never inferred from evaluation. The CI
decision's reopen condition concerns an x86_64 guest and is not touched by
this work.

## Increments

1. This spec and its report.
2. `nixos.headless` and `nixos.utm`, the composition row, the inventory
   entry, fixtures — the toplevel derivations of `nixos`, the standalone home
   and the Darwin system unchanged.
3. A `repository` increment: the installation and update procedure in
   `CONTRIBUTING.md`.
4. The installation, on the Mac: the maintainer installs the guest, and the
   session there records build, native runtime and activation evidence, then
   the decision record if the installation settled anything a reviewer will
   ask about, `docs/status/unixlike.md`, and the end of the report with the
   roadmap row (`repository`).

Amended 2026-09-20: the increments are regrouped at the evidence lanes and no criterion changes. Increment 2 is the evaluation lane: it verifies AC1 to AC4 and carries their report rows and the status sentence with them. Increment 3 is unchanged and verifies AC5. Increment 4 is the guest's lanes: it verifies AC6 to AC9, records AC10 for the pull requests before it, and ends the report; the roadmap row follows that end in `repository`.

Amended 2026-09-20 (2): the guest was adopted, not installed from the minimal ISO, and no criterion changes. The maintainer had already installed NixOS 25.11 in UTM with the graphical installer before the session on the Mac: an unlabelled EFI system partition on `/boot`, an ext4 root labelled `root`, a swap partition, the host name `nixos` and an installer account. Reinstalling would have proved nothing the criteria ask for, so the two file systems are relabelled `boot` and `nixos` in place, the first switch to this flake's `utm` output is made by naming the output, because the host-bound recipes refuse while the host still answers to `nixos`, and the installer's channel and `/etc/nixos` are removed afterwards. The inventory entry keeps `shk` as the account and takes `25.11` as the state version, the installed release. The swap partition is left unused: nothing the flake declares names it. The maintainer means this guest to become a graphical machine; that stays with the roadmap's GNOME orders, and this spec ends headless as written.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | `nixosConfigurations.utm` evaluates with the `nixos.headless` and `nixos.utm` classes and the `home.shared` home; `modules/host/placeholder.nix` no longer defines `utm`; the toplevel derivations of `nixosConfigurations.nixos`, the standalone home and the Darwin system are unchanged. | evaluation |
| AC2 | On `utm`: the account named by the entry exists, is a normal user in `wheel` with zsh as its shell and no password in tracked state; sshd is enabled on port 22 with password and root login off and no authorized key in tracked state; the firewall is on and opens only that port; channels are off. Fixtures prove each, and that a class change which opens another port or enables password login is refused. | evaluation |
| AC3 | No graphical program reaches the `utm` home, and no feature file names the host. | evaluation |
| AC4 | No machine-unique identifier and no generated hardware configuration is tracked for the guest; the hygiene scan passes. | evaluation |
| AC5 | `CONTRIBUTING.md` states the installation from the minimal ISO and the in-place update, with what is the maintainer's to run. | review |
| AC6 | The `utm` toplevel builds inside the guest. | build |
| AC7 | Inside the installed guest: the host answers to `utm`; `just nixos-generations` lists its generations; the account logs in over ssh with a key and is refused with a password; `sudo` asks for the password; `nix` runs flakes and no channel exists. | native runtime |
| AC8 | `just nixos-test` then `just nixos-switch` from a clone inside the guest activate a generation built from this flake, and `just nixos-rollback` returns to the one before. | activation |
| AC9 | The inventory entry's `user` and `stateVersion` are the installed guest's, and `docs/status/unixlike.md` states the host as installed with the evidence of each lane named separately. | review |
| AC10 | `Required checks` passes on the head of every pull request of this work before it merges. | evaluation |
