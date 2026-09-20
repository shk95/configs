# Bring the isolated OrbStack machine under the flake

kind: spec
date: 2026-09-20
scope: unixlike
status: approved
review-by: 2026-10-31
issue: #311

Agreed with the maintainer in the session of 2026-09-20 on the Mac. Lane
`orbstack` of `docs/work/roadmap.md`, order 7, taken beside order 6, which
another session holds; the two share no outcome. The maintainer wants a
sandbox: a disposable aarch64 NixOS machine that cannot reach the Mac's files
or its ssh agent. No graphical use is planned for it.

## What was read on 2026-09-20

A machine named `orbstack` was created with OrbStack 2.2.3 from its NixOS
25.11 image and read before anything in it was changed.

- OrbStack writes three files under `/etc/nixos`. `configuration.nix` holds
  the account — named after the Mac's, UID 501, a system user shaped like a
  normal one, in `wheel` and `orbstack` — a sudo that asks for nothing,
  `users.mutableUsers = false`, the Mac's time zone, `eth0` under
  systemd-networkd with dhcpcd off, three certificates of which one is the
  Mac's own mkcert authority, and state version 25.11. `orbstack.nix`, which
  says it will be overwritten, sources OrbStack's profile fragments, points
  `/etc/resolv.conf` at OrbStack's, turns sshd off, sets the watchdog of
  eighteen systemd services to zero, includes an ssh client fragment that
  names OrbStack's agent proxy, and declares x86 platforms and the `orbstack`
  group. `incus.nix` holds the host name. A restart rewrote none of them.
- The machine is an LXC container without a user namespace: its root is root
  on the kernel every OrbStack machine and OrbStack's Docker share. OrbStack
  masks `systemd-binfmt.service` at every boot and mounts no `binfmt_misc`
  inside. Sessions come from an agent OrbStack injects beside systemd, not
  from sshd or a login; the account is locked and root's password is empty.
- The image has flakes off and a `nixos` channel registered, and neither
  `git` nor `just`.
- Not isolated, the machine mounts the Mac's `/Users`, `/private` and
  `/Volumes` read-write and proxies its ssh agent. Isolated — set that day
  with OrbStack's `machine.orbstack.isolated` and a restart — none of that is
  there and the network still is.
- The flake's `orbstack` output evaluates inside the machine to the
  derivation the Mac evaluates it to.

## Problem

1. **The `orbstack` host is a placeholder.** It imports the LXC container
   module and nothing else: no account, no home, none of what OrbStack needs
   from the guest. Switching the machine to it would remove the account
   OrbStack enters as.
2. **What OrbStack needs is written by OrbStack, outside the flake.** The
   generated files sit at an absolute path in the machine, mix facts about
   OrbStack with facts about this Mac, and announce that they will be
   overwritten.
3. **There is no procedure** for creating the machine, switching it to the
   flake, or recovering it.

## Decisions

### A `nixos.orbstack` class that declares what OrbStack needs, by hand

A file of its own under `modules/host/`, replacing the placeholder, holding
what is true of any OrbStack machine and of no particular Mac: the LXC
container module, `eth0` under systemd-networkd with dhcpcd off, OrbStack's
`resolv.conf` with resolved and resolvconf off, the profile fragments, the
watchdog settings, the `orbstack` group with its GID, sshd off, and no
emulated binfmt registration. The account is `host.user` with the shape
OrbStack gives it — UID 501, which is how OrbStack maps the Mac's first
account, a system user with a home, in `wheel` and `orbstack` — zsh as its
login shell the way `modules/shell/wsl.nix` selects it, immutable users, and
a sudo that asks for no password, because OrbStack's sessions carry no
authentication and the account has no password to ask for.

Left out on purpose, because the machine is an isolated sandbox: the
certificates, the ssh client fragment for the agent proxy, the `audio` group
and the x86 platforms. The time zone is the one the repository already
declares for its other NixOS host.

Rejected: importing `/etc/nixos/orbstack.nix` with `--impure`, because the
output would then evaluate only inside the machine and the evaluation check
and the merge gate reach every host; copying the generated files into the
tree, because they carry the Mac's account, time zone and certificate
authority; `nixos.headless`, because that class is sshd, a firewall and a
password, and this host has an injected agent, no listener and no password.
What this costs is stated: an OrbStack update may change what it generates,
and only a person reading the new `orbstack.nix` against the class finds
out. The procedure carries that step.

### The shared kernel is not the machine's to change

The class registers no binfmt emulation and asserts it, under an invariant of
its own: the registry belongs to the kernel OrbStack's Docker and every other
machine use. That OrbStack's own mask of `systemd-binfmt.service` survives an
activation is observed in the machine, not assumed.

### The home is `home.shared`

As on the UTM guest: the shared class alone, composed into the system, no
graphical class and no coding agents.

