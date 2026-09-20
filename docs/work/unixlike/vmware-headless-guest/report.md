# Report: install a headless x86_64 NixOS guest on VMware Workstation

kind: report
spec: docs/work/unixlike/vmware-headless-guest/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Evaluation on the x86_64 WSL host at c73b5dd: `nixosConfigurations.vm` evaluates (`2k390ll6…-nixos-system-vm`) from `nixos.vmware`, `nixos.headless` and `home.shared`, with no failed assertion; `unixlike/modules/host/placeholder.nix` defines `desktop` only. The `drvPath` of the `nixos`, `utm`, `orbstack` and `desktop` toplevels, of the standalone home's activation package and of the Darwin system, taken at 9bdcf48 before the work, are each identical at c73b5dd (`4flr7mgw…-nixos-system-nixos`, `as9fqcav…-nixos-system-utm`, `k7rvgmsr…-nixos-system-orbstack-lxc`, `j7rzvfqb…-nixos-system-desktop`, `l5k66knp…-home-manager-generation`, `bifca69m…-darwin-system`); `vm` alone moved, from `g8zr0v6z…`. `unixlike/tool/checks/test` exits 0 with all seven configurations `eval ✓`. |
| AC2 | verified | Evaluation, `unixlike/tool/checks/flake-test` at c73b5dd, in the unit tagged `INV unixlike/headless-key-only`, which now runs over every host of kind `vm` and requires one under each hypervisor: on `vm`, as on `utm`, the entry's account is a normal user in `wheel` with zsh as its shell and every password field null, no account carries an authorized key, sudo asks for a password, sshd is enabled on 22 with password, keyboard-interactive and root login off, the firewall is on and opens 22 alone, channels are off, and the home is the entry's account alone. Added to the real host, each of these is refused: a second TCP port, a UDP port, a port opened on one interface, the firewall turned off, password authentication, a root login, an authorized key, an initial password, and a passwordless sudo; the unextended host passes clean. Read from the evaluated `vm` configuration: `virtualisation.vmware.guest.enable` and `.headless` are true, the X server is off, `vmw_pvscsi` is an initrd module and `mptspi` and `nvme` are available ones. No fixture holds the guest tools' form, because no invariant states it. |
| AC3 | verified | Evaluation at c73b5dd: `flake-test`, in the unit tagged `INV unixlike/desktop-not-wsl`, finds no `wezterm` in the `vm` home's packages and finds it in the Darwin home's; `tool/checks/composition` passes over 49 feature files, none of which names a host flavour. |
| AC4 | verified | Evaluation at c73b5dd: `unixlike/modules/host/vmware.nix` names the file systems by label and writes no module list; the tree holds no UUID, MAC address or generated hardware configuration for the guest, and `tool/version-control/hygiene` passes over 373 tracked paths. `docs/policy/decisions/unixlike/x86-64-guest-runs-on-vmware-workstation.md` states the choice, that VMware Workstation is installed by hand, and Hyper-V and QEMU/KVM as later lanes with their costs; `tool/version-control/records` and `invariants` pass. |
| AC5 | verified | Build on the x86_64 WSL host: `nix build` of the `vm` toplevel, the derivation `2k390ll6…` that c73b5dd evaluates to, exits 0 and realises `yi3x4fhq…-nixos-system-vm`. `unixlike/tool/checks/test` does not build it — it reports `vm` as `not activatable here (already in the store)` — so this row rests on the direct build. A build proves the closure realises, not that it boots. |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | |
| AC10 | pending | |
