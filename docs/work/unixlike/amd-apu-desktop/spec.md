# Build and certify the AMD APU Niri desktop

kind: spec
date: 2026-09-23
scope: unixlike
status: approved
review-by: 2026-10-23
issue: #335

Agreed with the maintainer on 2026-09-23 as roadmap order 9. The order is
split at the evidence boundary: this checkout can define, evaluate and build
the x86_64 desktop, while only the physical host can supply hardware review,
runtime, installation and activation evidence.

## Problem

The inventory declares `desktop`, but its class is still an evaluation-only
ext4 placeholder with no account or home. It does not describe the selected
Niri and Noctalia environment, AMD APU graphics, encrypted Btrfs storage or
desktop networking. Treating that placeholder as installable would also hide
the fact that its account and state version are provisional and that no real
hardware configuration has been reviewed.

Issue #20 is historical input. Its AMD APU, UEFI, LUKS2, Btrfs, zram and
evidence boundaries remain relevant; its GNOME direction is superseded by the
accepted Niri and Noctalia base.

## Decisions

### Compose existing classes at the one composition boundary

The `desktop` row in `unixlike/modules/flake/configurations.nix` composes
`nixos.desktop`, `nixos.headless` and `nixos.graphical`, with
`homeManager.shared`, `homeManager.desktop` and
`homeManager.linuxGraphical`. The headless class remains the account, SSH and
recovery base. Feature modules continue to contribute only to classes and name
no host.

This order changes the declared desktop only. The VMware and UTM guests remain
headless until order 10.

### Declare a portable AMD APU machine base and review facts later

The desktop class enables early AMDGPU loading, redistributable firmware and
AMD microcode. The graphical class already owns Mesa graphics and the Wayland
session. Modern Mesa supplies the AMD Vulkan and VA-API implementations, so no
vendor package or driver override is added.

The tracked class contains no generated `hardware-configuration.nix`, disk
UUID, monitor description or kernel module list inferred from a machine that
has not been inspected. Before installation, the maintainer reviews the
installer's generated hardware facts and adds only facts that the generic
class lacks. That review is physical-host evidence, not something evaluation
can invent.

### Fix the storage contract by labels and subvolumes

The machine boots with UEFI systemd-boot. A partition labelled `cryptroot`
holds one LUKS2 container that is unlocked manually in the initrd. Its Btrfs
file system provides `@`, `@home` and `@nix` subvolumes at `/`, `/home` and
`/nix`; each uses `compress=zstd` and `noatime`. The EFI system partition is
labelled `boot`. Zram supplies swap, so the desired state declares no disk swap
partition.

Labels and subvolume names are an installation contract rather than observed
hardware facts. The installation procedure must create them exactly and must
show the destructive disk target before writing it. Disk selection and
partitioning remain maintainer actions.

### Keep installation identity provisional until the host answers

The existing inventory account `user1` and state version `26.11` remain the
values used for evaluation and build. They are not certified installation
facts. Before activation, the maintainer confirms or corrects the account and
sets the state version to the release of the installation medium. A source
change caused by that confirmation gets its own reviewed increment before the
first switch.

### Separate automatic and physical evidence

This checkout evaluates every host, builds the x86_64 desktop toplevel and
checks the composed options. It does not activate a host. The physical lane
reviews hardware, installs the disk, proves AMD rendering, Vulkan and VA-API,
observes displays, Korean input, audio and networking, then verifies reboot and
previous-generation rollback. The report stays pending after the automatic
increment and ends only when those observations exist.

## Increments

1. Add this spec and report and open the execution issue.
2. Replace the placeholder with the AMD APU/storage class, compose the shared
   headless and graphical layers, add evaluation fixtures, build the x86_64
   toplevel and record automatic evidence.
3. On the physical host, review hardware facts and identity, install and
   activate only with explicit authorization, then record native runtime,
   reboot and rollback evidence.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The desktop alone composes the desktop, headless and graphical system classes and the shared, desktop and Linux graphical home classes; the VM guests remain headless. | evaluation |
| AC2 | The desktop evaluates with UEFI systemd-boot, manual LUKS2 unlock of the labelled container, the three declared Btrfs subvolumes with compression, and zram without disk swap. | evaluation, build |
| AC3 | The desktop evaluates with AMDGPU, firmware, AMD microcode, Mesa graphics and NetworkManager, with no invented UUID, monitor value or generated hardware file. | evaluation, build, review |
| AC4 | The managed account and state version remain explicitly provisional until the physical installation confirms or corrects them. | review |
| AC5 | The x86_64 desktop toplevel builds natively from the locked inputs, and unrelated declared hosts continue to evaluate. | evaluation, build |
| AC6 | The installation procedure names the destructive boundary, hardware and identity review, manual LUKS unlock and recovery path without claiming that the repository performed them. | review |
| AC7 | The installed physical host identifies its AMD APU and proves hardware rendering, Vulkan and VA-API plus usable displays, Korean input, audio and networking. | native runtime |
| AC8 | An explicitly authorized activation, disk boot, reboot and previous-generation rollback succeed on the physical host. | activation, native runtime |
| AC9 | `Required checks` passes on the head of every pull request of this work before it merges. | evaluation |

## Ownership amendment, 2026-09-25

The automatic evidence above describes the former final `desktop` output and
remains historical evidence. Item 17 moved that provisional final instance,
its account and state version, and its future installation to private
`configs-hosts/hosts/desktop/`. The public provider keeps the AMD desktop,
headless, graphical and storage classes and exercises them through synthetic
fixtures. In the private consumer, confirm the provisional identity and
installation medium before installation; its native final build and physical
runtime must be recorded there. AC7 and AC8 remain pending until the physical
machine supplies the observations and authorized activation. The final
desktop report here links that consumer evidence when the work resumes.
