# Status and decisions

## Monorepo convergence

The repository converges four former projects into one configuration model.
The architecture follows the tested dendritic pattern from `nix-wsl`:
flake-parts evaluates every feature file collected by import-tree, deferred
module classes merge feature contributions, and one composition module assigns
those fragments to hosts.

`nix-config` was an early prototype. Its Darwin defaults, Homebrew list,
packages, and host values were migrated as content; its explicit import tree
and `specialArgs` wiring were not.

`term-config` contributes one shared WezTerm aspect. Home Manager deploys it
on Unix-like hosts and the Windows manifest deploys the same source files
natively.

`win-env` remains the source of Windows reconciliation semantics: read-only
check, package detection, managed-file comparison, first-original backup,
PowerToys lifecycle handling, font integrity, post-apply validation, and
recoverable state. The addon framework was a boundary between repositories and
is removed now that composition is static.

## History boundary

This monorepo starts a clean history because the convergence changes both
ownership and composition rather than merely moving four directory trees. The
former repositories are archived independently; their unrelated histories are
not merged, vendored, or retained as refs in this repository.

The initial convergence used these source revisions:

- `term-config` `master`: `9282d19`
- `win-env` `master`: `dc5d27d` (`v0.1.0`)
- `win-env` `dev`: `64f0b90`
- `win-env` local `draft`: `dd13282`
- `nix-wsl` `dev`: `1875f8f`
- `nix-config` `master`: `84c05c2`
- `nix-config` remote `darwin`: `5f94d5d`

These identifiers are provenance, not Git parents. New development integrates
on `dev`; `master` identifies the latest state validated on the affected real
hosts. Short-lived feature and fix branches start from `dev`, and validated
snapshots receive date-based tags only after promotion to `master`.

## Windows generation boundary

Windows cannot evaluate Nix and does not need to. A Unix-like development host
builds `packages.<system>.windows-bundle`; `tool/render-windows` materialises
that output under `windows/generated/`; source and generated result are
committed together.

The generated tree must contain no timestamps, Nix store paths, or final Git
commit hash. A commit hash cannot be an input to content committed by that same
commit. Windows records the checkout commit at apply time and separately hashes
the generated bundle for drift.

## Verification observed during initial convergence

- The standalone WSL Home Manager activation derivation evaluates.
- The NixOS-WSL system derivation evaluates.
- The nix-darwin system derivation evaluates for `aarch64-darwin`.
- The Windows bundle builds and its JSON/Lua payload is checked in the
  derivation.
- No Unix-like configuration was activated.
- No native-Windows apply was performed; native Pester and `-Check` remain
  required evidence for Windows runtime behavior.

## Import-order caveat

Auto-imported deferred modules do not preserve the former hand-written import
order. List-valued options can therefore produce different store hashes even
when their element set is unchanged. Features whose list order carries meaning
must use explicit ordering or a keyed attribute model instead of relying on
file collection order.