### Isolation is OrbStack's state, recorded in the procedure

Whether a machine is isolated is a setting of the OrbStack application on the
Mac, which this repository does not declare. The procedure creates the
machine isolated, and the native runtime criterion reads from inside that the
Mac's file system and ssh agent are absent. Declaring OrbStack's settings
through nix-darwin, and using the machine as the Mac's Linux builder, are not
part of this work.

### Created by OrbStack, switched once by name, rebuilt from a clone

`orb create --isolated` makes the machine under the inventory's host name.
Isolation leaves no shared path, so the repository is cloned inside. The
first switch names the output and turns flakes on for that one command,
because the image has neither; from then on the host-bound recipes apply
(`just nixos-test`, `just nixos-switch`, `just nixos-rollback`). Recovery is
deleting the machine and creating it again, which takes seconds and is why
nothing here tries to preserve one. The procedure is written into
`CONTRIBUTING.md` beside the other NixOS hosts'.

### The inventory entry

`identity.nixosHosts.orbstack` keeps its name and `shk`; its state version
becomes `25.11`, the release of OrbStack's image.

## Increments

Cut at the evidence lanes and scopes.

1. The evaluation lane (`unixlike`): this spec and its report as the first
   commit, then `nixos.orbstack`, the composition row, the inventory entry,
   the invariant and the fixtures, the status, and the report rows they
   verify.
2. `repository`: the procedure in `CONTRIBUTING.md`, the rationale for the
   shared-kernel rule beside the one WSL has, and the roadmap's note that
   orders 6 and 7 run side by side.
3. The machine's lanes (`unixlike`): build, native runtime and activation
   evidence from inside the machine, the status, and the report's end; the
   roadmap row follows in `repository`.

Amended 2026-09-20: corrections to what was read, and no criterion changes. The spec says the machine is an LXC container without a user namespace; that was inferred from its identity UID map. Read again the same day after a reviewing agent questioned it, each machine runs in a user namespace of its own that is not the kernel's initial one — two machines read side by side had different ones — with UIDs mapped one to one, so root in it is still UID 0 on the shared kernel, and a binfmt registration made in it would probably stay in it, which was not tried. The decision stands as written: the class registers nothing and asserts it. The machine was then deleted and created again the way the procedure says, isolated from the start, to read what had been left unread: OrbStack writes no certificate into a machine created isolated, and the rest of what it generates is the same; the debug file system mount fails under OrbStack's own image there too; and the first switch from the image exits non-zero whatever the class holds, because the reload of the message bus times out when its implementation changes between the image's release and the flake's, which a restart settles. The list of what the class leaves out also gains what restates a default or configures what is off: the `documentation.*` options, the dhcpcd options and `useDefaultShell`.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | `nixosConfigurations.orbstack` evaluates with the `nixos.orbstack` class and the `home.shared` home; `modules/host/placeholder.nix` no longer defines `orbstack`; the toplevel derivations of every other NixOS host, the standalone home and the Darwin system are unchanged. | evaluation |
| AC2 | On `orbstack`: the account named by the entry has UID 501, is in `wheel` and `orbstack`, has zsh as its shell and no password in tracked state; users are immutable; sshd is off; `eth0` is configured by systemd-networkd with dhcpcd off and `/etc/resolv.conf` is OrbStack's; channels are off; no binfmt emulation is registered. Fixtures prove each, and that a change which registers a binfmt emulation is refused. | evaluation |
| AC3 | No graphical program reaches the `orbstack` home, and no feature file names the host. | evaluation |
| AC4 | No file OrbStack generated, no certificate and no machine-unique identifier is tracked for the machine; the hygiene scan passes. | evaluation |
| AC5 | `CONTRIBUTING.md` states how the machine is created isolated, switched to the flake, updated, recovered by recreation, and re-read after an OrbStack update, with what is the maintainer's to run. | review |
| AC6 | The `orbstack` toplevel builds inside the machine. | build |
| AC7 | Inside the switched machine: the host answers to `orbstack`; an OrbStack session enters as the account in zsh; `sudo` works; names resolve and the network is reachable; `nix` runs flakes and no channel exists; the Mac's file system and ssh agent are absent; `systemd-binfmt.service` is masked and no `binfmt_misc` is mounted; the system is running with no failed unit; the machine comes back after a restart from the Mac. | native runtime |
| AC8 | The first switch names the output; after it `just nixos-test` then `just nixos-switch` from a clone inside the machine activate a generation built from this flake, and `just nixos-rollback` returns to the one before, between generations of this flake. | activation |
| AC9 | The inventory entry's `user` and `stateVersion` are the machine's, and `docs/status/unixlike.md` states the host with the evidence of each lane named separately. | review |
| AC10 | `Required checks` passes on the head of every pull request of this work before it merges. | evaluation |
