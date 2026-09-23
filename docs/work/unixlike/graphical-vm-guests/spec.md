# Adopt Niri and Noctalia on the VM guests

kind: spec
date: 2026-09-23
scope: unixlike
status: approved
review-by: 2026-10-23
issue: #339

Agreed with the maintainer on 2026-09-23 as the automatic part of roadmap
order 10. The VMware and UTM guests are installed and retain their headless
recovery layer. This checkout can compose and evaluate both architectures,
build and test the x86_64 result, and document the activation boundary. Only
the installed guests can supply disk-capacity, login, rendering, input, audio,
reboot, rollback and activation evidence.

## Problem

Roadmap order 8 established the shared Niri and Noctalia classes and proved
them in a disposable x86_64 VM. The physical desktop now consumes those
classes, while both installed VM guests still compose only their hypervisor,
headless and shared-home layers. Their desired state therefore stops before
the graphical environment they were created to run.

The VMware guest has a 20 GiB disk and an already verified test, switch and
rollback path. The UTM guest is aarch64 and must build natively there. Neither
guest's current free capacity or graphical runtime can be inferred from this
checkout, and no evaluation or foreign build authorizes activation.

## Decisions

### Compose the same graphical classes into both guest rows

The `utm` and `vmware` rows in
`unixlike/modules/flake/configurations.nix` keep their hypervisor and
`nixos.headless` system classes and add `nixos.graphical`. Their homes keep
`homeManager.shared` and add `homeManager.desktop` plus
`homeManager.linuxGraphical`. Feature modules remain host-independent and the
composition table remains the only place that selects classes for a host.

NixOS-WSL and OrbStack remain non-graphical. The physical desktop composition
is unchanged.

### Let each hypervisor retain its own machine integration

UTM keeps the QEMU guest profile, virtio devices and serial recovery console.
VMware changes from the headless open-vm-tools package to the full guest
package so the graphical guest receives the integration nixpkgs provides,
including its vmblock mount and user wrapper. No display resolution, monitor
identity, virtual GPU parameter or host network value is invented.

The graphical class continues to own Niri, Noctalia, greetd, portals, audio,
input and applications. Hypervisor modules do not duplicate those settings.

### Prove the automatic boundary without touching installed guests

Evaluation fixtures verify the exact class reach, headless recovery, VMware
integration and UTM machine properties. The existing booted graphical and
headless NixOS tests continue to exercise the actual shared classes under
QEMU. The x86_64 VMware toplevel builds natively and its closure size is
recorded. The aarch64 UTM toplevel evaluates here; its native build remains an
installed-guest check.

Before activation, each guest builds its own output, records free space and
the realised closure, and stops if the build cannot complete with useful
headroom. VMware is exercised first because its headless native runtime and
rollback path are already verified. UTM follows after the VMware evidence is
recorded. Both use `just nixos-test` before `just nixos-switch`, retain SSH as
the recovery route, reboot once, and prove rollback between two generations
of this flake.

## Increments

1. Add this spec and report and open the execution issue.
2. Compose the graphical classes into both guests, add evaluation fixtures,
   build the x86_64 VMware toplevel and record automatic evidence.
3. Add the capacity, activation, graphical runtime and recovery procedure in
   the repository scope and record its review separately.
4. On explicit authorization, verify capacity and activate VMware first, then
   UTM; record each host's native runtime and rollback evidence.

## Acceptance

Amended 2026-09-23: AC8 no longer requires VMware to precede UTM. The
maintainer requested UTM first on that date; each guest still owes its own
native build, graphical runtime, activation, reboot and rollback evidence.
This amendment also supersedes the guest ordering in Decisions and increment
4; no evidence requirement is removed.

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The UTM and VMware compositions retain their hypervisor and headless classes and add the shared graphical system and home classes; the composition table alone makes that selection. | evaluation |
| AC2 | The VMware output evaluates with full open-vm-tools graphical integration, key-only SSH recovery and the shared Niri/Noctalia environment, and its locked x86_64 toplevel builds natively. | evaluation, build |
| AC3 | The UTM output evaluates for aarch64 with its QEMU guest devices and serial recovery console plus the shared graphical environment; its native build remains pending for the installed aarch64 guest. | evaluation |
| AC4 | The booted x86_64 graphical and headless VM checks still pass with the same shared classes, proving the graphical services and account/SSH/firewall recovery contracts independently of a physical display. | native runtime |
| AC5 | NixOS-WSL and OrbStack remain non-graphical, and the physical desktop composition is unchanged. | evaluation, review |
| AC6 | The guest update procedure checks realised capacity before activation, orders test before switch, names graphical observations and preserves SSH, boot-menu and rollback recovery without claiming they ran. | review |
| AC7 | On the installed VMware guest, native build, test activation, Niri/Noctalia login, rendering, Korean input, audio, networking, reboot, switch and rollback succeed with sufficient disk capacity. | build, native runtime, activation |
| AC8 | The installed UTM guest supplies its own native aarch64 build, graphical runtime, activation, reboot and rollback evidence, independently of the VMware execution order. | build, native runtime, activation |
| AC9 | `Required checks` passes on the head of every pull request of this work before it merges. | evaluation |
