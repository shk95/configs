# Report: Unix-like provider API and external host instances

kind: report
spec: docs/work/unixlike/host-provider-api/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | The exported `lib.mkNixos`, `lib.mkDarwin`, and `lib.mkHome` are called by `provider-api-test` without importing internal files. Its synthetic NixOS, Darwin, and standalone Home outputs take their name, account, and Git values from the consumer; NixOS system and home extension modules also reach the final evaluator. |
| AC2 | verified | The constructor input schema rejects missing Git identity and host state version, an illegal machine combination, duplicate, unavailable, and unknown profiles. The existing `flake-test` still checks the five legal machine combinations and profile selection on the current outputs. |
| AC3 | verified | All seven current outputs use the exported constructors. On 2026-09-24 their toplevel derivation paths matched the clean `origin/dev` tree at `e8730ce` exactly after the constructor refactor and again after formatting. No generated-setting difference was observed in the final derivations. |
| AC4 | pending | |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |

## Evidence lanes

- Evaluation: `provider-api-test` passes across a separate consumer flake for all three constructors and checks negative cases; all seven current output derivation paths match the clean `e8730ce` baseline. `nix flake check --no-build`, `composition-test`, and `import-order-test` pass on aarch64 Darwin. The existing local `flake-test` passed its schema fixtures, while its later installation fixture stopped because macOS `/var` is a symlink. The first Linux CI run passed `flake-test` but found that the graphical runtime fixture, which composes classes without a constructor, lacked typed Home Manager identity. That fixture now supplies it and its test derivation evaluates locally; a Linux rerun is pending.
- Build: The existing Darwin output built natively on aarch64 macOS after the API refactor. The standalone x86_64 Linux home awaits the Linux CI job; migrated hosts still need their own matching builds.
- Native runtime: pending in each migrated host.
- Activation: not requested; any future action is recorded per host.
- Review: The typed public arguments and extension points are recorded in `docs/policy/decisions/unixlike/provider-constructors-own-composition.md`; external template, host migrations, and final provider-only state remain pending.
