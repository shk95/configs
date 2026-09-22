# Report: build and certify the AMD APU Niri desktop

kind: report
spec: docs/work/unixlike/amd-apu-desktop/spec.md
status: pending

Automatic implementation commit `1d56e4a` defines and checks the portable
desktop base. This report remains pending because the repository-scope
installation procedure and all physical-host evidence are separate
increments.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | `unixlike/modules/flake/configurations.nix` composes the desktop from `nixos.desktop`, `nixos.headless` and `nixos.graphical`, and its home from the three corresponding home classes. `unixlike/tool/checks/flake-test` verifies that only the desktop is graphical and that both VM guests remain headless. |
| AC2 | verified | `unixlike/tool/checks/flake-test` evaluates systemd-boot, label-based manual LUKS unlock, all three Btrfs subvolumes and options, the private ESP mount, zram and the absence of disk swap. The native desktop toplevel build produced `/nix/store/jjgld6myzsbiha19jdh0wr49djczx51k-nixos-system-desktop-26.11.20260916.b1b8759`. |
| AC3 | verified | The same fixture evaluates AMDGPU in the initrd, firmware, AMD microcode, default Mesa graphics, 32-bit graphics and NetworkManager, and refuses an unreviewed generated hardware file or UUID. Review found no monitor value or vendor graphics override. The native toplevel build includes the AMDGPU firmware and initrd. |
| AC4 | verified | The inventory, status document and accepted decision each identify `user1` and `26.11` as provisional values that must be confirmed or corrected before activation. |
| AC5 | verified | `nix flake check --no-build path:./unixlike` evaluated all declared outputs, the full `unixlike/tool/checks/flake-test` passed, and the locked x86_64 desktop toplevel built natively at the store path recorded for AC2. |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | |
