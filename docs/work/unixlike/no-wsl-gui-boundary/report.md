# Report: make the WSL command-line boundary explicit

kind: report
spec: docs/work/unixlike/no-wsl-gui-boundary/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review at `9d9aae9`: the invariant, NixOS-WSL decision, Home Manager class decision and Unix-like status exclude WSL GUI and direct any future proposal to revise the architecture and invariant first. |
| AC2 | verified | On aarch64-darwin, the `unixlike/tool/checks/flake-test` WSL section evaluated both WSL homes without WezTerm, Noctalia or XWayland Satellite and evaluated `wsl.useWindowsDriver = false` and `wsl.startMenuLaunchers = false`; its positive graphical-home probes also passed. After merging `origin/dev`, `nix flake check --no-build path:./unixlike` passed, while warning that incompatible aarch64-linux and x86_64-linux checks were omitted. Direct evaluation returned both WSL derivations; neither was built here. |
| AC3 | verified | Review of the `9d9aae9` diff: the Nix module edits are comments only; the new fixture does not enter a host output. Fontconfig remains for Linux-side file rendering, with no WSLg rationale. `sh -n unixlike/tool/checks/flake-test`, the Unix-like pre-commit format, composition, payload and policy checks, and `git diff --check` passed. |

## Evidence lanes

- Evaluation: verified for both WSL outputs and the WSL fixture section on
  aarch64-darwin; the flake check passed with incompatible-system checks omitted.
- Build: not required; this work changes no Nix configuration value.
- Native runtime: not claimed; no running host was checked.
- Activation: not requested.
- Review: verified against `9d9aae9` and the post-merge working tree.

The rest of `flake-test` completed its schema fixture section, then its
installation-plan subtest failed on this Mac because the default `/var` temp
path is a symlink. With `TMPDIR=/private/tmp`, that subtest reached its
x86_64-only installation-test guard and stopped on this aarch64 host. Neither
failure concerns the WSL checks. The pull request's Linux CI is the full
suite evidence; it must pass before merge.
