# Report: install a headless aarch64 NixOS guest on UTM

kind: report
spec: docs/work/unixlike/utm-headless-guest/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Evaluation on the aarch64 Darwin host at 38e5cee: `nixosConfigurations.utm` evaluates (`as9fqcav…-nixos-system-utm`) from `nixos.utm`, `nixos.headless` and `home.shared`, with no failed assertion; `unixlike/modules/host/placeholder.nix` defines `vmware`, `orbstack` and `desktop` only. The `drvPath` of the `nixos`, `vm`, `orbstack` and `desktop` toplevels, of the standalone home's activation package and of the Darwin system, taken at 224164f before the work, are each identical at 38e5cee (`4flr7mgw…-nixos-system-nixos`, `g8zr0v6z…-nixos-system-vm`, `2vffvvvf…-nixos-system-orbstack-lxc`, `j7rzvfqb…-nixos-system-desktop`, `l5k66knp…-home-manager-generation`, `bifca69m…-darwin-system`). `unixlike/tool/checks/test` exits 0 with all seven configurations `eval ✓`; `utm` is reported `build — targets aarch64-linux`. |
| AC2 | verified | Evaluation, `unixlike/tool/checks/flake-test` at 38e5cee, in the unit tagged `INV unixlike/headless-key-only`: on `utm` the entry's account is a normal user in `wheel` with zsh as its shell and every password field null, no account carries an authorized key, sudo asks for a password, sshd is enabled on 22 with password, keyboard-interactive and root login off, the firewall is on and opens 22 alone, channels are off, and the home is the entry's account alone. Added to the real host, each of these is refused by the class's assertions: a second TCP port, a UDP port, a port opened on one interface, the firewall turned off, password authentication, a root login, an authorized key, an initial password, and a passwordless sudo; the unextended host passes clean. |
| AC3 | verified | Evaluation at 38e5cee: `flake-test`, in the unit tagged `INV unixlike/desktop-not-wsl`, finds no `wezterm` in the `utm` home's packages and finds it in the Darwin home's; `tool/checks/composition` passes over 46 feature files, none of which names a host flavour, and the new fragments read the account from `host.user`. |
| AC4 | verified | Evaluation at 38e5cee: `unixlike/modules/host/utm.nix` names the file systems by label and imports nixpkgs' QEMU guest profile; the tree holds no UUID, MAC address or generated hardware configuration for the guest, and `tool/version-control/hygiene` passes over 361 tracked paths. |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | |
| AC10 | pending | |
