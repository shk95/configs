# The NixOS-WSL system layer declares only what Home Manager cannot

date: 2026-09-06
scope: unixlike
status: accepted
issue: #190
issue: #191
issue: #195
reopen-when: the NixOS-WSL host gains a display, or a second NixOS host composes `modules.nixos.wsl`.

`modules/wsl.nix` was written as an experiment: a system layer kept almost
empty, so that whether one earned its place could be answered by what had to
move in rather than by what was assumed. The test it set is kept as the rule.
A declaration belongs to `modules.nixos.wsl` only when standalone Home
Manager on the Ubuntu flavour genuinely could not make it. Everything else
stays in the Home Manager classes the NixOS flavour composes beside the
system layer, because a package or a file moved into the system layer is not
shared with the standalone flavour, it is removed from it: that flavour has
no `environment.systemPackages` at all
(`docs/decisions/home-manager-platform-classes.md`,
`INV unixlike/package-ownership`).

The test was applied on 2026-09-06 with the host imported and running, and
with the Darwin system layer beside it as the reference for what a system
layer of this repository already declares. It admitted eight things.

1. **The WSL integration.** `wsl.enable`, the account WSL logs into, and
   `/etc/wsl.conf`. The automount options are derived from the declared
   account: nixos-wsl mounts Windows drives for `uid=1000,gid=100` whatever
   the account's UID is, and on the imported host every file under `/mnt/c`
   listed an owner no account there had, while the account is 2000.
2. **The account's identity.** The UID, 2000, for the cgroup reason recorded
   in `modules/wsl.nix` and unchanged by this decision; the login shell,
   which the system layer selects (`modules/wsl-shell.nix`); and sudo
   asking for the account's password. The password is host state
   (`users.mutableUsers` at its default, `passwd` once), because a hash in
   tracked source — `hashedPassword`, or `initialHashedPassword` to cover a
   fresh import — would publish it. A fresh import therefore starts locked
   and is unlocked by `wsl -d NixOS -u root -- passwd`, which WSL grants
   without Linux authentication; `CONTRIBUTING.md § Import the NixOS-WSL
   distribution` is the procedure.
3. **The kernel-global protection.** `wsl-binfmt-protect`, unchanged, with
   its reasoning; and `wsl.interop.register = false` stated explicitly, since
   the two attempts recorded beside the service proved that registering our
   own entry adds nothing to the shared registry.
4. **The Nix daemon's settings.** `experimental-features`, the trusted
   account, and weekly collection, as `modules/darwin-nix.nix` declares for
   the Mac. The standalone flavour writes `~/.config/nix/nix.conf` from
   `homeManager.wslStandalone`, which the NixOS composition omits on
   purpose; under NixOS `/etc/nix/nix.conf` is generated from
   `nix.settings`, and nothing had declared it. `tool/doctor.sh unixlike` on
   the imported host reported `nix-command/flakes not enabled by default`
   against a host whose whole configuration is a flake. Declared in
   `modules/nix-conf.nix` beside its standalone twin, one feature in two
   classes.
