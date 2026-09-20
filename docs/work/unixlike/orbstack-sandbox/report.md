# Report: bring the isolated OrbStack machine under the flake

kind: report
spec: docs/work/unixlike/orbstack-sandbox/spec.md
status: done

## Verification boundary and disposition

Follow-up: `docs/work/unixlike/binfmt-scope-investigation/report.md` records
the read-only WSL and OrbStack comparison of 2026-09-21, with primary-source
review and an unprivileged disposable container. It adds evidence about the
namespace arrangement, not a direct-registration experiment. The dated
disposition below is retained as the record that preceded that investigation.

Clarified 2026-09-21 after the maintainer's review of the completion record.
The observations below are those of 2026-09-20; this clarification adds no
new machine experiment or runtime evidence.

The machines were observed to share a kernel and to have distinct user
namespaces with one-to-one UID mappings. AC2 verifies that this host declares
no binfmt emulation or registration and refuses either when added to its
configuration. AC7 records the service mask and absence of a `binfmt_misc`
mount in the inspected machine. Neither observation tests the reach of a
registration made directly inside a machine.

No direct registration was attempted. Whether such a registration would
affect another machine or OrbStack's container engine remains unverified;
the spec's amended paragraph suggesting that it would stay in the machine
is a hypothesis, not a result. Sharing a kernel and mapping UID 0 one to one
do not establish that registrations propagate between machines.

Disposition for this work: retain `done`, because AC1–AC10 do not require
that experiment, and record its result as unknown rather than passed or
failed. The existing `unixlike/orbstack-shared-kernel` invariant assigns
emulation to OrbStack and explicitly does not depend on the answer. This
clarification neither changes that rule nor certifies isolation against a
manual registration.

