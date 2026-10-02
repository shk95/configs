# Report: build and certify the AMD APU Niri desktop

kind: report
spec: docs/work/unixlike/amd-apu-desktop/spec.md
status: pending

Automatic implementation commit `1d56e4a` defines and checks the portable
desktop base. The repository-scope installation procedure is merged. This
report remains pending because all physical-host evidence is a separate
increment.

The 2026-09-25 provider transition retired the public final `desktop` output.
AC1–AC6 and AC9 below are dated evidence from that output and its provider
classes. Private `configs-hosts/hosts/desktop/` owns the provisional final
instance and future native and physical evidence. AC7 and AC8 remain pending.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | `unixlike/modules/flake/configurations.nix` composes the desktop from `nixos.desktop`, `nixos.headless` and `nixos.graphical`, and its home from the three corresponding home classes. `unixlike/tool/checks/flake-test` verifies that only the desktop is graphical and that both VM guests remain headless. |
| AC2 | verified | `unixlike/tool/checks/flake-test` evaluates systemd-boot, label-based manual LUKS unlock, all three Btrfs subvolumes and options, the private ESP mount, zram and the absence of disk swap. The native desktop toplevel build produced `/nix/store/jjgld6myzsbiha19jdh0wr49djczx51k-nixos-system-desktop-26.11.20260916.b1b8759`. |
| AC3 | verified | The same fixture evaluates AMDGPU in the initrd, firmware, AMD microcode, default Mesa graphics, 32-bit graphics and NetworkManager, and refuses an unreviewed generated hardware file or UUID. Review found no monitor value or vendor graphics override. The native toplevel build includes the AMDGPU firmware and initrd. |
| AC4 | verified | The inventory, status document and accepted decision each identify `user1` and `26.11` as provisional values that must be confirmed or corrected before activation. |
| AC5 | verified | `nix flake check --no-build path:./unixlike` evaluated all declared outputs, the full `unixlike/tool/checks/flake-test` passed, and the locked x86_64 desktop toplevel built natively at the store path recorded for AC2. |
| AC6 | verified | Agent review on 2026-09-23 of `CONTRIBUTING.md` at `7190eae`, merged through #337: “Install the AMD APU desktop” makes every command the maintainer's to run, shows the selected whole disk and requires its exact typed confirmation before partitioning, confirms account and state version, creates manual LUKS2 unlock and the declared Btrfs layout, reviews generated hardware without adopting it wholesale, and gives both previous-generation and minimal-ISO recovery. No procedure command was run. PR #337 passed `Required checks` ([run 35771089835](https://github.com/shk95/configs/actions/runs/35771089835)). |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | verified | GitHub read on 2026-09-23: PR #336 at its final head `418df1e` passes `Required checks`; its Unix-like job, including every host evaluation, the desktop assertions and both booted VM tests, passes in 10m23s ([run 35769433012](https://github.com/shk95/configs/actions/runs/35769433012)). The PR then merged as `c12c323`. |
