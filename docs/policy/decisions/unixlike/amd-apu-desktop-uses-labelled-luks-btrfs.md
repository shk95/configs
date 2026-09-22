# The AMD APU desktop uses labelled LUKS and Btrfs

date: 2026-09-23
scope: unixlike
status: accepted
issue: #335
reopen-when: The physical host cannot boot or recover reliably from the labelled layout, or its reviewed hardware facts require a different storage or graphics contract.
source: docs/work/unixlike/amd-apu-desktop/spec.md § Decisions

The first physical NixOS host is an x86_64 desktop with an AMD APU. Its
predecessor in the inventory was an ext4 evaluation placeholder with no
account or home; it was not an installable description of the selected Niri
and Noctalia desktop.

## The portable base names created values, not observed hardware

The EFI system partition is labelled `boot`. A partition labelled `cryptroot`
holds one LUKS2 container and is unlocked with a passphrase in the initrd. The
mapped device contains Btrfs subvolumes `@`, `@home` and `@nix`, mounted at
`/`, `/home` and `/nix` with zstd compression and `noatime`. Zram supplies the
only declared swap.

These labels and subvolume names are values the installation procedure
creates. They make the source independent of a disk path while keeping the
layout reviewable before a destructive command. A disk UUID, controller module
or generated hardware file is an observation and enters only after the
physical installer has produced it and the maintainer has reviewed it.

Systemd-boot owns the UEFI boot path. Secure Boot, TPM unlock and unattended
unlock are outside this order. The passphrase is host state and never enters
the repository.

## AMDGPU and Mesa stay on the distribution path

The desktop class loads AMDGPU in the initrd, enables redistributable firmware
and AMD microcode, and enables the 32-bit graphics path. The shared graphical
class enables graphics; nixpkgs' default Mesa package provides OpenGL, Vulkan
and VA-API for the APU. No vendor override, OpenCL runtime, overclocking option
or hardware-specific kernel parameter is declared without an observed need.

NetworkManager owns desktop networking. Monitor layout remains runtime state
until the installed Niri session provides an observed output identity worth
declaring.

## The desktop keeps the recovery base

The composition table gives the physical host `nixos.desktop`,
`nixos.installLuksBtrfs`, `nixos.headless` and `nixos.graphical`, and gives its
home the shared, desktop and Linux graphical classes. The installation class
now owns the storage shape described above; the machine class owns zram,
networking and the assertion over the combined shape. The headless layer
retains the password-backed sudo account, key-only SSH and one-port firewall
as a recovery route; the graphical layers add Niri and Noctalia without
weakening it. Roadmap order 10 also composed those graphical classes into the
two VM guests.

The inventory's account and state version remain provisional. Evaluation and
build use them, but the installing step confirms or corrects them from the
chosen installation medium before any activation. Physical rendering, video,
display, input, audio, reboot and rollback remain evidence the repository
cannot manufacture.
