# Repository guidance for agents

## Goal and authority

This repository is one personal configuration system. The flake is the
composition authority for Unix-like hosts and for the desired Windows state.
Windows does not evaluate Nix: Unix-like development hosts render
`windows/generated/`, commit it with its source, and Windows only consumes it.

Every file below `modules/` is a flake-parts module collected by import-tree.
Prefer one feature per file. A feature may contribute Home Manager, NixOS,
nix-darwin, Windows desired state, checks, or several of those at once.
`modules/flake/configurations.nix` is the only place that decides which
deferred module classes reach a host.

The source repositories contributed different kinds of authority:

- `nix-wsl`: dendritic structure, verification boundaries, and WSL findings.
- `term-config`: shared WezTerm behavior and minimal platform differences.
- `win-env`: Windows ownership, drift detection, backup, and safe apply.
- `nix-config`: Darwin setting values only; its prototype wiring is not a
  pattern to preserve.

## Durable decisions

- Do not introduce `specialArgs` for repository identity or host inventory;
  declare typed flake-parts options instead.
- Do not create plugin or addon boundaries for features that live in this
  monorepo. Static module composition replaces cross-repository discovery.
- Do not edit `windows/generated/` by hand. Edit modules or assets, then run
  `tool/render-windows`.
- Do not add a second Windows manifest owned by PowerShell. PowerShell observes
  and reconciles the generated manifest.
- Do not rely on import-tree collection order for order-sensitive list values.
  Use explicit ordering or a keyed attribute model.
- Keep secrets, usernames outside the declared inventory, absolute home paths,
  and snapshots of runtime state out of generated Windows content.

## Host safety

- Never activate Home Manager, NixOS, or nix-darwin without an explicit request.
- Never run Windows `Apply` without an explicit request. `-Check` is the
  read-only Windows path.
- Do not update flake inputs, change login shells, garbage-collect Nix stores,
  shut down WSL, or change global Git configuration unless the task calls for it.
- Treat WSL cgroups, binfmt_misc, mounts, and similar kernel-global resources as
  shared by every distribution.
- Preserve externally managed PowerShell profile blocks. Do not change Windows
  OpenSSH DefaultShell or add a `.wslconfig` firewall value without explicit
  direction.
- Do not commit, push, tag, rewrite history, or change branches unless the user
  explicitly requests it.

## Working contract

1. Read `CONTRIBUTING.md` and the relevant part of `docs/status.md`.
2. Use `tool/doctor.sh` before relying on host-local capabilities.
3. Make the feature change in `modules/` and source payload changes in
   `assets/`.
4. Run `tool/render-windows` whenever Windows desired state may have changed.
5. Run the narrow checks, then `tool/checks/test`.
6. Report evaluation, build, activation, and native-Windows evidence separately.

User-facing usage belongs in `README.md`, shared workflow in
`CONTRIBUTING.md`, expensive decisions in `docs/status.md`, recurring
symptoms in `docs/troubleshooting.md`, and executable policy in `tool/`,
hooks, and CI. Model-specific context files only point to these sources.