No separate investigation is started by this clarification. If a future
change needs machine-owned emulation, relies on binfmt isolation, or finds
that an OrbStack update changes the observed mask or namespace arrangement,
the repository maintainer should decide a separate investigation before
that change relies on either propagation or isolation. Start with read-only
source and namespace inspection. If a direct registration experiment is
needed, prepare its affected machines and container workloads, observations,
cleanup and recovery procedure, and stop conditions for the maintainer's
explicit approval. Its spec, report and execution issue belong to that new
work; no such experiment is authorized by this completion record.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Evaluation on the aarch64 Darwin host at 9198817: `nixosConfigurations.orbstack` evaluates (`7iqn3iqz…-nixos-system-orbstack-lxc`) from `nixos.orbstack` and `home.shared`, with no failed assertion; `unixlike/modules/host/placeholder.nix` defines `vmware` and `desktop` only. The `drvPath` of the `nixos`, `utm`, `vm` and `desktop` toplevels, of the standalone home's activation package and of the Darwin system, taken at 51be325 before the work, are each identical at 9198817 (`4flr7mgw…-nixos-system-nixos`, `as9fqcav…-nixos-system-utm`, `g8zr0v6z…-nixos-system-vm`, `j7rzvfqb…-nixos-system-desktop`, `l5k66knp…-home-manager-generation`, `bifca69m…-darwin-system`). `unixlike/tool/checks/test` exits 0 with all seven configurations `eval ✓`; `orbstack` is reported `build — targets aarch64-linux`. |
| AC2 | verified | Evaluation, `unixlike/tool/checks/flake-test` at 9198817, in the unit tagged `INV unixlike/orbstack-shared-kernel`: on `orbstack` the entry's account has UID 501, is in `wheel` and `orbstack`, whose GID is 67278, has zsh as its shell and every password field null; users are immutable; sshd is off; `eth0` is matched by a systemd-networkd network with dhcpcd and `useDHCP` off; resolved is off and `/etc/resolv.conf` is OrbStack's; the watchdog of `systemd-logind` is 0; channels are off; no emulated system, no binfmt registration and no certificate is declared; the home is the entry's account alone. Added to the real host, an emulated system and a registration are each refused by the class's assertion, and the unextended host passes clean. |
| AC3 | verified | Evaluation at 9198817: `flake-test`, in the unit tagged `INV unixlike/desktop-not-wsl`, finds no `wezterm` in the `orbstack` home's packages and finds it in the Darwin home's; `tool/checks/composition` passes over 48 feature files, none of which names a host flavour, and the new fragments read the account from `host.user`. |
| AC4 | verified | Evaluation at 9198817: the tree holds none of the three files OrbStack generated, and `unixlike/modules/host/orbstack.nix` declares no certificate, which the fixture of AC2 also holds the host to; the machine's identifier, address and the Mac's certificate authority appear nowhere; `tool/version-control/hygiene` passes. |
| AC5 | verified | Review at aeee77d (#314, corrected by #315): `CONTRIBUTING.md` § Create the OrbStack machine opens by naming every action that changes the host as the maintainer's to run, and states how the machine is created isolated, with the account that must be the entry's; how it is switched to the flake — a clone that names a ref, the image's channel removed, a first switch that names the output and is expected to exit with status 4, a restart that reads the machine back, the channel's leftovers removed; how it is updated with the host-bound recipes and rolled back only within this flake's generations; how it is recovered by deleting and creating it again; and how OrbStack's generated files are compared after an OrbStack update. A reviewing agent read the section against the machine first and its findings were corrected; the section was then run from a newly created machine on 2026-09-20, which is where the ref, the exit status and the leftovers came from. Reviewed and confirmed by the repository maintainer on 2026-09-20. |
| AC6 | verified | Build inside the machine (aarch64 NixOS under OrbStack 2.2.3 on the Mac) on 2026-09-20, in two machines: in the first, at 98b1a23, the `orbstack` toplevel built from a clone as `kyq7zrpv…-nixos-system-orbstack-lxc-26.11.20260916.b1b8759`, from `7iqn3iqz…`, the derivation the Mac had evaluated; in the machine created again from the image, at d616c51, the first switch and `just nixos-test` built `c6ibfvh9…-nixos-system-orbstack-lxc`, the same path the first machine had built at e562c49. |
| AC7 | verified | Native runtime on 2026-09-20 inside the machine that exists now — created isolated with `orb create --isolated nixos:25.11 orbstack`, switched at d616c51 — read from the Mac through `orb -m orbstack` after `orb restart orbstack`: the host answers to `orbstack`; the session enters as `shk`, UID 501, and its shell is `/run/current-system/sw/bin/zsh`; `sudo -n` works; `nix-channel` is absent and the image's channel links under root's profile were removed; `machine.orbstack.isolated` is true, no file system of the Mac is mounted and `SSH_AUTH_SOCK` is empty; `/run/systemd/system/systemd-binfmt.service` is a link to `/dev/null` written at that boot and no `binfmt_misc` is mounted; the system and the account's user manager both answer `running` with no failed unit. The same reading of the first machine, created not isolated and isolated afterwards, at e562c49, agreed and added: `cache.nixos.org` resolves through OrbStack's `resolv.conf` and answers over HTTPS, `nix flake metadata` resolves the clone's flake, `NIX_PATH` is `nixpkgs=flake:nixpkgs`, sshd is inactive, and OrbStack's `mac` command, run from a login bash, fails with `dial: no such file or directory`. Under the first generation of this flake, at 98b1a23, the first machine answered `degraded`: `sys-kernel-debug.mount` failed with permission denied at the switch and at every boot, which e562c49 corrects in the class; OrbStack's own image answers `degraded` on the same unit in a machine created isolated. Observed and not asked for: a zsh session does not carry OrbStack's path additions, which come from `/etc/profile` and which no `/etc/zshenv` repeats; each machine runs in a user namespace of its own that is not the kernel's initial one, with UIDs mapped one to one; OrbStack writes no certificate into a machine created isolated; and `/etc/nixos` is kept for the procedure's reading after an OrbStack update. |
| AC8 | verified | Activation inside the machine on 2026-09-20, run by the session on the maintainer's approval of that day, in two machines. In both, the first switch named the output, `sudo nixos-rebuild switch --flake "path:./unixlike#orbstack"`, after the image's `nixos` channel was removed, activated the first generation of this flake and exited 4 with the OrbStack session intact: at 98b1a23 on `sys-kernel-debug.mount` and on the reload of `dbus-broker.service`, and at d616c51, with that mount suppressed, on the reload alone, which times out because the message bus changes implementation between the image's release and the flake's; after `orb restart orbstack` the system is `running`. In the machine that exists now, from the clone at d616c51, `just nixos-test` and `just nixos-switch` each exited 0 on `c6ibfvh9…`; with one uncommitted line in the clone's `unixlike/modules/host/orbstack.nix` that adds `/etc/orbstack-rollback-probe`, they activated `z5b04xra…` as generation 4 and the file existed; `just nixos-rollback` switched the profile from 4 to 3, exited 0 and removed it; with the line reverted and the clone clean, `just nixos-switch` activated `c6ibfvh9…` again as generation 5. The first machine had shown the same between its generations 5 and 4, and that `just nixos-rollback` onto its degraded first generation switches the profile and exits 4. The image's generations were not rolled back to. |
| AC9 | verified | At a334f5c the entry's `user` is `shk` and its `stateVersion` is `25.11`. Inside the machine the session's account is `shk` with UID 501, and `/etc/nixos/configuration.nix`, which OrbStack generated from its image, carries `system.stateVersion = "25.11"`; the image's generations are `lxc-25.11.12484`. `docs/status/unixlike.md` states the host as switched to the flake and names evaluation, build, native runtime and activation separately, each with the commit and the place it was observed. A reviewing agent checked both against the machine before the review. Reviewed and confirmed by the repository maintainer on 2026-09-20. |
| AC10 | verified | `Required checks` passed on the head of each pull request of this work before it merged: #312 (08442c4, merged as 98b1a23), #314 (b9c4b97, merged as d8c2121) and #315 (4324ced, merged as aeee77d). The pull request that carries this row is held to the same check by the merge gate before it lands, and the `Work closure` run on its push is what closes #311. |
