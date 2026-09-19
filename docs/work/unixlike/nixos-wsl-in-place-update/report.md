# Report: update the registered NixOS-WSL distribution in place

kind: report
spec: docs/work/unixlike/nixos-wsl-in-place-update/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | On x86_64-linux at the commit that turns channels off. Evaluation: `nixosConfigurations.nixos` evaluates and `config.nix.nixPath` is `nixpkgs=flake:nixpkgs` alone (`flake-test` checks it); the toplevel derivation moves from `kksxcq51…` on `dev` f2a8595 to `4flr7mgw…`, while `homeConfigurations.user1` (`l5k66knp…-home-manager-generation.drv`) and `darwinConfigurations.shk-macbook` (`bifca69m…-darwin-system-26.11.4cff07d.drv`, foreign evaluation) are the same derivations on both trees. Build: `just nixos-build` produced `/nix/store/ac7p0dch…-nixos-system-nixos-26.11.20260916.b1b8759`; the home generation built at pre-push. The Darwin toplevel is not built on this host. |
| AC2 | verified | The rendered `config.system.build.tarballBuilder` script, built on both trees: on `dev` f2a8595 it carries `nix-channel --add …/NixOS-WSL/archive/refs/heads/main.tar.gz nixos-wsl` (2 lines naming a channel); at this commit it carries none. |
| AC3 | verified | `unixlike/tool/checks/flake-test`, in the unit tagged `INV unixlike/nixos-no-channel`: a module that forces `nix.channel.enable = true` is refused by the tagged assertion, and the real configuration evaluates clean. Mutation runs, each restored: with the assertion made always true the refusal fixture fails ("was not refused"); with the option set to true the clean fixture fails. |
| AC4 | pending | |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | |
