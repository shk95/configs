# Report: reduce repeated work inside Unix-like verification

kind: report
spec: docs/work/unixlike/test-efficiency/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Evaluation-coverage fixtures pass, including empty/no-output refusal, failed-host refusal and native NixOS build selection. The pre-push gate evaluated all seven provider outputs and built fixture-mac on aarch64 Darwin. Skipped-build size planning is removed; evaluation and build decisions are unchanged. |
| AC2 | verified | Pre-commit lint ran the real composition scan. Composition fixtures accepted the valid contribution with comment mentions and rejected forced values and host naming. |
| AC3 | verified | The final local import-order suite accepted all 74 real modules in both orders, accepted the minimal stable fixture and refused the order-dependent pair, identifying all three output flavours. Production module collection still uses the original flake store path. |
| AC4 | verified | Full local flake-test passed, including external consumer and rejection tests. One evaluation replaces 45 positive host-property queries. A temporary mutation of the extracted query reported every one of 30 injected mismatches across five hosts and six properties; the unmodified query passed. Runtime check definitions and host configuration sources are unchanged. |
| AC5 | verified | Baseline and candidate Linux CI measurements are recorded below with host, cache and attribution limits. Local evidence is separate; no aggregate speed guarantee is made. |

## Evidence lanes

- Evaluation: `eval-coverage-test`, `composition-test`, `flake-test` and
  `import-order-test` passed on aarch64 Darwin. Pre-commit formatting, lint,
  payload and policy checks passed. The pre-push gate evaluated all seven
  provider configurations. The final import-order suite used committed source
  `20650e1`; an earlier run overlapped an edit and is excluded from evidence.
- Build: The pre-push gate built `darwinConfigurations.fixture-mac` natively.
  Foreign outputs were evaluated, not built locally. Linux CI run 36221624262
  built the standalone Home Manager fixture and evaluated all seven outputs.
- Native runtime: No host runtime claim. Existing headless/graphical flake
  runtime check definitions remain unchanged; Darwin runs no Linux checks.
  Linux CI run 36221624262 passed the headless and graphical VM runtime
  checks and all three Zellij patch checks. This is synthetic CI evidence,
  not installed-host runtime or activation.
- Activation: not requested or performed.
- Review: Changes are confined to Unix-like check internals, their fixture,
  invariant explanation and these work documents. No dependency update,
  desired-state edit, CI selection change or dev merge was performed.

## Measurements

The baseline is GitHub PR run
[36216060416](https://github.com/shk95/configs/actions/runs/36216060416)
from 2026-09-26. Its Unix-like job took 762 seconds; `flake-test` took 342,
`test` took 250 and `import-order-test` took 116. This is the existing locked
input version at the branch base `b8a8770`, not a controlled paired benchmark. Runner hardware allocation, store/cache
contents and network timing were not controlled.

Candidate run [36221624262](https://github.com/shk95/configs/actions/runs/36221624262)
passed all required checks for `20650e1`. Observed seconds:

| Check | Baseline | Candidate |
| --- | ---: | ---: |
| flake-test | 342 | 241 |
| test | 250 | 209 |
| import-order-test | 116 | 48 |
| Unix-like job | 762 | 539 |

These are individual execution measurements, not an aggregate speed guarantee
or proof that each time difference comes solely from this patch.

Local elapsed times were 297.81 seconds for `flake-test` and 143.29 seconds
for the final `import-order-test`. Checks overlapped on the same Mac, so
these are execution observations, not a speedup comparison against Linux.
The isolated minimal stable detector fixture took 0.35 seconds locally.
No percentage speedup is inferred from those different environments.

## Review hardening

The real-tree positive unsets `CHECKS_IMPORT_MODULES` in a subshell, so an
external fixture override cannot silently replace it. The fixture path is
passed as an explicitly overwritten environment value read by Nix, rather
than interpolated as source text. A directory containing a double quote
passed the stable detector probe. Running the entire suite with inherited
`CHECKS_IMPORT_MODULES=/does-not-exist` still accepted all 74 actual modules,
accepted the minimal positive and rejected the pair for all three flavours;
that local run took 128.51 seconds. The comparator and real output coverage
are unchanged.

## Deferred candidates

- Remaining schema queries and negative cases are unchanged. Further batching
  needs separate measurements and preserved failure attribution; external
  provider tests are not duplicates of internal contracts.
- Runtime tests remain separate from evaluation. No runtime guarantee was
  replaced by a derivation comparison.
- Effect-based CI selection and PR/post-merge verification reuse belong to
  repository governance and remain outside this worktree.
- The composition duplicate was inexpensive; removing it is housekeeping,
  not the explanation for any large CI time difference.

## Outcome

Implementation and evidence are available in PR #415. The PR remains Draft
until checks pass on its final head, including the review hardening.
Integration belongs to the separate integration session; no auto-merge is
armed and no deployment or release is claimed.