5. **The host name.** Declared in the typed identity as `identity.wsl.hostName`
   and read by both the output name and `networking.hostName`
   (`modules/wsl-host.nix`, #191), as `identity.darwin.hostName` already
   was; `tool/checks/flake-test` proves the two agree. The value is the
   inventory's to change; the shape is the schema's to refuse
   (`INV unixlike/typed-identity`).
6. **The system environment.** `EDITOR` for what runs as root, as an
   absolute store path so the package stays Home Manager's
   (`modules/wsl-editor.nix`, the same declaration as
   `modules/darwin-editor.nix`), and the time zone
   (`modules/wsl-timezone.nix`; the imported host reported UTC).
7. **sshd** (`modules/wsl-sshd.nix`), key-only, on 2223: the port is the one
   Windows sees, because WSL2 relays every VM port to the Windows loopback
   and every distribution shares the VM's network namespace, and Windows
   holds 22 with its own OpenSSH server while Ubuntu holds 2222. Authorized
   keys stay host-owned, as `modules/ssh.nix` already keeps keys and
   `known_hosts`; a public key in tracked desired state is host identity by
   the statement of `INV repository/hygiene-machine-identity` even where the
   scan would not catch it.
8. **The state version**, already in `modules/state-version.nix`.

Two GUI options are set to their defaults explicitly rather than inherited:
`wsl.useWindowsDriver` and `wsl.startMenuLaunchers`, both `false`. The host
has no display, #21 owns WSLg, and `INV unixlike/desktop-not-wsl` keeps
graphical programs out of the WSL homes; a default that moved would
otherwise reach this host unseen. `hardware.graphics.enable` is forced on by
nixos-wsl itself and could be turned off only with `mkForce`, which
`INV unixlike/composition-in-one-place` forbids in a feature file; it is
accepted, because it installs no graphical program. `wsl.wslConf.interop`
stays at its defaults, interop on and the Windows `PATH` appended, because
the Windows domain's checks run from a Unix-like clone through Windows
executables; `wsl.docker-desktop` and `wsl.usbip` stay at nixos-wsl's
defaults, because neither is a headless concern.

Selecting the login shell reverses a sentence `modules/shell.nix` carried
since 2026-08-30, that the repository never chooses one. That sentence
described what the tooling could do at the time — standalone Home Manager
cannot select a shell, so `just switch-shell` ran `chsh` — and it was read as
policy; the intent has been one zsh across the Unix-like domain. Under NixOS
the account's shell and `/etc/shells` are both generated, so the system
layer is the only place the choice can be made. Declaring it also installs
the shell system-wide, which is load-bearing here rather than incidental:
nixos-wsl substitutes its own wrapper for the passwd shell, and that wrapper
waits for the activation script to finish before exec'ing the shell out of
the system profile. The choice is made without
`programs.zsh.enable`: the nixpkgs zsh sources `/etc/set-environment` from
its own compiled global `zshenv` and pam_env gives a login its `PATH`, both
observed on the imported host, so the global `/etc/zshrc` and second
`compinit` that option adds are not needed. NixOS guards against exactly
this combination, on the premise that the shell would lack the Nix
directories in its `PATH`; the premise does not hold here, and the guard's
own exit, `ignoreShellProgramCheck`, is declared with that observation
beside it. `modules/darwin-shell.nix` takes the `programs.zsh` route
because nix-darwin's environment is loaded from `/etc/zshrc`. The recipe
now serves the standalone home and Darwin, each with its own target, and
refuses NixOS. The sentence itself leaves `modules/shell.nix` as tracked
text that is false the moment the system layer selects a shell — the
exemption `CONTRIBUTING.md` names for a deletion that does not wait in
`docs/candidates/` — and this record is where the reversal is written down.
Making the Darwin layer select the shell too needs `users.knownUsers` and
is a later change.

Refused by the test: moving interactive packages or fonts into the system
layer (Home Manager declares them, `useUserPackages` folds them into the
system generation, and the standalone flavour keeps them); declaring the
authorized keys or a password hash; and `programs.zsh.enable`, above. The
coding agents are not a system-layer question at all: `modules/agents.nix`
is a Home Manager class the composition file gives to the NixOS-WSL home
and to no other, the mechanism that keeps `homeManager.desktop` out of the
WSL homes used the other way round (#195;
`docs/decisions/home-manager-platform-classes.md` records the new kind of
class, `docs/decisions/package-ownership-by-generating-module.md` what it
means for the shared list).

What it costs. The NixOS host is now read in seven files rather than one,
each holding one feature across the classes that need it. The automount
change alters the Linux-side owner of every file under `/mnt/c` on the next
activation; the shell, the time zone, sudo and sshd change on the same
activation. A fresh import needs two host-owned steps before it is usable,
the password and the authorized keys, and the procedure carries them.
Weekly collection with `--delete-older-than 14d` makes two weeks the
rollback window.
