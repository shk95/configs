# Roadmap

Lanes and order, not schedule. A lane is a host this repository configures or
means to; an order is the sequence work is taken in, and an item without a
number is a decision that must be made before the number it precedes. Each
numbered item becomes a work item under this directory when it starts; the
index is `tool/version-control/records --table work`. The repository
maintainer owns this file, and changing the order is a repository change.

## Lanes

| Lane | Host | State on 2026-09-23 |
| --- | --- | --- |
| darwin | aarch64-darwin | operational; generation 36 activated |
| utm | aarch64 NixOS guest, UTM on the Mac | graphical; native build, runtime, switch/reboot and rollback/restoration verified on 2026-09-23 |
| orbstack | aarch64 NixOS OrbStack machine | an isolated sandbox on the Mac, switched to the flake on 2026-09-20; disposable, recreated by its procedure |
| desktop | x86_64 NixOS, physical AMD APU desktop | declared as host `desktop`, evaluated only; not installed |
| vm | x86_64 NixOS guest, VMware Workstation on a Linux and a Windows host | graphical on Windows; native build, runtime, switch/reboot and rollback/restoration verified on 2026-09-23; Linux-host runtime unverified |
| kvm | x86_64 NixOS guest, QEMU/KVM on the NixOS desktop | not declared; order 12 declares the host |
| hyperv | x86_64 NixOS guest, Hyper-V on the Windows host | not declared; order 13 declares the host |
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
| 5 | headless aarch64 guest on UTM — done 2026-09-20 | unixlike |
| 6 | headless x86_64 guest on VMware Workstation — done 2026-09-21 | unixlike |
| 7 | aarch64 OrbStack machine — done 2026-09-20 | unixlike |
| — | judgement on the CI decision's `reopen-when`, met by the installed x86_64 guest — minimal VM check accepted on the existing required job 2026-09-21 | repository |
| 8 | shared Niri and Noctalia Wayland profile, Linux graphical home layer, and utility adoption — done 2026-09-23 | unixlike |
| 9 | x86_64 desktop on an AMD APU | unixlike |
| 10 | Niri and Noctalia on the VM guests — done 2026-09-23 | unixlike |
| 11 | installation and deployment (disko, nixos-anywhere, deploy-rs) | unixlike |
| 12 | x86_64 guest on QEMU/KVM, on the NixOS desktop | unixlike |
| 13 | x86_64 guest on Hyper-V, on the Windows host | unixlike |
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

