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
| AC4 | verified | Public `shk95/configs-host-template` pins the merged provider API `66fed098` in its synthetic `example` flake. `tool/check-hosts` evaluated its final output on aarch64 Darwin and GitHub Actions run `35979339688` passed on x86_64 Linux. Its README states the one-time copy model and the host-owned SOPS + age boundary without a real identity, recipient or secret. |
| AC5 | pending | Private `shk95/configs-hosts` PR #1 merged seven independent host flakes and locks, pinned to provider merge `66fed098`. All seven final `drvPath` values matched the `e8730ce` baseline; local `tool/check-hosts` and Linux CI run `35979483776` passed. Darwin built natively on aarch64 macOS, and the OrbStack and UTM consumers built natively in their aarch64 Linux guests. The other installed Linux and WSL consumers still need native builds; all consumers need their own runtime evidence. The physical desktop is uninstalled. No consumer activation was requested. |
| AC6 | pending | |
| AC7 | pending | |
| AC8 | pending | |

## Evidence lanes

- Evaluation: `provider-api-test` passes across a separate consumer flake for all three constructors and checks negative cases; all seven current output derivation paths match the clean `e8730ce` baseline. `nix flake check --no-build`, `composition-test`, and `import-order-test` pass on aarch64 Darwin. The existing local `flake-test` passed its schema fixtures, while its later installation fixture stopped because macOS `/var` is a symlink. The first Linux CI run found that the graphical runtime fixture, which composes classes without a constructor, lacked typed Home Manager identity. After that fixture supplied it, CI runs `35975584104` and final `35977694175` passed `flake-test`, full output evaluation, and `import-order-test` on x86_64 Linux.
- External template evaluation: Public template commit `dcb8c6d` pins the provider merge and passed `tool/check-hosts` locally and in Linux CI run `35979339688`; the repository is marked as a GitHub template.
- Build: The existing Darwin output built natively on aarch64 macOS after the API refactor. CI run `35975584104` built the standalone x86_64 Linux home. The private consumer's Darwin output built natively on aarch64 macOS. Its OrbStack output built on the already running aarch64 Linux machine with `nix build --no-link --max-jobs 2`; the resulting system path differed from `/run/current-system`. The UTM consumer also built its toplevel with that command inside its aarch64 NixOS guest, started in UTM disposable mode. The first test temporarily used macOS Shared Network to fetch inputs, then restored the original VM configuration byte-for-byte. After the maintainer authorized Shared as the permanent VM mode, a fresh guest boot showed a default route and successful DNS lookup; the VM was stopped with Shared still configured. The UTM built system path differed from `/run/current-system`. The other installed Linux and WSL consumers still need matching builds.
- Native runtime: pending in each migrated host. The physical desktop has no installed runtime.
- Activation: not requested; any future action is recorded per host.
- Review: The typed public arguments and extension points are recorded in `docs/policy/decisions/unixlike/provider-constructors-own-composition.md`. The public template and private consumer declarations are available. Host-specific native evidence, secret recipients and final provider-only state remain pending; the current provider inventory and outputs stay in place.
