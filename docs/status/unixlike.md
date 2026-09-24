# Current state: Unix-like

This file states what is observably true of the Unix-like domain today: hosts and
classes in use, schema and version facts, and open conditions. Every decision
is recorded under `docs/policy/decisions/`; the model those decisions implement
is `docs/policy/architecture.md`. The other scopes' state is in the files
beside this one.

The physical module tree now groups concerns under `flake`, `machines`,
`platforms`, `foundation`, `desktop`, and `programs`. These directories aid
navigation; each module still declares its own class, and
`unixlike/modules/flake/configurations.nix` alone selects host classes.

The flake now exports typed `lib.mkNixos`, `lib.mkDarwin`, and `lib.mkHome`
constructors for external consumers. Their host, account, Git and profile
values are checked before composition; host-owned system and home modules
have explicit extension points. All seven current outputs still come from the
provider inventory through those constructors during migration. An external
consumer fixture passes without importing provider-internal files, and the
seven toplevel derivation paths equal the pre-API `dev` tree. The public
`configs-host-template` now evaluates a synthetic output against the pinned
provider merge; its setup documents host-owned SOPS + age delivery. The one
private `configs-hosts` repository declares all seven current outputs with
independent flakes and locks. Their derivation paths match the pre-API tree;
the Darwin, OrbStack and UTM consumers built natively. Other installed Linux and
WSL consumers still need native builds, and each consumer needs runtime
evidence, so the provider inventory and outputs
remain in place
(`docs/policy/decisions/unixlike/provider-constructors-own-composition.md`).

Unix-like Home Manager hosts are standalone Ubuntu WSL, NixOS-WSL, and
nix-darwin, each importing `homeManager.shared`. `homeManager.wsl`,
`homeManager.wslStandalone`, `homeManager.desktop`, and `homeManager.darwin`
are the platform classes layered on top
(`docs/policy/decisions/unixlike/home-manager-platform-classes.md`).
NixOS host identity and profile choice are separate typed options. The
machine-kind rows provide required classes and offered profiles; each host
explicitly selects profiles it uses. `nixos` selects the `agents` profile,
while the VM guests and desktop retain their required graphical classes
(`docs/policy/decisions/unixlike/hosts-select-offered-machine-profiles.md`).
The seven existing output derivations are unchanged by this selection refactor;
a matching Linux host has not yet supplied a new native build for it.

SDKMAN is adopted but not owned
(`docs/policy/decisions/unixlike/sdkman-adopted-not-owned.md`). Its hook is the last
thing the generated zsh initialisation runs: since 2026-09-04 it sits after
Home Manager's own late pieces (starship, direnv, syntax highlighting),
where before it ran inside the repository's default-order block ahead of
them, and an assertion refuses a PATH assignment placed later.

Three other generated things changed on 2026-09-04 and reach a home on its
next activation: `~/.config/zellij/config.kdl` is Home Manager's rendering
of the asset (a blank line and an `// extraConfig` marker, then the asset)
rather than a link to it; every home carries Pester 5.7.1 under
`~/.local/share/powershell/Modules`, fetched from the PowerShell Gallery at
build time, so `pre-push` can run the Windows suite from a Unix-like clone;
and every generation's hash moved once, because the fragments a class
collects are now imported in the order of their defining files rather than
the directory walk (`INV unixlike/import-order-independence`).
`unixlike/flake.lock` is unchanged.

Since 2026-09-05 that rendering is the asset alone for every class: the
keymap, the `theme_dark`/`theme_light` pair, and a static
`theme "modus-operandi"` no class overrides. Windows Terminal 1.23 was probed
on 2026-09-05 and does not answer the colour-scheme query the pair depends
on, and every terminal this repository declares for a composed home is light
(`docs/policy/decisions/unixlike/composed-homes-render-in-declared-terminals.md`).