Order 5, UTM (from #22, re-scoped). Headless first; the graphical profile
waits for order 10. It was order 6 until 2026-09-20: the two guests share
nothing but the headless layer, which whichever comes first writes and the
other reuses, and the maintainer took the UTM guest first. Its build, boot and activation
evidence comes from the Mac, because an aarch64 system is only evaluated on
the x86_64 hosts.
The guest existed before the work, installed with the graphical installer,
and was adopted in place. The maintainer means it to be a graphical machine,
which the headless spec left out on purpose: order 10 carries that, on the
account, sshd and firewall this order wrote.

Order 6, VMware (from #23, re-scoped). One guest profile for Linux and
Windows hosts, headless first; the graphical profile waits for order 10. The
choice and its costs are recorded in
`docs/policy/decisions/unixlike/x86-64-guest-runs-on-vmware-workstation.md`.
On 2026-09-21 the maintainer completed installation, native runtime and
test/switch/rollback verification on Windows; Linux-host runtime remains
unverified. The completed report is
`docs/work/unixlike/vmware-headless-guest/report.md`. VMware Workstation is
installed by hand as part of the
guest's procedure and is managed by neither configuration domain.

The installed x86_64 guest now has an account, a service and a port, meeting
the second `reopen-when` condition of
`docs/policy/decisions/repository/ci-evidence-without-hosted-runners.md`.
The maintainer accepted one minimal booted headless check in the existing
required Unix-like job on 2026-09-21. It adds no runner or workflow; account,
ssh and firewall runtime are now affected-dispatch evidence for Unix-like pull
requests.

Order 7, OrbStack. A host kind of its own, like WSL in having no boot loader
and a host that injects its integration, so it reuses the flake-only rebuild
that order 3 settles.
It was taken on 2026-09-20 beside order 6, which another session holds: the
two share no outcome — the VMware guest reuses the headless class order 5
wrote, and an OrbStack machine takes none of it, because OrbStack's agent is
the way in and sshd is off. The machine is an isolated sandbox with no
graphical use planned.

Order 8 replaces the former GNOME direction. Its reference is the coherent
Niri and Noctalia desktop in
[`ryan4yin/nix-config`](https://github.com/ryan4yin/nix-config/tree/3b13291216bbea04169360b9d8a18a210d816c04)
at commit `3b13291216bbea04169360b9d8a18a210d816c04`; the work ports behaviour
and configuration selectively instead of copying that repository's import
tree.
The existing headless class remains the account, ssh and recovery base.
System graphical services belong to a `nixos.graphical` class, existing
cross-platform graphical programs remain in `homeManager.desktop`, and
Linux-only session configuration belongs to a new
`homeManager.linuxGraphical` class. Only
`unixlike/modules/flake/configurations.nix` composes those classes into a
host. Each concern owns its module and payloads and contributes to the class;
the work adds neither a central desktop import tree nor host-specific enable
switches.

The graphical increments establish the classes, then a minimal
greetd/tuigreet and Niri session, then Noctalia with portals, keyring and
PipeWire, and finally Fcitx5 with Hangul and the selected graphical programs.
The core candidates also include Hypridle, XWayland Satellite, dconf, GTK and
XDG MIME integration, `wl-clipboard`, `wf-recorder`, `brightnessctl`,
`udiskie`, `pavucontrol`, `playerctl`, Thunar, Remmina with FreeRDP, `mpv`,
`imv` and one browser. Existing WezTerm and Ghostty supply the terminal layer.
The repository's current font configuration is unchanged. Author-specific
secrets, paths, hardware, networks and application collections from the
reference are not adopted. Age and SOPS remain a later, dedicated secrets
work item.

Order 8 also evaluates utilities in increments separate from the graphical
implementation. The first candidates are `nix-output-monitor`, `nix-index`,
`nix-tree`, `procs`, `duf`, `dust`, `tealdeer`, `zoxide`, `trash-cli`,
`hyperfine`, `jc`, `sad`, `mtr`, `gping`, `doggo`, `dnsutils`, `rsync` and
`croc`. Later candidates are `nix-melt`, `nix-init`, `iperf3`, `tcpdump`,
ImageMagick, Graphviz, FFmpeg and `qrtool`. A utility with configuration owns
its concern module; an unconfigured package may join the existing package
module. The order's work item fixes the accepted set before implementation.

Order 10 applied the shared graphical classes to the UTM and VMware guests
without removing their headless base. The original plan put VMware on the
Windows host first; the maintainer requested UTM first on 2026-09-23, and
the spec's dated AC8 amendment records that change. Both guests supplied
their own native build, graphical runtime, switch/reboot and
rollback/restoration evidence after capacity checks. VMware required 3D
acceleration and a larger disk; both guests required live-user-session
activation guards for immediate restoration from a headless generation.
The completed report is
`docs/work/unixlike/graphical-vm-guests/report.md`. Linux-hosted VMware
runtime remains unverified.

The former GNOME issues #19 and #42 are historical context, not execution
authority for orders 8 and 10. A new spec, report and execution issue are
created when order 8 starts. Order 9 carries #20, order 11 carries #24 and
#25, and the deferred item carries #21.

Orders 12 and 13, added 2026-09-20, keep the numbers before them as the
documents that cite those numbers have them. Each is a guest profile of its
own: the VMware guest stays the one profile that serves both hosts, and these
are the hypervisor each host has without a program installed by hand. Neither
is a value of the inventory's hypervisor or a placeholder until its order
starts, which is when the order declares the host, because only the
combinations a lane has declared evaluate; the inventory's decision record
is reopened by that order, not by this row. Both reuse the headless class
and, by then, the graphical classes of order 8 and the installation tooling
of order 11.

Order 12, QEMU/KVM. The host is the desktop of order 9, so it cannot come
before it. What the desktop needs to run a guest — libvirt or plain QEMU,
the bridge, the account's group — is the desktop's and is declared there;
the guest is a `vm` host whose machine is QEMU's, as the UTM guest's is on
aarch64.

Order 13, Hyper-V. A generation 2 machine on the Windows host, beside WSL2
and the VMware guest. It is intended to become a graphical guest, but no 3D
guest graphics are available, so the order verifies that the shared Niri and
Noctalia profile is usable with software rendering before adopting it and
evaluates xrdp separately. Enabling Hyper-V on the host is the
maintainer's by hand, as installing VMware Workstation is; the Windows
domain reconciles what it deploys and does not manage it. Hyper-V needs a
Windows edition that carries it, which the order reads on the host before
anything else.

## Constraints recorded with the order

- aarch64 builds never use qemu binfmt on a WSL distribution: binfmt_misc is
  shared by every distribution. They run natively in the UTM guest or on a
  remote builder.
