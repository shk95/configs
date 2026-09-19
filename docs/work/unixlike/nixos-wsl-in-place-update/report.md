# Report: update the registered NixOS-WSL distribution in place

kind: report
spec: docs/work/unixlike/nixos-wsl-in-place-update/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC2 | pending | |
| AC3 | pending | |
| AC4 | pending | On the Ubuntu distribution (x86_64-linux), at the commit that adds the recipes: `just nixos-test`, `nixos-switch`, `nixos-rollback` and `nixos-generations` each exit 1 before any `sudo` with "This host is not NixOS (/etc/NIXOS is absent)…", and `just nixos-eval` prints the toplevel derivation (`…-nixos-system-nixos-26.11.20260916.b1b8759.drv`). Still owed, on the NixOS distribution: `just home-switch` refuses there, and the host-name half of the guard. |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | |
