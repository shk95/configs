# The x86_64 guest runs on VMware Workstation

date: 2026-09-20
scope: unixlike
status: accepted
issue: #23
issue: #317
reopen-when: VMware Workstation stops running beside WSL2 on the Windows host or stops being installable on either host, or the guest needs something only a host-native hypervisor gives.
source: docs/work/unixlike/vmware-headless-guest/spec.md § Decisions

The maintainer works on a Windows host and means to work on a NixOS one, and
wants the same x86_64 NixOS guest on both: headless first, a GNOME machine
later. Each host has a hypervisor of its own, so the choice was between one
guest profile under a hypervisor both hosts can run and one profile for each
host.

## One guest profile, under VMware Workstation

The `vm` host of the inventory is a guest of VMware Workstation. Its class
(`unixlike/modules/host/vmware.nix`) names nothing about the host's
operating system, so the same output is installed on either host. Two facts
carry the choice. `vmwgfx` gives the guest 3D graphics, which the later
GNOME stage needs to render on the GPU. On the Windows host, VMware
Workstation runs over the Windows Hypervisor Platform, so it coexists with
WSL2 instead of displacing it.

## VMware Workstation is installed by hand

Neither domain installs, configures or observes VMware Workstation. It is a
program the maintainer installs, and the Windows domain reconciles only what
it deploys. The installation is a step of the guest's procedure in
`CONTRIBUTING.md`, and nothing in the repository checks it.

## What was not taken, and is not closed

Hyper-V on the Windows host is the lighter choice for a headless guest and
needs no program installed by hand. It is Windows-only, it gives the guest
no 3D graphics, so GNOME would render in software, and its enhanced session
is xrdp.

QEMU/KVM is the native choice on a NixOS host and needs no program
installed by hand either. It does not run on the Windows host beside WSL2.

Taking either for this guest would have meant a guest profile per host from
the start. Neither is rejected as a hypervisor: the maintainer takes each as
a lane of its own, after this guest, and a hypervisor becomes a value of the
inventory, with a class of its own, in the order that takes its lane
(`docs/policy/decisions/unixlike/nixos-hosts-declared-in-typed-inventory.md`).
Such a lane adds a profile beside this one and does not reopen this record.

## Cost

VMware Workstation is proprietary, outside nixpkgs' control on the Windows
host, and updated by hand on both. A change in its licensing, or in how it
shares the processor's virtualisation with WSL2, is felt by this guest and
by no check in the repository.
