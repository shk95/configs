# Recover Unix-like provider features: report
kind: report
spec: docs/work/unixlike/minimal-reconstruction/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | Evaluation: provider API 71 constructor cases and external-consumer fixtures passed locally. Selected native build and final remote CI remain separate endpoint gates. |
| AC2 | verified | Fixtures/evaluation: darwin-capture-test and karabiner-entry-test passed, including finite defaults, strict JSON/path, stale and atomic preservation, generated mkDarwin fixture, and retired publication no-effect checks. No actual host capture or activation. |
| AC3 | verified | Fixtures: refresh-inputs-test passed actual local Nix repositories, byte/mode/stale guards, read-only inventory and explicit selection preserving nonselected inputs; unknown, alias and duplicate selections refused. Automatic selection is exactly four declared inputs. |
| AC4 | verified | Fixtures: eval-coverage-test exercises eval-build directly; test wrapper invokes refresh, capture and retired-entry suites once before the core. The eight coverage cases no longer multiply independent suites into nine runs. |

## Source identity and native evidence

The original minimal endpoint's native qualification is historical and remains
in its original PR/Actions records. Exact-source qualification must be established by the matching Actions run and
recorded in the replacement annotation; it is not established by this report.
Existing local fixture rows describe their own source checkpoints. No host
adoption, activation or Apply is implied; pending native rows are not certified
by a foreign-host run or an old endpoint's successful CI.
