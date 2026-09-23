# Report: adopt Niri and Noctalia on the VM guests

kind: report
spec: docs/work/unixlike/graphical-vm-guests/spec.md
status: done

Automatic implementation commit `5b20df4` composes and checks both guest
outputs. The repository-scope procedure is reviewed. Both installed guests
have supplied their native evidence, and the VMware recovery fix `1fe78ff`
passed the required CI gate. The report is complete on 2026-09-23.
VMware has supplied native build, graphical runtime,
switch, reboot and a repaired rollback/restoration test, as recorded below.
At the maintainer's
request, UTM native build and test activation began on 2026-09-23 before the
VMware increment. The UTM graphical candidate is now the boot default after
switch, reboot, rollback and restoration. The initially failed immediate
re-switch path was repaired and passed a repeat test; AC8 is verified.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | `unixlike/modules/flake/configurations.nix` keeps `nixos.utm` or `nixos.vmware` and `nixos.headless` in each guest row and adds `nixos.graphical`; both homes compose the shared, desktop and Linux graphical classes. `unixlike/tool/checks/composition-test` confirms that all 62 feature files name no host and force no value. |
| AC2 | verified | Evaluation and native build at `5b20df4`: the VMware assertion and fixture require full `open-vm-tools`, its vmblock mount, Niri, greetd, PipeWire, key-only SSH and port 22 alone. Direct evaluation returned `headless=false`, package `open-vm-tools`, `vmblock=true`, `niri=true`, `ssh=true` and ports `[22]`. The locked x86_64 toplevel built as `/nix/store/8y0l58zss29qirmg4p8pmsblm0lr0dk1-nixos-system-vm-26.11.20260916.b1b8759`; `nix path-info -Sh` reports a 10.4 GiB closure. |
| AC3 | verified | `nix flake check --no-build path:./unixlike` evaluates the UTM output for aarch64, and its host assertion plus positive and negative fixture require the QEMU guest service, both serial-console parameters, the graphical services, key-only SSH and port 22 alone. Its evaluated toplevel is `/nix/store/bdf9k51kl3pn063s90nw67xcsjd8r1bi-nixos-system-utm-26.11.20260916.b1b8759.drv`; no aarch64 build is claimed. |
| AC4 | verified | Native x86_64 runtime at `5b20df4`: `nix build --no-link` succeeds for `/nix/store/my7fmjhcvm132h1wwg8jhg3mrlnql5m3-vm-test-run-configs-graphical-runtime` and `/nix/store/l9iik30kxxajmvg60xhkb8pppmh3ap9x-vm-test-run-configs-headless-runtime`. The first boots the actual shared graphical classes and validates their services, files and programs; the second separately boots and exercises the account, SSH and firewall recovery contract. |
| AC5 | verified | `unixlike/tool/checks/flake-test` requires all `desktop` and `vm` hosts to enable Niri, greetd and PipeWire and to contain the graphical home markers, while both WSL homes and OrbStack contain none. Review found no change to the physical desktop row. |
| AC6 | verified | Review of `CONTRIBUTING.md` at `e346c36`, merged through #342: “Activate the graphical profile on the VM guests” records capacity before and after realising the candidate, compares closures, and refuses garbage collection as a way to make the activation fit. It orders VMware before UTM and test before switch, requires a second SSH session and hypervisor console, names Niri/Noctalia, input, audio, network and hypervisor observations, and gives test failure, systemd-boot and previous-generation recovery paths. Every activation command is explicitly the maintainer's to authorize and run. |
| AC7 | verified | On 2026-09-23, VMware passed native build, graphical login, both terminals, Korean input, pointer, audio, network, switch and reboot. An immediate headless-to-graphical restoration failure was repaired; the fixed candidate passed test activation, rollback/restoration and reboot. The maintainer confirmed Niri and Ghostty again after the final reboot. Details follow. |
| AC8 | verified | UTM built the final aarch64 candidate natively, passed on-screen Niri/Noctalia, Ghostty/WezTerm, Korean input, pointer, sound and network observations, switched and rebooted it, and returned successfully from a headless test activation with the still-running user bus. The maintainer requested UTM before VMware; details follow. |
| AC9 | verified | Prior implementation passed run `35776083090` at `6a15e9e`. The VMware recovery source `1fe78ff` passed the Unix-like job and `Required checks` in [run 35859977954](https://github.com/shk95/configs/actions/runs/35859977954). PR #354 must also pass the same gate on its final documentation head before merging; branch protection enforces that final gate. |

## VMware installed-guest evidence, 2026-09-23

- **Source and capacity.** The existing installation checkout retains its
  local inventory edit. An archive of reviewed source `1056a35` was built in
  `/tmp/configs-vmware-1056a35`, without changing that checkout. The maintainer
  enlarged the virtual disk from 20 to 40 GiB. After saving the partition
  table on the guest, the agent extended only the final root partition,
  preserving its start sector, and grew the mounted ext4 file system.
  `sfdisk --verify` reported no errors; root then measured 39 GiB with
  31 GiB free. No partition was formatted and no Nix garbage collection ran.
- **Native build.** The guest built
  `/nix/store/1bkavsb96m8brk7kh8qxvjlx4z4ihhp4-nixos-system-vm-26.11.20260916.b1b8759`.
  `nix path-info -Sh` measured the candidate at 10.4 GiB and the existing
  headless generation at 5.2 GiB. After the build, root retained 25 GiB free
  and the EFI file system 980 MiB free.
- **Test activation.** With the maintainer's authorization and a second SSH
  session retained, `just nixos-test` exited successfully. The running system
  moved to the candidate while the boot profile remained
  `/nix/store/5g17hsxndjl9gdcilnm775a0fyz4daw2-nixos-system-vm-26.11.20260916.b1b8759`.
  The old headless target did not start greetd automatically; starting
  `graphical.target` brought up greetd. Fresh key-authenticated SSH worked,
  sshd, greetd, Home Manager, VMware tools and the vmblock mount were active,
  and neither the system nor user manager listed a failed unit. Niri and
  Noctalia validated the installed configuration; an HTTPS request to GitHub
  returned 200. These checks do not yet prove a graphical login or rendering,
  physical input, audible output or host clipboard integration.
- **First console attempt.** The maintainer could log in through greetd but
  observed a black screen. Niri and Noctalia remained running with no failed
  user unit, but Niri logged `VMware: No 3D enabled`, rejected the software
  EGL renderer and reported `no allocator available for device`. Its output
  query returned no display. The kernel reported the legacy shader model.
  Thus a successful test activation did not establish graphical runtime.
  VMware display acceleration must be checked on the host before repeating
  the graphical test; the graphical candidate has not become the boot default.
- **3D acceleration retry.** After the maintainer enabled VMware display
  acceleration and booted the guest again, vmwgfx reported the `3D`
  capability and shader model `SM_5_1X`, replacing the earlier legacy model.
  The same candidate passed `just nixos-test` again and `graphical.target`
  started successfully. The maintainer confirmed Niri/Noctalia rendering and
  Ghostty through Mod+Return. Niri initialized its primary renderer and
  registered `Virtual-1` at 1718x928 and 60 Hz. Fcitx5, PipeWire,
  WirePlumber and the VMware user integration process were running; system
  and user managers had no failed units. An HTTPS request returned 200.
  A two-second 440 Hz tone played successfully through PipeWire. The
  maintainer confirmed audible output, Korean input, WezTerm through
  Mod+Shift+Return and pointer interaction with the Noctalia panel.
- **Switch and reboot.** `just nixos-switch` succeeded and registered the
  graphical candidate as generation 3, with both system paths equal and no
  failed system unit. An orderly `systemctl reboot` changed the boot ID.
  A fresh SSH connection found both
  system paths still at the graphical candidate, with sshd, greetd, Home
  Manager and VMware tools active and zero failed system units. The maintainer
  confirmed the graphical session, Ghostty and Korean input after reboot.
- **Rollback defect and repair.** `just nixos-rollback` returned both system
  paths to generation 2, the earlier `rollback-check` headless generation
  `/nix/store/apbk2rh5l15r03cp0y0y594xl2a0izc8-nixos-system-vm-rollback-check-26.11.20260916.b1b8759`.
  SSH survived and no unit failed. Immediate re-switch to the first graphical
  candidate exited 4: Home Manager failed at `dconfSettings` with
  `org.freedesktop.DBus.Error.ServiceUnknown`. This was a failed restoration,
  even though the system and boot profile had moved to the graphical candidate.
  The VMware module now refreshes the live user bus before dconf settings and
  clears an unreachable inherited X display before `onFilesChange`, using the
  same guards already exercised on UTM. No other host's configuration changed.
- **Repeated recovery test.** Source `1056a35` with the uncommitted VMware
  recovery fix (subsequently committed as `1fe78ff`) built natively as
  `/nix/store/jsrs1wx2672720vq15351287jl82vmag-nixos-system-vm-26.11.20260916.b1b8759`.
  `just nixos-test` succeeded and recovered Home Manager. Another
  `just nixos-rollback` returned to the headless generation while retaining
  the user bus, whose activatable names lacked dconf, and stale `DISPLAY=:0`.
  Immediate `just nixos-switch` then exited 0: Home Manager completed
  `reloadDconfServices`, `dconfSettings`, `discardStaleXDisplay` and
  `onFilesChange` on its first start. Both system paths named the fixed
  graphical candidate and no system unit failed. `nix flake check --no-build`
  passed on the guest; formatting and composition checks passed locally.
  An orderly reboot changed the boot ID again; both system paths still named the
  fixed candidate, and sshd, greetd, Home Manager and VMware tools were active
  with zero failed system units. Root retained 25 GiB free. The maintainer
  confirmed Niri and Ghostty after this final reboot; SSH also observed both
  processes and zero failed user units. SHA-256 comparison confirmed that
  the guest's VMware module matches the local edited source. Independent
  read-only verification also matched the complete tracked `unixlike/` and
  `Justfile` content between the local tree and guest, and re-evaluation
  returned the running candidate. Commit `1fe78ff` preserves that fix;
  its PR CI passed in run `35859977954`. The report's final documentation
  head remains subject to the same required gate before merge.

## UTM installed-guest evidence, 2026-09-23

- **Build and capacity.** The aarch64 guest started from headless generation
  `/nix/store/pmvi10q9m3h1wky11263jz59yzb0rhm6-nixos-system-utm-26.11.20260916.b1b8759`.
  Its clean `~/configs` checkout remained at `51be325`, so an archive of
  `origin/dev` at `7af620f` was built in `/tmp/configs-utm-7af620f`.
  The first graphical candidate was
  `/nix/store/p41h9r7ypgbcvqlyn8141dz9wfmbfbba-nixos-system-utm-26.11.20260916.b1b8759`.
  `nix path-info -Sh` measured 5.3 GiB for the old closure and 10.0 GiB for
  that candidate. Free root space was 38 GiB before and 33 GiB after the
  build; `/boot` had 866 MiB free.
- **Display diagnosis.** The first `just nixos-test` preserved the headless
  boot profile; SSH and greetd were active after `graphical.target` started,
  but UTM showed `Display output is not active`. A reboot returned to the old
  headless generation. With `virtio-ramfb`, the guest exposed simpledrm as
  fb0 and virtio GPU as fb1. A temporary `con2fbmap 1 1` made tty1 and
  `tuigreet` visible. Niri then logged `software EGL renderers are skipped`
  and `no allocator available for device` and displayed no desktop. An
  experimental `fbcon=map:1` candidate was built, but its boot parameter was
  never tested; the code was removed after the display hardware changed.
- **UTM display card.** With maintainer approval, the agent saved the original
  VM configuration at
  `~/Library/Application Support/UTM-config-backups/nixos-tutorial-config-pre-virgl-20260923.plist`,
  requested an orderly shutdown, and changed the card from `virtio-ramfb` to
  `virtio-gpu-gl-pci`. The first boot retained the headless generation, SSH,
  and zero failed units. The guest kernel reported `+virgl` and one
  `virtio_gpudrmfb` on fb0. A repeat `just nixos-test` of the original
  graphical candidate displayed Niri and Noctalia. Niri initialized a
  renderer and connected `Virtual-1` at 1280×800.
- **Graphical runtime.** Clicking Noctalia's system panel proved pointer
  input. The keyboard shortcut opened a rendered WezTerm shell. Niri,
  Noctalia, Fcitx5, PipeWire, WirePlumber and WezTerm ran with zero failed
  system or user units. `wpctl status` found an ALSA stereo sink and source,
  and `curl -I https://github.com` returned HTTP 200. The maintainer
  confirmed that a two-second 440 Hz PipeWire tone was audible and that
  `한글 테스트` appeared correctly in WezTerm through Fcitx5.
- **Ghostty on UTM.** Ghostty 1.3.1 displayed `No EGL configuration
  available` with both Wayland and X11 launches. With
  `LIBGL_ALWAYS_SOFTWARE=1`, it displayed a shell. A UTM-only wrapped
  Ghostty package then built natively as part of
  `/nix/store/0r8g78lrkyycgamd23jpipnak739k9h9-nixos-system-utm-26.11.20260916.b1b8759`.
  Its direct launch and default Niri shortcut both showed a shell after
  `just nixos-test`; VMware still evaluates to the unwrapped Ghostty package.
  The host-specific choice is recorded in
  `docs/policy/decisions/unixlike/utm-ghostty-uses-software-gl.md`.
- **Switch and reboot.** The maintainer ran `just nixos-switch` from
  `/tmp/configs-utm-ghostty-software`. Both `/run/current-system` and the
  boot profile pointed to the wrapped candidate, with SSH and greetd active
  and zero failed units. An orderly UTM restart booted the same candidate;
  SSH returned, `tuigreet` was visible, and the maintainer confirmed Niri,
  Ghostty, Korean text and audible sound after login. Firefox loaded an online
  page in the observed session.
- **Rollback and restoration.** `just nixos-rollback` moved both system
  paths to the prior headless generation, retained SSH and zero failed units,
  and stopped greetd as expected. Immediate `just nixos-switch` returned both
  system paths to the graphical candidate, but
  `home-manager-shk.service` failed twice at `dconfSettings` with
  `org.freedesktop.DBus.Error.ServiceUnknown` on the user bus. An orderly UTM
  restart recovered: Home Manager, SSH and greetd were active, zero system
  units failed, the graphical candidate remained both current and boot
  default, and `tuigreet` appeared. Later candidates addressed the immediate
  re-switch failure, as recorded below.
- **UTM keyboard repeat candidate.** After the restoration, the maintainer
  requested a shorter delay before a held key repeats. A 250 ms candidate was
  test-activated: the running system and Home Manager's Niri configuration
  showed `repeat-delay 250`, while the boot profile retained the previous
  graphical generation. The maintainer then requested 150 ms. The UTM-only
  setting now asks Niri for 150 ms without changing the repeat rate. A native
  aarch64 build produced
  `/nix/store/w69yv2sjmm9s2mj62b5xhk6hp63a1fjs-nixos-system-utm-26.11.20260916.b1b8759`;
  Niri validated the generated KDL, which contains `repeat-delay 150`.
  The maintainer test-activated this candidate and confirmed that the current
  keyboard response feels right. Read-only verification found the running
  system at this candidate, Home Manager's installed Niri file at
  `repeat-delay 150`, and SSH, greetd and Home Manager active with no failed
  system units. `just nixos-switch` then set both the running system and boot
  profile to this candidate with those services active. UTM's power-button
  shutdown request suspended the guest (`Power key pressed short`, then
  `suspend entry (s2idle)` in the previous boot journal), so the agent stopped
  the suspended VM and started it again. The new boot ID and on-screen Niri
  and Noctalia session, both system paths at the 150 ms candidate, installed
  `repeat-delay 150`, and active SSH, greetd and Home Manager prove a cold
  start. The maintainer then ran `sudo systemctl reboot` inside the guest.
  The previous boot journal reached `System Reboot` and shut down normally;
  the next boot ID differed from the previous one.
  Both system paths still point to the 150 ms candidate, Home Manager's Niri
  file still says `repeat-delay 150`, Niri and Noctalia appeared on screen,
  and SSH, greetd and Home Manager were active with no failed system units.
- **D-Bus service refresh candidate.** The earlier dconf failure happened
  when Home Manager returned from the headless generation while the user bus
  remained alive. Its activation script uses that bus when
  `DBUS_SESSION_BUS_ADDRESS` is present; `dbus-broker` supports
  `org.freedesktop.DBus.ReloadConfig` to refresh activatable services. The UTM
  home now calls it immediately before `dconfSettings` when a user bus exists.
  The call succeeded on the running graphical guest. A native aarch64 build
  produced
  `/nix/store/1w40wwrym52qhr1cfma2nhyvkwj5vpyf-nixos-system-utm-26.11.20260916.b1b8759`;
  inspection of its generated Home Manager activation script verified that
  order. The maintainer test-activated it successfully. A test activation of
  the previous headless generation left the user bus running but removed
  `ca.desrt.dconf` from its activatable names and `/etc/systemd/user/dconf.service`.
  On immediate return to the graphical candidate, dconf succeeded after the
  reload. Home Manager's first run then failed at `onFilesChange`: the old
  user-manager `DISPLAY=:0` pointed to a stopped Xwayland server, and its
  Xresources hook called `xrdb` there. A second automatic Home Manager start
  succeeded, but `nixos-rebuild test` exited 4. This is not a successful
  activation result.
- **Stale display guard and time zone candidate.** The UTM Home Manager
  activation now tests whether `xrdb` can reach the inherited display and
  clears `DISPLAY` before `onFilesChange` when it cannot. The generated script
  places this guard after the D-Bus refresh and before `onFilesChange`. The
  repository's shared NixOS time-zone class now sets `Asia/Seoul` for all five
  NixOS outputs; evaluation returned that zone for `desktop`, `nixos`,
  `orbstack`, `utm` and `vm`. The UTM guest built their combined candidate
  natively as
  `/nix/store/f5cim43xa6idrvjrlxzg9dyd0ig0jwyp-nixos-system-utm-26.11.20260916.b1b8759`.
  A second test activation of the earlier headless generation again left the
  user bus alive, removed dconf's activatable name, and retained stale
  `DISPLAY=:0`; SSH and the graphical boot profile survived. The maintainer's
  `just nixos-test` of this candidate returned `Done`. Home Manager completed
  `reloadDconfServices`, `dconfSettings`, `discardStaleXDisplay` and
  `onFilesChange` on its first start. SSH, greetd and Home Manager were active,
  no system unit failed, Niri ran, and the guest reported `Asia/Seoul` and
  `+0900`. The command's initial nix-index and zoxide messages came from
  starting a shell in the headless generation before activation. The
  maintainer then ran `just nixos-switch`; both the running system and boot
  profile pointed to this candidate, the zone and 150 ms delay remained,
  SSH, greetd and Home Manager were active, and no system unit failed. The
  maintainer ran `sudo systemctl reboot`; the prior journal reached `System
  Reboot`, the boot ID changed,
  both system paths still pointed to this candidate, and the zone and delay
  remained `Asia/Seoul` and 150 ms. SSH, greetd and Home Manager were active
  with no failed system units, and `tuigreet` appeared in the UTM display.
  After another orderly reboot, a new boot ID confirmed a fresh boot with
  the same system paths, zone, delay and active services. The maintainer
  logged in and confirmed
  Niri, a Mod+Return Ghostty shell and the 150 ms keyboard response; SSH
  observed both Niri and Ghostty processes.
