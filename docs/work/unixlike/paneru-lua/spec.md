# Paneru flake integration and Lua migration
kind: spec
date: 2026-11-01
scope: unixlike
status: approved
review-by: 2026-11-08

Add the Paneru input and its upstream Home Manager service to the Darwin
home class. Migrate the current host TOML configuration to a source Lua
payload without changing active behavior. Preserve all explanatory comments
and inactive examples, adapting syntax and descriptions to Lua.

The initial primary-checkout changes already add Paneru at
`3efa72bb7bf791ba9009f9c5990e628d6ecd631a`; retain that pin and all existing
input pins. Initial local dev `f631a058d2d77442fb043921a2c48e527eb5c679`
incorporated the then-selected local master snapshot. Publication additionally
incorporates master `b03f0f34e1962348b17bef186b1c47a261ed4c58`. Prepare source in
a dedicated linked worktree on `feature/unixlike-paneru-lua`. Branch and
worktree creation were authorized for initial implementation. The subsequent
publication request authorizes source commits, dev integration, protected
master promotion and Unix-like versioning. The release declaration is
`1.1.0` (minor), based on `unixlike-v1.0.26`.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Darwin imports the upstream Home Manager service with the Lua runtime and one owner for package, service and configuration; other platforms remain outside it. Existing input pins are unchanged. | review, evaluation, build |
| AC2 | All active TOML settings, 33 bindings and seven window rules are preserved in Lua; all comments and inactive examples retain their meaning in Lua context. The payload is declared and parses. | review, evaluation |

## Verification and deployment

Compare the evaluated Lua setup table to a separately parsed TOML source;
review every prose adjustment and inactive example. Evaluate provider
composition, run formatting, lint, payload and import-order checks, and build
the native Paneru package and delivered configuration. Report host runtime
and activation separately; neither provider checks nor a package build
certifies a consumer adoption or changes the running host. Real host
activation uses the reviewed private consumer, with the source selection
explicitly reviewed before switching.
