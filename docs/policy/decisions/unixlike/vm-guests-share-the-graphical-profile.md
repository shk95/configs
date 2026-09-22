# The VM guests share the Niri and Noctalia profile

date: 2026-09-23
scope: unixlike
status: accepted
issue: #339
reopen-when: A guest cannot provide a usable Niri session with its hypervisor graphics, or a guest needs a materially different graphical environment rather than a machine-specific integration layer.
source: docs/work/unixlike/graphical-vm-guests/spec.md § Decisions

The installed UTM and VMware guests were deliberately adopted headless before
the shared graphical profile existed. They now receive the same
`nixos.graphical`, `homeManager.desktop` and
`homeManager.linuxGraphical` classes as the physical desktop while retaining
the headless account, key-only SSH and firewall recovery layer.

## Composition owns the shared environment

Only `unixlike/modules/flake/configurations.nix` selects the graphical
classes for the two guest rows. Niri, Noctalia, greetd, portals, audio, input
and graphical applications stay in their concern modules. The hypervisor
modules continue to describe only the virtual machine they run under, so UTM
keeps the QEMU guest devices and serial console and VMware keeps open-vm-tools.

The VMware row uses the full open-vm-tools package rather than its headless
variant. That is the distribution module's route to its graphical vmblock
mount and user wrapper; it does not make the VMware module a second owner of
the Wayland session. No monitor, resolution, virtual GPU parameter or host
network value is declared without runtime evidence.

## Adoption stops before activation

The x86_64 VMware toplevel is built on a matching host, both guest outputs are
evaluated, and the existing booted tests continue to prove the shared
graphical and recovery classes. The aarch64 build belongs to the UTM guest.
Each installed guest must still prove free capacity, login, rendering, Korean
input, audio, networking, reboot and rollback, with VMware first. The desired
state and its automatic evidence do not authorize either activation.
