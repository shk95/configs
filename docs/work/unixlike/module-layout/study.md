# Group the Unix-like module tree for human navigation

kind: study
date: 2026-09-24
scope: unixlike
status: closed
outcome: docs/work/unixlike/module-layout/spec.md

This is a proposed file inventory, not a rule that a directory determines a
Nix module class. It was read from `dev` at `269dd11` on 2026-09-24. The
earlier restructure study measured the tree before `unixlike/` existed; it
chose concern-first placement while joining modules, payloads and scripts
inside the domain. It rejected class-first `darwin/nixos/hm` directories,
not a small number of human navigation groups within `modules/`.

`import-tree` recursively collects `.nix` files below `modules/`, and the
feature class is written in each file. The proposed group therefore cannot
become a second composition authority. The file that chooses classes for
hosts remains the sole composition point. Existing module-local payloads and
scripts move as units. No file is split merely to make a group pure.

## Proposed groups and file inventory

| Group | Present paths assigned to it | Placement rule |
| --- | --- | --- |
| `flake/` | All existing `flake/*` files | Flake-level schema, input policy, checks and output construction; the eventual provider API also lives here. |
| `machines/` | `host/{desktop,orbstack,utm,vmware}.nix`, `amd-apu.nix` | Hardware, hypervisor and machine-kind facts, never an individual host's identity. |
| `platforms/` | `host/darwin.nix`, `wsl.nix`, `defaults.nix`, `homebrew.nix`, `editor/{darwin,wsl}.nix` | Darwin or WSL integration that is neither a portable program nor a machine kind. |
| `foundation/` | `host/nixos.nix`, `account.nix`, `home-account.nix`, `firewall.nix`, `installation.nix`, `nix/{darwin,shared}.nix`, `packages.nix`, `shell/{darwin-home,darwin,headless,orbstack,shared,wsl}.nix`, `ssh.nix`, `sshd.nix`, `state-version.nix`, `timezone.nix` | Account, system access, installation, package ownership and shell/Nix baseline. A platform-specific fragment stays beside other fragments of the same concern. |
| `desktop/` | `audio.nix`, `fonts/{desktop,wsl}.nix`, `graphical/{base,home}.nix`, `hypridle.nix`, `input-method.nix`, `media.nix`, `niri/{home,system}.nix`, `noctalia.nix` | Graphical session and its supporting services; Niri's system and home fragments stay together. |
| `programs/` | `agents.nix`, `bat.nix`, `btop.nix`, `direnv.nix`, `eza.nix`, `fzf.nix`, `gh.nix`, `ghostty.nix`, `git.nix`, `glow.nix`, `karabiner/`, `lazygit.nix`, `neovim.nix`, `nix-index.nix`, `powershell/`, `skim.nix`, `starship.nix`, `tealdeer.nix`, `uv.nix`, `wezterm/`, `yazi.nix`, `zellij/`, `zoxide.nix` | An individually managed program and every payload or script it owns. |

The table assigns every current module concern once. Two placements deserve
review before the move: `installation.nix` is a reusable storage contract
rather than a machine fact, and `fonts/wsl.nix` is kept with the font concern
despite being a non-graphical WSL fragment. `host/nixos.nix` defines the
typed value a NixOS configuration receives, so it is a foundation contract,
not a file for a particular host. If inspection changes a placement, update
this table and the spec before moving the file.

On 2026-09-24 at `269dd11`, a read-only path classification over all 89
regular files below `unixlike/modules/` matched each file to exactly one row
of this table; zero were unmatched or assigned twice. This checks coverage
of the proposed map, not whether every placement is conceptually right.

## Existing path readers

The move affects relative references inside Nix files, the paths in
`unixlike/payloads.json`, literal paths in `unixlike/tool/checks/`, installation
helpers, the root `Justfile`, CI, documentation, and any external reference to
the source tree. The current tree contains 16 declared payloads. The move
must update those declarations and parse them with the declared consumers.
The positive composition and import-order fixtures must still discover the
new tree. `import-tree` ignores paths containing `/_`, so no proposed group
uses that prefix.

The 2026-09-24 path search at `269dd11` found active, non-module readers that
need individual review:

| Reader | Current literal or discovery |
| --- | --- |
| `unixlike/payloads.json` | Sixteen payload paths relative to the module tree. |
| `unixlike/tool/checks/flake-test` | Explicit schema and inventory imports, desktop machine files, and many evaluated host outputs. |
| `unixlike/tool/checks/karabiner-test` | Three explicit Karabiner module-side paths. |
| `unixlike/tool/checks/composition` and `import-order` | Recursive module discovery with `flake/` as the composition exemption. |
| Root `Justfile` | An executable Karabiner tool path and source-path guidance for shell modules. |
| `.github/workflows/zellij-upstream-5500.yml` | Executable overlay path plus explanatory paths. |
| `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `docs/policy/`, `docs/status/` | Current policy, procedure and status paths; update statements that describe the live layout. |
| Existing `docs/work/` reports and studies | Dated evidence and historical paths; retain their original referents rather than silently rewriting history. |

The search does not prove this list is exhaustive: relative references such
as `../` and externally held paths need the move's full diff and a second
search. `Justfile` classifies as `unixlike`; CI and repository governance
paths classify as `repository`, so their path changes need a separate
repository increment under the one-scope-per-commit rule.

## Evidence and limits

Before moving files, record the seven existing output derivation paths from
the pinned flake. After the move, compare all seven and investigate every
difference; the old restructure spike's equality is evidence for its own
older tree, not proof for this one. Run path-reference search, payload
validation, composition and import-order fixtures, then the normal scoped
evaluation and appropriate native build checks. Native runtime and host
activation are outside a physical source relocation unless a difference
shows the host result changed.

On 2026-09-24 at `dev` commit `269dd11`, `nix eval --impure --json --expr`
with `builtins.getFlake (toString ./unixlike)` evaluated the seven current
output derivation paths without building or activating any host:

| Output | Baseline derivation path |
| --- | --- |
| `darwinConfigurations.shk-macbook` | `/nix/store/jn1lkq5h7kvalwmf6v3yih8qzfqi10zq-darwin-system-26.11.4cff07d.drv` |
| `homeConfigurations.user1` | `/nix/store/qz6mn43wxqy3r1c90iak0x49191ii5xk-home-manager-generation.drv` |
| `nixosConfigurations.desktop` | `/nix/store/7lhc6r1sk1wym5xh1g7qdiavwamn34pj-nixos-system-desktop-26.11.20260916.b1b8759.drv` |
| `nixosConfigurations.nixos` | `/nix/store/2v9adg7mfz2mqhqpp1a73cwqqgc0lpb1-nixos-system-nixos-26.11.20260916.b1b8759.drv` |
| `nixosConfigurations.orbstack` | `/nix/store/x0yd9iv66w0p9xvsl6si00nnn3vhcb70-nixos-system-orbstack-lxc-26.11.20260916.b1b8759.drv` |
| `nixosConfigurations.utm` | `/nix/store/5z0gk1l5sn0mb0pwkplf9igrnbpij562-nixos-system-utm-26.11.20260916.b1b8759.drv` |
| `nixosConfigurations.vm` | `/nix/store/r1r5p5gv5010hixld06a2z9a4dnniknk-nixos-system-vm-26.11.20260916.b1b8759.drv` |
