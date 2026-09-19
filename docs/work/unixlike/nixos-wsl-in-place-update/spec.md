# Update the registered NixOS-WSL distribution in place

kind: spec
date: 2026-09-19
scope: unixlike
status: approved
review-by: 2026-10-31

Agreed with the maintainer in the session of 2026-09-19 and revised the same
day after an independent review whose findings were reproduced before they
were applied. Lane `wsl-nixos`, order 3 in `docs/work/roadmap.md`.

## Problem

The distribution was imported on 2026-09-06 and activated once since
(generation 2, #192, built from a working tree inside the distribution). No
documented path updates it in place, and what exists misleads:

1. **No recipe.** The `nixos-wsl` group in the `Justfile` has `nixos-build`,
   `nixos-tarball` and `nixos-stage`; nothing corresponds to
   `darwin-switch`, `darwin-generations` or a rollback.
2. **The one recorded command no longer works.** Generation 2 came from
   `nixos-rebuild switch --flake path:.#nixos`; the flake has lived under
   `unixlike/` since 2026-09-12.
3. **The rootfs carries a configuration and a channel nothing uses.**
   `wsl.tarball.configPath` is null and `nix.channel.enable` is true, so the
   import installed nixos-wsl's default `/etc/nixos/configuration.nix`
   (the nixos-wsl modules, `wsl.enable`, `defaultUser`, `stateVersion`) and
   registered a `nixos-wsl` channel (pinned `modules/build-tarball.nix`).
   nixos-wsl's welcome text advises `sudo nix-channel --update` and
   `sudo nixos-rebuild switch`. Read from the pinned sources, not yet on the
   host: the second does not switch to that file — `nix.nixPath` here is
   `nixpkgs=flake:nixpkgs` plus the channels directory and carries no
   `nixos-config` (nixpkgs `nixos/modules/misc/nixpkgs-flake.nix`), so a
   rebuild without `--flake` stops on the search path. The failure is safe
   but unexplained, and the file and the channel suggest a path that does
   not exist.
4. **`just switch` on NixOS activates the wrong home.** `home-switch`
   (aliases `switch`, `bootstrap`) has no NixOS guard and would activate the
   standalone Ubuntu home over the one the NixOS system composes;
   `switch-shell` already refuses on NixOS, and `tool/doctor.sh` still says
   a home can switch there.
5. **Nothing says how to roll back or when a re-import is right.** WSL has
   no boot loader, so rollback is `nixos-rebuild switch --rollback` or a
   `system-<n>-link`, inside the 14-day collection window
   (`unixlike/modules/nix/shared.nix`).

## Decisions

- **Updates happen inside the distribution, from a clone there.** The
  distribution clones this public repository; generation 2 was built from a
  working tree inside it. Building on Ubuntu and copying the closure
  (`nix copy`, `switch-to-configuration`) is rejected: more steps, and a
  second host's evaluation to trust.
- **Home Manager stays composed into the system.** Splitting it into a
  standalone home is rejected: the tarball's first boot would no longer
  carry the home, rollback would need two generation lists kept in step, and
  the UID the system declares (2000) and the home uses would sit in two
  evaluations. The cost accepted: a dotfile change needs `sudo` and a
  system evaluation. Recorded as a paragraph appended to the system-layer
  decision record for NixOS-WSL.
- **The channel goes; the default configuration file is removed, not
  replaced.** `nix.channel.enable = false` removes the channel path from
  `nix.nixPath`, the `nix-channel` command, and the tarball's channel
  registration. Replacing `/etc/nixos/configuration.nix` with a file that
  throws is rejected: the rebuild it would guard already fails on the search
  path, and a tracked `.nix` payload outside the module tree would need the
  payload check extended for no gain. A Nix-built `configPath` is rejected
  as well: the builder's `lib.cleanSource` makes evaluation build it, which
  on the Mac would need an x86_64-linux build (evaluated 2026-09-19).
- **The file and the channel are removed by a documented step,** once on
  the imported distribution and once after every future import; nothing an
  activation does removes them. On the imported distribution it runs before
  the first switch that turns the channel off, while `nix-channel` still
  exists.

## Increments

| Increment | Scope | Content |
| --- | --- | --- |
| A1 recipes | unixlike | `nixos-eval`, `nixos-test`, `nixos-switch`, `nixos-rollback`, `nixos-generations`; the rebuilding ones run `sudo nixos-rebuild <verb> --flake "path:./unixlike#$target"`. Every one but `nixos-eval` refuses unless `/etc/NIXOS` exists and `hostname` equals `_nixos-target`. `home-switch` refuses on NixOS. |
| A2 no channel | unixlike | `nix.channel.enable = false`, with an invariant registered in this increment and a `flake-test` fixture in both directions. |
| A3 procedure | repository | `CONTRIBUTING.md` § Update the registered NixOS-WSL distribution: clone inside the distribution; `git pull`; the cleanup step before the first switch; `just nixos-test` then `just nixos-switch`; `wsl --terminate NixOS` from Windows after a `/etc/wsl.conf` change; rollback within the collection window; re-import as recovery only, what it loses (`/home`, the account password, `authorized_keys`), and the cleanup step after it. The import section links to it. `tool/doctor.sh` names `just nixos-switch` and stops saying a home can switch on NixOS. |
| A4 records | unixlike | The Home Manager paragraph in the system-layer decision; `docs/status/unixlike.md`. |
| evidence | — | recorded in the report, starting with a baseline taken before A2 reaches the host. |

`home-manager.backupFileExtension` (a newly managed file colliding with an
unmanaged one fails the system switch) is a separate single change, not part
of this spec.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | `nixosConfigurations.<host>` evaluates and builds with the channel off; `nix.nixPath` is `nixpkgs=flake:nixpkgs` alone; the standalone home and the Darwin toplevel derivations are unchanged. | evaluation, build |
| AC2 | The rendered tarball builder registers no channel. | evaluation |
| AC3 | `flake-test` refuses the configuration with the channel on and accepts it with the channel off. | evaluation |
| AC4 | Each recipe but `nixos-eval` refuses on the Ubuntu distribution and names why; `nixos-eval` prints the toplevel derivation there; `home-switch` refuses on NixOS. | native runtime |
| AC5 | Baseline on the NixOS distribution before the change: `sudo nixos-rebuild dry-build` without `--flake` fails, and its message is recorded. | native runtime |
| AC6 | On the NixOS distribution, after the cleanup step: `just nixos-test` then `just nixos-switch` produce a new generation; `just nixos-generations` lists it; a rebuild without `--flake` fails before building anything; `/etc/nixos` and root's channel profile are absent. | activation, native runtime |
| AC7 | After that activation: `systemctl is-system-running` and `systemctl --user is-system-running` answer `running`; `binfmt_misc` is still read-only in the distribution and `WSLInterop` still present; `.exe` interop works; sudo still asks for a password. | native runtime |
| AC8 | `just nixos-rollback` returns to the previous configuration, and a following `just nixos-switch` activates the current one again as a further generation. | activation |
| AC9 | `CONTRIBUTING.md`, `tool/doctor.sh`, the system-layer decision and `docs/status/unixlike.md` state the procedure, the rejected split and the cleanup step. | review |

AC5 to AC8 run on the maintainer's host at the maintainer's request; `sudo`
needs the account password, so the maintainer runs them.

## Out of scope

- The host inventory and a second NixOS output; `_nixos-target`'s
  one-output assumption is replaced there (roadmap order 4).
- WSLg (deferred on the roadmap).
- `.wslconfig` and any Windows-side state.