Also since 2026-09-05, Darwin's zellij carries upstream PR
zellij-org/zellij#5500, which attaches combining marks instead of dropping
them, so a decomposed Hangul syllable is expected to survive a pane; without it
only the leading jamo arrives, which was reproduced on Linux against the pinned
unpatched build. The patch is an overlay in
`unixlike/modules/programs/zellij/module.nix`, applies with no fuzz to whatever zellij
the lock brings in, and yields nothing on Linux, where every toplevel
derivation path is unchanged; since 2026-09-14 three flake checks built on every
system refuse a lock whose zellij the patch no longer applies to. The measure is registered as temporary
in `docs/provisional/unixlike/zellij-combining-marks.md`. Evaluation and the two
fixed-output hashes are Linux evidence. On 2026-09-06 the Mac built and
activated it twice. Generation 34 showed the jamo still dropped, because the
pull request attaches general-category Mark code points and a syllable's medial
vowel and final consonant are letters that `unicode-width` gives zero width;
the overlay then gained a `postPatch` that accepts those jamo ranges and a
Hangul grid test, and generation 35 rendered a decomposed syllable whole in a
real session, with the build's check now running the combining-mark tests in
`zellij-server`. The pull request's author folded that addition into the branch
the same day, with a fix to the readback paths (`dump-screen`, copy, serialize)
found on the way; the overlay now pins the branch's commit range instead of its
first commit, and generation 36 runs it, with the client stream and
`dump-screen` agreeing on the whole syllable. The dated paragraphs in
`docs/policy/decisions/unixlike/zellij-patched-on-darwin-until-upstream.md` record the
readings.

WezTerm and Ghostty are the desktop terminals; Home Manager installs the
D2Coding Nerd Font package and configures `D2KodingLigature Nerd Font Mono`
for both. On Darwin, WezTerm also reads Home Manager's nested font directory
explicitly, and Home Manager state version 25.11 uses
`targets.darwin.copyApps`, so the WezTerm bundle sits under `~/Applications/
Home Manager Apps` as a Spotlight-compatible copy rather than a Nix-store
symlink. Alacritty is fully inactive: there is no Alacritty package, Home
Manager module, or generated configuration. A future adoption should add its
package, configuration, and Dock ownership together.

The Linux graphical base is defined and composed into the physical desktop and
the two ordinary VM guests.
`nixos.graphical` collects Niri, greetd/tuigreet, PipeWire/WirePlumber,
portals, polkit, GNOME Keyring, dconf, graphics and removable-media services;
`homeManager.linuxGraphical` collects Noctalia, Hypridle, XWayland Satellite,
Fcitx5 Hangul, XDG/GTK integration and the selected Wayland applications.
The existing `homeManager.desktop` terminal and font ownership is unchanged.
An x86_64 NixOS VM check composes the real classes and validates their
generated configuration without a physical display. On 2026-09-23 UTM built
and activated the graphical output natively. Its display card was changed to
`virtio-gpu-gl-pci`; Niri, Noctalia, both terminals, pointer, Korean input,
audio and network were observed on screen or confirmed by the maintainer.
The candidate survived reboot and a rollback to the prior headless generation,
then was restored. Early immediate re-switch attempts failed Home Manager at
dconf and later at an inherited stale X display. The UTM-only Home Manager
guards passed a repeated headless-to-graphical test and an orderly reboot.
The UTM Ghostty software OpenGL choice is recorded in
`docs/policy/decisions/unixlike/utm-ghostty-uses-software-gl.md`, and the
detailed evidence remains in `docs/work/unixlike/graphical-vm-guests/report.md`.
VMware also runs the graphical state after native build, test activation,
switch and reboot on 2026-09-23. Enabling VMware's 3D acceleration resolved
the initial black screen. The maintainer confirmed both terminals, Korean
input, panel pointer interaction and audible output. Immediate restoration
from a headless rollback exposed the same live-user-bus failure as UTM;
the VMware module now carries its own activation guards, and a repeat
rollback/restoration plus reboot passed with no failed system units. This
VMware fix is recorded in `1fe78ff`; the maintainer confirmed Niri and Ghostty
after the final reboot, as recorded in
`docs/work/unixlike/graphical-vm-guests/report.md`.

`btop.conf` is now generated by `unixlike/modules/programs/btop.nix` with a
`modus-operandi` theme and takes effect on each host's next activation; on the
WSL host the existing hand-written `~/.config/btop/btop.conf` must be moved
aside first.

Karabiner's configuration is desired state and the application is not:
`unixlike/modules/programs/karabiner/karabiner.json` and
`unixlike/modules/programs/karabiner/symbolic-hotkeys.json` declare the members this
repository owns, `unixlike/modules/programs/karabiner/module.nix` delivers them from
`homeManager.darwin` through an activation script rather than a link, and
`unixlike/modules/programs/karabiner/tool` compares and reads them back through one
projection onto those members (`INV unixlike/host-written-payload-projected`,
`just karabiner-check` and `just karabiner-capture`). Symbolic hotkeys other
than 60 and 61 are unmanaged; the host dictionary holds dozens of entries and
each declared one is written on its own.

