# Roadmap

Lanes and order, not schedule. A lane is a host this repository configures or
means to; an order is the sequence work is taken in, and an item without a
number is a decision that must be made before the number it precedes. Each
numbered item becomes a work item under this directory when it starts; the
index is `tool/version-control/records --table work`. The repository
maintainer owns this file, and changing the order is a repository change.

## Lanes

| Lane | Host | State on 2026-09-20 |
| --- | --- | --- |
| darwin | aarch64-darwin | operational; generation 36 activated |
| utm | aarch64 NixOS guest, UTM on the Mac | declared as host `utm`, evaluated only; not installed |
| orbstack | aarch64 NixOS OrbStack machine | declared as host `orbstack`, evaluated only; not installed |
| desktop | x86_64 NixOS, physical AMD APU desktop | declared as host `desktop`, evaluated only; not installed |
| vm | x86_64 NixOS guest, VMware Workstation on a Linux and a Windows host | declared as host `vm`, evaluated only; not installed |
| wsl-standalone | x86_64 Ubuntu WSL, standalone Home Manager | operational; tagged `unixlike-v2026.08.31` |
| wsl-nixos | x86_64 NixOS-WSL | activated (generation 4); updated in place since that day |

## Order

| Order | Work | Scope |
| --- | --- | --- |
| 1 | docs layout — done 2026-09-19 | repository |
| 2 | work model — done 2026-09-19 | repository |
| 3 | NixOS-WSL updated in place — done 2026-09-19 | unixlike |
| — | release tag contract: an annotation that states each host's evidence state (before 4) — done 2026-09-19 | repository |
| 4 | typed NixOS host inventory — done 2026-09-20 | unixlike |
| — | judgement on the CI decision's `reopen-when` (before 5) — done 2026-09-20 | repository |
| 5 | headless aarch64 guest on UTM | unixlike |
| 6 | headless x86_64 guest on VMware Workstation | unixlike; a windows spec for the host install |
| 7 | aarch64 OrbStack machine | unixlike |
| 8 | shared GNOME Wayland profile and the Linux terminal layer | unixlike |
| 9 | x86_64 desktop on an AMD APU | unixlike |
| 10 | GNOME on the VM guests | unixlike |
| 11 | installation and deployment (disko, nixos-anywhere, deploy-rs) | unixlike |
| deferred | WSLg on NixOS-WSL | unixlike |

## What each order carries

Order 4, typed NixOS host inventory (from #18, re-scoped). A host declares
its system (`x86_64-linux`, `aarch64-linux`), its kind (`wsl`, `orbstack`,
`vm`, `desktop`), for `vm` its hypervisor (`vmware`, `utm`), its primary user
and its state version. Only the combinations the lanes name evaluate.
`aarch64-linux` joins the evaluated systems. The NixOS-WSL identity moves
into the inventory while Darwin and the standalone home keep theirs. The
output name and `networking.hostName` agree, and `_nixos-target` selects by
host name instead of assuming one NixOS output.

Order 5, UTM (from #22, re-scoped). Headless first; GNOME waits for order
10. It was order 6 until 2026-09-20: the two guests share nothing but the
headless layer, which whichever comes first writes and the other reuses, and
the maintainer took the UTM guest first. Its build, boot and activation
evidence comes from the Mac, because an aarch64 system is only evaluated on
the x86_64 hosts.

Order 6, VMware (from #23, re-scoped). One guest profile, headless first, on
both a Linux and a Windows host; GNOME waits for order 10. VMware Workstation
is chosen so that one guest profile serves both hosts and carries the later
GNOME stage: `vmwgfx` gives the guest 3D graphics, and on the Windows 10 host
it runs over the Windows Hypervisor Platform beside WSL2. Hyper-V remains the
lighter choice for a headless guest on a Windows-only host, but it is
Windows-only, has no 3D guest graphics, and its enhanced session is xrdp;
QEMU/KVM is the more native choice on a NixOS host. The decision record
lands with order 6.

Order 7, OrbStack. A host kind of its own, like WSL in having no boot loader
and a host that injects its integration, so it reuses the flake-only rebuild
that order 3 settles.

Orders 8 to 11 carry #19 and #42 (8), #20 (9), and #24 and #25 (11). The
deferred item carries #21.

## Constraints recorded with the order

- aarch64 builds never use qemu binfmt on a WSL distribution: binfmt_misc is
  shared by every distribution. They run natively in the UTM guest or on a
  remote builder.
