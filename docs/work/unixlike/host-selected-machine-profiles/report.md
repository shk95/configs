# Report: host-selected machine profiles

kind: report
spec: docs/work/unixlike/host-selected-machine-profiles/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | On commit `17e970c`, the schema portion of `unixlike/tool/checks/flake-test` accepted each declared host and refused an extra or missing host choice, an unknown or unavailable profile, and a repeated profile. |
| AC2 | verified | On commit `17e970c`, the same fixture found Codex in the NixOS-WSL home when `agents` was selected and absent when omitted; `unixlike/tool/checks/composition-test` found 63 feature files naming no host or forced class decision. |
| AC3 | verified | On 2026-09-23, `nix eval` compared five NixOS toplevel derivation paths, the standalone Home Manager activation derivation and the Darwin system derivation against `1314520`; all seven paths matched. `nix flake check --no-build path:./unixlike` passed with incompatible Linux-system checks omitted on this Mac. |
| AC4 | pending | The Unix-like decision, invariants and status are in `17e970c`; the repository-owned architecture text and a commit-based review remain. |

## Evidence lanes

- Evaluation: the profile fixtures, `unixlike/tool/checks/composition-test`,
  `unixlike/tool/checks/import-order-test`, seven derivation-path comparisons
  and `nix flake check --no-build path:./unixlike` passed on 2026-09-23.
  `unixlike/tool/checks/flake-test` reached `✓ flake schema fixtures behave`,
  then its chained `install-plan-test` failed because the default macOS
  temporary path resolves through the `/var` symlink, which Nix refuses.
  The complete chained script therefore did not pass. The flake check omitted
  incompatible `aarch64-linux` and `x86_64-linux` checks on this Mac.
- Build: unavailable on this `aarch64-darwin` host for the affected Linux
  targets. The 2026-09-23 pre-push test also attempted the unchanged Darwin
  toplevel and failed: `trash-cli` and `trash` both provide `bin/trash` in
  `home-manager-path`. The Darwin derivation path matches the base commit,
  so this is not evidence of a new output regression, but it is a real failed
  build and the push was refused. Matching derivation paths are evaluation
  evidence, not a completed build.
- Native runtime: not observed.
- Activation: not requested or performed.