`unixlike/modules/programs/karabiner/karabiner.json` was a reconstruction of the host
file from the description in #177 until 2026-09-06, when the Mac's own `check`
reported drift, `just karabiner-capture` wrote the host's values back (#183),
and the check exited 0 with `project` reproducing both payloads byte for byte.
Generation 34 the same day delivered the module without rewriting the file,
because the host already matched, so Karabiner's last load of the file predates
the activation. The `INV unixlike/generated-config-key-in-schema` item is
observed as Karabiner running a file whose declared members are the payload's
bytes; a load after an activation that rewrites the file is not yet observed
(`docs/policy/decisions/unixlike/karabiner-desired-state-by-projection.md`).

The NixOS-WSL host is headless and its system layer is a decided boundary since
2026-09-06 rather than the experiment `unixlike/modules/platforms/wsl.nix` described:
`modules.nixos.wsl` declares the WSL integration, the account's UID, login
shell and sudo password requirement, the binfmt protection, the system
`EDITOR` and time zone, and key-only sshd on 2223 — and nothing a standalone
home can declare
(`docs/policy/decisions/unixlike/nixos-wsl-system-layer-ownership.md`). The
host is the entry `nixos` of `identity.nixosHosts`, the typed inventory of
NixOS hosts: every `nixosConfigurations` output is generated from an entry
and named after it, `modules.nixos.shared` gives the host that name and the
entry's state version, and only a combination of system, kind and hypervisor
that a host lane names evaluates (`INV unixlike/nixos-host-inventory`).
`unixlike/tool/checks/flake-test` proves each host answers to its entry's
name (#191). `aarch64-linux` is an evaluated system and is not built here
(`docs/work/unixlike/nixos-host-inventory/report.md`, done).
`utm` (aarch64, UTM on the Mac) now boots the graphical generation. Its desired state is composed from `nixos.utm`
(`unixlike/modules/machines/utm.nix`), the labelled UEFI/ext4
`nixos.installExt4` class, and the `nixos.headless`
class — the entry's account without a tracked password, key-only sshd on 22
and a firewall that opens that port alone (`INV unixlike/headless-key-only`)
— and the shared Niri and Noctalia graphical system and home classes. The
x86_64 flake check also boots the shared headless class and
reaches it from a separate network namespace: the declared account accepts a
disposable key, password and root logins fail, sudo asks for a password, and
the firewall refuses a listening port other than ssh. The guest had been
installed from the graphical
installer as NixOS 25.11 and was adopted in place on 2026-09-20: its file
systems relabelled, a first switch that named the output, the installer's
channel and configuration removed; its state version is 25.11 and its swap
partition is unused. Each lane was observed separately, inside the guest at
629076e unless said otherwise: evaluation on the aarch64 Darwin host and in
the merge gate; build, the `utm` toplevel; native runtime, the host answers
to `utm`, the account logs in over ssh with a key and is refused with a
password, sudo asks for the password, flakes run and no channel exists;
activation, `just nixos-test` and `just nixos-switch` activated generations
built from this flake and `just nixos-rollback` returned to the one before
(`docs/work/unixlike/utm-headless-guest/report.md`). The graphical state was
built natively, test-activated, switched into the boot profile, rebooted,
rolled back to the prior headless generation and restored on 2026-09-23.
After the latest reboot, SSH, greetd and Home Manager are active, no system
unit is failed, and the maintainer confirmed Niri and a Ghostty shell after
login. The resolved re-switch failures
and complete evidence are recorded in
`docs/work/unixlike/graphical-vm-guests/report.md`.
The UTM-only Niri key-repeat delay is now 150 ms; the running and boot
generations retain it after an orderly guest reboot.
The shared NixOS time-zone class now declares `Asia/Seoul` for all five NixOS
outputs. Evaluation confirms the zone on each output; the UTM guest has also
test-activated and switched a native build, while the other hosts have not
been reactivated for this change.

`orbstack` (aarch64, an isolated OrbStack machine on the Mac, created on
2026-09-20 as a sandbox) is composed from `nixos.orbstack`
(`unixlike/modules/machines/orbstack.nix`), which declares by hand what OrbStack
needs from a guest — the account OrbStack enters as, its network and
resolver, no sshd — imports nothing OrbStack generates, registers no binfmt
emulation on the kernel the machines share
(`INV unixlike/orbstack-shared-kernel`), and takes the shared home alone. The
machine was switched to the flake on 2026-09-20, then deleted and created
again isolated from OrbStack's image to read the procedure end to end, and
each lane was observed separately, inside the machine that exists now at
d616c51 unless said otherwise: evaluation, at 9198817, on the aarch64 Darwin
host and in the merge gate; build, the `orbstack` toplevel; native runtime,
after a restart from the Mac the host answers to `orbstack`, an OrbStack
session enters as the account in zsh, sudo works, no channel exists, nothing
of the Mac is mounted and no ssh agent is forwarded, OrbStack's mask of
`systemd-binfmt.service` is in place with no `binfmt_misc` mounted, and the
system is `running` with no failed unit — names resolving and flakes running
were read in the first machine, at e562c49; activation, a first switch that
named the output, which exits non-zero on the message bus's reload when the
image's release differs from the flake's and is settled by a restart, then
`just nixos-test`, `just nixos-switch` and `just nixos-rollback` between
generations of this flake, each exiting 0. The first generation, at 98b1a23,
ran degraded on `sys-kernel-debug.mount`, which cannot be mounted in the
machine and the class now suppresses
(`docs/work/unixlike/orbstack-sandbox/report.md`). `vm` (x86_64, a guest of
VMware Workstation on a Linux or a Windows host,
`docs/policy/decisions/unixlike/x86-64-guest-runs-on-vmware-workstation.md`)
is composed from `nixos.vmware`
(`unixlike/modules/machines/vmware.nix`), the labelled UEFI/ext4
`nixos.installExt4` class, the `nixos.headless` class and the
shared Niri and Noctalia graphical system and home classes. Its earlier
headless evidence is evaluation and a build of its toplevel on
the x86_64 WSL host at c73b5dd. On 2026-09-21 the maintainer installed it from
the 26.05 minimal medium in UEFI mode, using the account declared in the
inventory and state version 26.05. The maintainer reported a successful
installation and disk boot: native runtime answers `vm` and `vmware`, runs
NixOS `26.11.20260916.b1b8759`, asks for a sudo password and lists no failed
system unit. The host operating system is Windows; the installation source
is abc5dae with a local inventory edit selecting the confirmed account and
state version. The VMware tools and sshd services are active, and a
password-only SSH attempt was refused while a public-key-only batch-mode
login succeeded. Copied ISO channel profile links were removed and their
absence verified. The generation recipe lists generation 1 as current, and
flake metadata resolves the locked inputs. Native-runtime AC7 is verified.
Activation: from the installation clone copied into the managed account's
home, `just nixos-test` and `just nixos-switch` both succeed and report
`5g17hsxn…-nixos-system-vm`; the running system and boot profile resolve to
that path, with no failed system unit. Both reuse generation 1 because the
configuration is unchanged. For rollback verification only, the same flake's
host extended with the `rollback-check` system tag built `apbk2rh5…` and was
activated as generation 2 with `--store-path` and `--no-reexec`; the latter
avoids a re-exec that otherwise tries the absent `nixos-config` before
activation. `just nixos-rollback` returned from 2 to 1, both system paths
equalled the saved original, and no unit was failed. Generation 2 remains
non-current. Test, switch and rollback are verified on this Windows-hosted
guest. Its desired state now also composes the shared Niri and Noctalia
graphical profile and full open-vm-tools integration. On 2026-09-23, the
40 GiB virtual disk's root partition and ext4 file system were expanded to
39 GiB, preserving the existing data and leaving 25 GiB free after the
graphical build. The Windows-hosted guest passed graphical runtime and
test/switch/reboot observations; an initial immediate restoration failure
was repaired with VMware-local Home Manager activation guards. The fixed
candidate passed native build, test, rollback/restoration and reboot, with
both system paths at that candidate and no failed system units. Source is
`1056a35` plus the recovery fix committed as `1fe78ff`. Linux-host runtime remains
unverified. Detailed evidence and final console confirmation are recorded in
`docs/work/unixlike/graphical-vm-guests/report.md`
(`docs/policy/decisions/unixlike/vm-guests-share-the-graphical-profile.md`).
The headless work report is done
(`docs/work/unixlike/vmware-headless-guest/report.md`). `desktop` (x86_64) is
not installed. Its desired state composes the encrypted
`nixos.installLuksBtrfs` class, the headless account/SSH recovery class and the
Niri/Noctalia graphical classes over a physical AMD APU base. It
declares UEFI systemd-boot, manual unlock of a labelled LUKS2 container, Btrfs
`@`, `@home` and `@nix` subvolumes, zram, AMDGPU with firmware and microcode,
Mesa and NetworkManager
(`docs/policy/decisions/unixlike/amd-apu-desktop-uses-labelled-luks-btrfs.md`).
The tracked source contains no generated hardware file, disk UUID or monitor
value. Its account and state version remain provisional until the physical
installer confirms or corrects them. Evaluation and x86_64 build are the only
available evidence; hardware runtime and activation remain pending in
`docs/work/unixlike/amd-apu-desktop/report.md`.

The three ordinary booting hosts now expose disko installation layouts. Their
tracked target is the unusable
`/dev/disk/by-id/INSTALL_TARGET_REQUIRED`; `just nixos-install-plan` writes a
new wrapper flake only after the maintainer supplies one installable inventory
host and one persistent by-id path. `just nixos-install-vm-test vm` formats
only disposable QEMU disks, installs the actual VMware-shaped output and boots
it; the test may use KVM or TCG and does not connect to an installed host.
Physical formatting and installation remain pending, as do all deploy-rs
nodes and remote activations
(`docs/work/unixlike/installation-and-deployment/report.md`). The
Nix daemon settings and the no-channel rule are in `modules.nixos.shared`
and reach every NixOS host, the registered distribution included.
GUI options are set off explicitly. Neither WSL output supports Linux GUI
applications or WSLg, and no WSL GUI work is planned. A future need first
requires revising the Unix-like architecture and `INV unixlike/desktop-not-wsl`.
The coding agents (`claude-code`, `codex`)
are a Home Manager class, `homeManager.agents`, composed into this home only
(#195). The distribution was imported on 2026-09-06 from the toplevel the
Ubuntu clone built at `dev` 92c5986, and generation 2 the same day is the first
to carry these declarations. It was read back on that host: `tool/doctor.sh
unixlike` reports ready, the account logs into zsh with a complete `PATH`, sudo
asks for a password, the zone is `Asia/Seoul`, sshd answers on 2223 and refuses
anything but a key, and both agents are on the per-user profile. The
kernel-global resources came through the activation untouched — the binfmt
registry is still read-only here, `WSLInterop` still carries the registration
Ubuntu made before this distribution booted, `.exe` still runs, and both
managers report `running`. On 2026-09-08 the distribution was terminated while
Ubuntu26.04 kept the WSL VM alive: Ubuntu's binfmt entries, their timestamps
and `.exe` interop survived unchanged. Restarting NixOS made the generated
`/etc/wsl.conf` effective, so `/mnt/c` now has the declared `uid=2000,gid=100`;
both managers returned to `running` with no failed units. The milestone's
evidence issue (#192) carries the readings.

Since 2026-09-19 the distribution is updated in place
(`docs/work/unixlike/nixos-wsl-in-place-update/report.md`, done). The
recipes `nixos-test`, `nixos-switch`, `nixos-rollback` and
`nixos-generations` act on the output named after the NixOS host they run on
and refuse where there is none; `nixos-eval`, `nixos-build` and
`nixos-tarball` run anywhere and take the host as an argument, refusing with
the list of exported names when it is missing or unknown; and `home-switch`
refuses on NixOS. `unixlike/tool/checks/test` builds a NixOS output only on
the host it is named after
(`docs/policy/decisions/unixlike/nixos-hosts-declared-in-typed-inventory.md`). Channels are off in the
configuration (`INV unixlike/nixos-no-channel`), so the search path names the
flake's nixpkgs alone and an archive built from here registers no channel.
`CONTRIBUTING.md`, "Update the registered NixOS-WSL distribution", is the
procedure.

The host took that path the same day. A rebuild without a flake failed on
the search path before and after, as predicted; the cleanup removed
`/etc/nixos` and the channel the import had added and never updated;
`just nixos-test` and `just nixos-switch` activated generation 4, whose
toplevel is the one the Ubuntu distribution had built, and both managers
report `running`. Generation 3 had been activated earlier that day from the
tree before channels were turned off. `just nixos-rollback` went back to
generation 3 and `just nixos-switch` returned to generation 4, the same
generation rather than a fifth, because Nix reuses the one that already holds
the path. The binfmt_misc mount is read-only in this distribution and a
Windows executable runs from a fresh shell; one long-lived shell session
failed to run one earlier the same evening, unexplained and not seen since.

## Open conditions

- The Darwin zellij overlay (`PROV unixlike/zellij-combining-marks`) stands
  until a nixpkgs zellij whose source already contains
  zellij-org/zellij#5500 reaches `unixlike/flake.lock`; review by 2026-12-04
  (`docs/provisional/unixlike/zellij-combining-marks.md`).
