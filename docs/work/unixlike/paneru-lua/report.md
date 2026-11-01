# Paneru flake integration and Lua migration report
kind: report
spec: docs/work/unixlike/paneru-lua/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review: upstream `nix/README.md`, `nix/home.nix` and `_paneru-common.nix` at locked Paneru `3efa72bb7bf791ba9009f9c5990e628d6ecd631a`; all eight pre-existing input nodes match the selected master snapshot `b03f0f34e1962348b17bef186b1c47a261ed4c58` as JSON after incorporating its already published input patches. Evaluation: Darwin toplevel, both Lua destination variants, 71 public contract cases, 11 constructor/environment toplevels and API refusal fixtures passed. Import-order check passed for 57 modules. Build: the initial native aarch64-darwin Lua-enabled package and wrapper succeeded, including a repeat realization from this worktree. Final combined-result verification after master synchronization is recorded below. The generated launchd Program points to the wrapper binary. |
| AC2 | verified | Review: all 267 standalone prose lines and 84 disabled field examples are retained, with Lua context adjustments to nine prose lines and table/array/key syntax; inline comments are preserved. A separate TOML parser and Lua setup-table capture compared every active value, all 33 command/chord pairs and all seven window rules recursively under Lua 5.4 and the pinned LuaJIT. Payload syntax/declaration check passed for all 18 payloads. The delivered Lua artifact was built and matched the source. |

## Source and checks

The host TOML input SHA-256 is
`939fbba435e12830d412eddf693be36ca6eed39426088b34f15e9c91ce2e1a22`.
The original file remains unchanged. Optional examples remain inactive;
Lua binding commands use spaces, while chord punctuation (including `[` and
`]`) is preserved. Alternative dimming examples are separate commented Lua
tables and explain selecting one mode.

Formatting, statix, deadnix, composition and work-document checks passed.
All changed paths classify as Unix-like. Source was prepared in the linked
`paneru-lua` worktree on `feature/unixlike-paneru-lua`, based on local dev
`f631a058d2d77442fb043921a2c48e527eb5c679`; the original primary checkout's
three Paneru draft files were preserved in a local stash before integration. The initial implementation checkpoint preceded commits and publication.
The subsequent request authorizes publication: selected master
`b03f0f34e1962348b17bef186b1c47a261ed4c58` was reflected by dev-based
merge `71b5abd`; the source-owned release declaration is `1.1.0` (minor),
based on `unixlike-v1.0.26`. Protected promotion and immutable tag evidence
belong to the PR and release annotation.

## Host evidence

Native GUI runtime and activation have not been performed. The built CLI
reports `paneru 0.5.2 (LuaJIT)` and renders its help successfully; its launchd
Program exists and is executable. Lua interpreter
execution is configuration-equivalence evidence, not a running window-manager
session. The current host still runs its independently installed Homebrew
Paneru 0.5.2 service. Consumer adoption and host switching are separate from
this provider change; no private consumer pin or host configuration was
modified.

## Initial build artifacts

- Lua-enabled package wrapper: `/nix/store/aqq26wxfrx8xbzhqnkvd33xl83a0a7cs-paneru-with-lua-wrapped`.
- Delivered Lua payload: `/nix/store/8an82ddzrpvcw90k02jhvjw3f79zkl1g-source`, byte-identical to the final source.
- Synthetic Darwin evaluation: `/nix/store/27cy908f3kgnfhh7y318q7xrkjayyigd-darwin-system-26.11.bb0b90d.drv` for the final payload; import-order and API witnesses also passed. No synthetic or private host closure was built.

## Publication candidate verification

After incorporation of selected master inputs, formatting, lint and the
complete `unixlike/tool/checks/test` provider suite passed on aarch64-darwin.
All seven exported examples evaluated, all 71 public contract cases and 11
constructor/environment toplevels passed, declared payloads parsed, import
order was stable and six matching-system flake artifact checks passed.
The local flake check explicitly omitted incompatible Linux systems; the
master PR's Linux CI supplies its own required evidence.

The native Paneru package was realized again after synchronization and remains
`/nix/store/aqq26wxfrx8xbzhqnkvd33xl83a0a7cs-paneru-with-lua-wrapped`.
The delivered Lua file matched the final source byte for byte at
`/nix/store/8an82ddzrpvcw90k02jhvjw3f79zkl1g-source`.
Final Darwin evaluation reached
`/nix/store/86vm48zybs15l0j1536riwbrq7p4i44h-darwin-system-26.11.ff0e21a.drv`.
Initial artifact paths above are retained as checkpoint evidence; no host
closure, graphical runtime or activation is inferred from these checks.
