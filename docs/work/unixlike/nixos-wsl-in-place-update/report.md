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
| AC4 | pending | On the Ubuntu distribution (x86_64-linux), at the commit that adds the recipes: `just nixos-test`, `nixos-switch`, `nixos-rollback` and `nixos-generations` each exit 1 before any `sudo` with "This host is not NixOS (/etc/NIXOS is absent)…", and `just nixos-eval` prints the toplevel derivation (`…-nixos-system-nixos-26.11.20260916.b1b8759.drv`). Still owed, on the NixOS distribution: `just home-switch` refuses there, and the host-name half of the guard. |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | What the reviewer reads: `CONTRIBUTING.md` § "Update the registered NixOS-WSL distribution" and the paragraph that links it from the import section (the procedure, the cleanup step and when its channel line must run, rollback and its window, re-import as recovery), landed by #277; `tool/doctor.sh`, which names `just nixos-test` and `just nixos-switch` on NixOS and says the standalone home is not activated there, also #277; the paragraph dated 2026-09-19 in `docs/policy/decisions/unixlike/nixos-wsl-system-layer-ownership.md` (the rejected split and its cost); and the paragraph in `docs/status/unixlike.md` that says what is declared and what the host still owes. Awaits review. |
