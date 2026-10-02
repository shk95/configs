# Report: build the shared Niri and Noctalia graphical base

kind: report
spec: docs/work/unixlike/niri-noctalia-graphical-base/spec.md
status: done

Source `2478711` defines the graphical classes without composing them into a
declared host. On the x86_64 Linux checkout, the exact source evaluates, builds
and completes its NixOS VM test as
`/nix/store/my7fmjhcvm132h1wwg8jhg3mrlnql5m3-vm-test-run-configs-graphical-runtime`.
No host was activated. Installed-host rendering, input, audio and activation
remain evidence for roadmap order 10.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Evaluation at `2478711`: `nix flake check --no-build path:./unixlike` evaluates every declared NixOS output and the new graphical VM check. `unixlike/tool/checks/flake-test` exits 0 after requiring Niri, greetd and PipeWire to remain disabled on every declared host and finding neither Noctalia nor XWayland Satellite in any declared home. `unixlike/tool/checks/composition-test` reports that all 61 feature files name no host and force no value; `unixlike/modules/flake/configurations.nix` is unchanged. |
| AC2 | verified | Evaluation and build at `2478711`: the graphical test composes the actual `nixos.graphical` class and evaluates Niri, greetd/tuigreet, PipeWire/WirePlumber, rtkit, portals, polkit, GNOME Keyring, dconf, graphics, gvfs, tumbler and udisks2. Building `checks.x86_64-linux.graphical-runtime` realises the complete NixOS closure. In the VM, `graphical.target` and greetd are active, greetd's generated command contains `--cmd niri-session`, polkit and udisks2 start, and the Niri, PipeWire and WirePlumber units exist. |
| AC3 | verified | Evaluation, build and runtime at `2478711`: the test imports the actual `homeManager.linuxGraphical` class with `homeManager.desktop`; its closure contains Noctalia, Hypridle, XWayland Satellite, Fcitx5 Hangul, XDG and GTK integration and the selected graphical tools. The booted VM runs the locked `niri validate` and `noctalia config validate` successfully against the generated files, finds the Hangul profile and Hypridle configuration, and resolves every accepted GUI command from the managed account's PATH. |
| AC4 | verified | Review of `2478711`: existing WezTerm, Ghostty and font concern files are unchanged. The new modules contain no fixed home, wallpaper, avatar, location, weather, monitor, hardware, network or secret value. The maintainer-excluded ebook, Zed, EasyEffects, OBS, Krita/Inkscape, Sunshine/Moonlight, Steam/Gamescope, Helix, Atuin, ipcalc, curlie and age/SOPS set is absent. `tool/version-control/hygiene` passes over 396 tracked paths. |
| AC5 | verified | Evaluation, build and runtime at `2478711`: `flake-test` accepts package single ownership across the real NixOS and Darwin configurations. `nix-index`, tealdeer and zoxide own their Home Manager concerns; the remaining accepted utilities have one owner in `modules/packages.nix`. The graphical VM builds the shared home and resolves `croc`, `dig`, `doggo`, `duf`, `dust`, `gping`, `hyperfine`, `jc`, `mtr`, `nix-index`, `nix-tree`, `nom`, `procs`, `rsync`, `sad`, `tldr`, `trash` and `zoxide`. |
| AC6 | verified | Native runtime on the x86_64 Linux checkout at `2478711`: `nix build --no-link path:./unixlike#checks.x86_64-linux.graphical-runtime` exits 0 with KVM unavailable and QEMU using TCG. The VM reaches the graphical target, validates the generated configurations and installed commands, and reports no failed system unit. The final test script finishes in 259 seconds; its reduced fixture supplies only the disposable Home Manager account because account, SSH and firewall integration is already owned by `headless-runtime`. |
| AC7 | verified | GitHub read on 2026-09-23: PR #333 at `87de9e8` passes `Required checks`; its Unix-like job, including the graphical VM check, passes in 7m35s ([run 35759183765](https://github.com/shk95/configs/actions/runs/35759183765)). This report ends in the same PR; its final report-only head must pass the protected gate again before merge. |

All acceptance criteria are verified. Evaluation, build and native runtime
evidence are complete; activation is not applicable to this shared, uncomposed
base. The installed-host evidence remains owned by roadmap order 10.
