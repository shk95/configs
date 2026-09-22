# Report: automate guarded NixOS installation and deployment

kind: report
spec: docs/work/unixlike/installation-and-deployment/spec.md
status: pending

The automatic installation increment is verified. Deployment topology, the
operator procedure and all installed-host evidence remain pending. No real
disk was formatted, no host was installed and no configuration was activated.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | Commits bc73343 and ff4af10 add the three isolated inputs and lock disko at `725ea35e410ad83be4931d1bff7e090eacaf3563`, nixos-anywhere at `1c2f124e970fed2a49bd14ce0a8b4e9bff74d3b4` and deploy-rs at `e760371d631165e7d8de5b0dcf148e21ec4c16f0`. At a7e7d8f, `nix flake check --no-build path:./unixlike` evaluates the disko module and `/nix/store/lcvis00widafa6jckgn5gj7znpkrkzqq-nixos-anywhere-1.13.0.drv`. The deploy-rs executable and schema check belong to AC6 and remain pending. |
| AC2 | verified | At a7e7d8f, `unixlike/tool/checks/flake-test` reads the real VMware, UTM and desktop layouts and passes their positive and negative assertions. The two guests compose `nixos.installExt4`; the desktop composes `nixos.installLuksBtrfs`; WSL and OrbStack expose no installation class. Native x86_64 builds produce `/nix/store/d2vy46rnzqpa0f6b2bcbcnz36q68x4nv-nixos-system-vm-26.11.20260916.b1b8759` and `/nix/store/jjgld6myzsbiha19jdh0wr49djczx51k-nixos-system-desktop-26.11.20260916.b1b8759`. |
| AC3 | verified | At a7e7d8f, `unixlike/tool/checks/install-plan-test` proves that `unixlike/tool/install-plan` writes a locked wrapper and review file for `vm` plus `/dev/disk/by-id/configs-install-plan-fixture`, then refuses `/dev/sda`, an unknown host, NixOS-WSL, an existing destination and surplus arguments. The NixOS assertion separately refuses a forced `/dev/sda`, and every real installable host evaluates with the inert `INSTALL_TARGET_REQUIRED` value and `disko.enableConfig = false`. |
| AC4 | verified | On 2026-09-23, at a7e7d8f, the pinned nixos-anywhere `--vm-test` path selected the portable form of disko's real `vm` install test and completed under QEMU TCG in 478 seconds as `/nix/store/47w9sdic4dk424sjs5m687nm7cs2g3n5-vm-test-run-disko-vm-disko`. It partitioned and formatted a disposable 4 GiB disk, installed the real VMware-shaped toplevel, wrote systemd-boot, powered off, booted from that disk and proved hostname `vm`, root label `nixos`, EFI label `boot`, a running sshd with password and root login disabled, and no failed system unit. No installed guest or physical device was opened. |
| AC5 | verified | At a7e7d8f, `nix flake check --no-build path:./unixlike` evaluates all NixOS configurations. UTM evaluates to `/nix/store/vpwmpvj81f559y1xla8f497ndp0kkdin-nixos-system-utm-26.11.20260916.b1b8759.drv`; its portable installation test also evaluates, while no aarch64 build is claimed. The desktop layout and portable encrypted install test evaluate, and only its ordinary toplevel receives x86_64 build evidence in AC2; physical installation and runtime remain pending. |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | |
| AC10 | pending | |
