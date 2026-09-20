# Report: bring the isolated OrbStack machine under the flake

kind: report
spec: docs/work/unixlike/orbstack-sandbox/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Evaluation on the aarch64 Darwin host at 9198817: `nixosConfigurations.orbstack` evaluates (`7iqn3iqz…-nixos-system-orbstack-lxc`) from `nixos.orbstack` and `home.shared`, with no failed assertion; `unixlike/modules/host/placeholder.nix` defines `vmware` and `desktop` only. The `drvPath` of the `nixos`, `utm`, `vm` and `desktop` toplevels, of the standalone home's activation package and of the Darwin system, taken at 51be325 before the work, are each identical at 9198817 (`4flr7mgw…-nixos-system-nixos`, `as9fqcav…-nixos-system-utm`, `g8zr0v6z…-nixos-system-vm`, `j7rzvfqb…-nixos-system-desktop`, `l5k66knp…-home-manager-generation`, `bifca69m…-darwin-system`). `unixlike/tool/checks/test` exits 0 with all seven configurations `eval ✓`; `orbstack` is reported `build — targets aarch64-linux`. |
| AC2 | verified | Evaluation, `unixlike/tool/checks/flake-test` at 9198817, in the unit tagged `INV unixlike/orbstack-shared-kernel`: on `orbstack` the entry's account has UID 501, is in `wheel` and `orbstack`, whose GID is 67278, has zsh as its shell and every password field null; users are immutable; sshd is off; `eth0` is matched by a systemd-networkd network with dhcpcd and `useDHCP` off; resolved is off and `/etc/resolv.conf` is OrbStack's; the watchdog of `systemd-logind` is 0; channels are off; no emulated system, no binfmt registration and no certificate is declared; the home is the entry's account alone. Added to the real host, an emulated system and a registration are each refused by the class's assertion, and the unextended host passes clean. |
| AC3 | verified | Evaluation at 9198817: `flake-test`, in the unit tagged `INV unixlike/desktop-not-wsl`, finds no `wezterm` in the `orbstack` home's packages and finds it in the Darwin home's; `tool/checks/composition` passes over 48 feature files, none of which names a host flavour, and the new fragments read the account from `host.user`. |
| AC4 | verified | Evaluation at 9198817: the tree holds none of the three files OrbStack generated, and `unixlike/modules/host/orbstack.nix` declares no certificate, which the fixture of AC2 also holds the host to; the machine's identifier, address and the Mac's certificate authority appear nowhere; `tool/version-control/hygiene` passes. |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | |
| AC10 | pending | |
