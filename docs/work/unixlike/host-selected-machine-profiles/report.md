# Report: host-selected machine profiles

kind: report
spec: docs/work/unixlike/host-selected-machine-profiles/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | On commit `17e970c`, the schema portion of `unixlike/tool/checks/flake-test` accepted each declared host and refused an extra or missing host choice, an unknown or unavailable profile, and a repeated profile. |
| AC2 | verified | On commit `17e970c`, the same fixture found Codex in the NixOS-WSL home when `agents` was selected and absent when omitted; `unixlike/tool/checks/composition-test` found 63 feature files naming no host or forced class decision. |
| AC3 | verified | After the separate trash collision fix entered `dev`, `nix eval` compared five NixOS toplevel derivation paths, the standalone Home Manager activation derivation and the Darwin system derivation against `facd625`; all seven paths matched on 2026-09-23. `nix flake check --no-build path:./unixlike` passed with incompatible Linux-system checks omitted on this Mac. |
| AC4 | verified | Codex reviewed the merged Unix-like decision, invariants and status in `fa58bfc` (PR #350) and the repository-owned architecture in `4a6c413` (PR #351) on 2026-09-23. They agree that machine kinds offer profiles, hosts make typed selections, and central composition validates and imports them. The maintainer authorized the `done` decision after this review. |

## Evidence lanes

- Evaluation: the profile fixtures, `unixlike/tool/checks/composition-test`,
  `unixlike/tool/checks/import-order-test`, seven derivation-path comparisons
  and `nix flake check --no-build path:./unixlike` passed on 2026-09-23.
  The final comparison baseline is `facd625`, after the independent
  `trash` package collision fix. All seven output paths agree with it.
  `unixlike/tool/checks/flake-test` reached `✓ flake schema fixtures behave`,
  then its chained `install-plan-test` failed because the default macOS
  temporary path resolves through the `/var` symlink, which Nix refuses.
  The complete chained script therefore did not pass. The flake check omitted
  incompatible `aarch64-linux` and `x86_64-linux` checks on this Mac. The
  complete Unix-like CI job and Required checks passed for PR #350 on Linux.
- Build: unavailable on this `aarch64-darwin` host for the affected Linux
  targets. The first pre-push attempt failed to build the then-unchanged
  Darwin toplevel because `trash-cli` and `trash` both provided `bin/trash`;
  no hook was bypassed. The independent fix merged as PR #349. After merging
  that `dev` into this branch, `nix build --no-link` of the Darwin system
  passed on 2026-09-23. This native Darwin build is not a Linux build.
- Native runtime: not observed.
- Activation: not requested or performed.
- Review: Codex reviewed merged commits `fa58bfc` and `4a6c413` against AC4
  on 2026-09-23; the repository maintainer approved marking this report
  `done` after review. This review does not certify a release or deployment.
