# Report: adopt Niri and Noctalia on the VM guests

kind: report
spec: docs/work/unixlike/graphical-vm-guests/spec.md
status: pending

Automatic implementation commit `5b20df4` composes and checks both guest
outputs. This report remains pending for the repository-scope procedure and
the two installed-guest evidence increments. No guest was activated.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | `unixlike/modules/flake/configurations.nix` keeps `nixos.utm` or `nixos.vmware` and `nixos.headless` in each guest row and adds `nixos.graphical`; both homes compose the shared, desktop and Linux graphical classes. `unixlike/tool/checks/composition-test` confirms that all 62 feature files name no host and force no value. |
| AC2 | verified | Evaluation and native build at `5b20df4`: the VMware assertion and fixture require full `open-vm-tools`, its vmblock mount, Niri, greetd, PipeWire, key-only SSH and port 22 alone. Direct evaluation returned `headless=false`, package `open-vm-tools`, `vmblock=true`, `niri=true`, `ssh=true` and ports `[22]`. The locked x86_64 toplevel built as `/nix/store/8y0l58zss29qirmg4p8pmsblm0lr0dk1-nixos-system-vm-26.11.20260916.b1b8759`; `nix path-info -Sh` reports a 10.4 GiB closure. |
| AC3 | verified | `nix flake check --no-build path:./unixlike` evaluates the UTM output for aarch64, and its host assertion plus positive and negative fixture require the QEMU guest service, both serial-console parameters, the graphical services, key-only SSH and port 22 alone. Its evaluated toplevel is `/nix/store/bdf9k51kl3pn063s90nw67xcsjd8r1bi-nixos-system-utm-26.11.20260916.b1b8759.drv`; no aarch64 build is claimed. |
| AC4 | verified | Native x86_64 runtime at `5b20df4`: `nix build --no-link` succeeds for `/nix/store/my7fmjhcvm132h1wwg8jhg3mrlnql5m3-vm-test-run-configs-graphical-runtime` and `/nix/store/l9iik30kxxajmvg60xhkb8pppmh3ap9x-vm-test-run-configs-headless-runtime`. The first boots the actual shared graphical classes and validates their services, files and programs; the second separately boots and exercises the account, SSH and firewall recovery contract. |
| AC5 | verified | `unixlike/tool/checks/flake-test` requires all `desktop` and `vm` hosts to enable Niri, greetd and PipeWire and to contain the graphical home markers, while both WSL homes and OrbStack contain none. Review found no change to the physical desktop row. |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |
| AC9 | pending | |
