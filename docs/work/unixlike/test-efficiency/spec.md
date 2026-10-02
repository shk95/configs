# Reduce repeated work inside Unix-like verification

kind: spec
date: 2026-09-26
scope: unixlike
status: approved
review-by: 2026-10-26
issue: #411

## Problem

The 2026-09-26 baseline PR CI run 36216060416 spent 342 seconds in
flake-test, 250 in test and 116 in import-order-test. These are observations,
not a controlled benchmark. The runner estimates download sizes even for
hosts it intentionally does not build, and the import-order detector's
negative fixture composes the entire real tree again.

## Decisions

Remove informational skipped-build size estimation while preserving every
configuration evaluation and the build selection contract. Keep the real
composition scan in lint and use representative positive/negative inputs
for its fixture suite. Keep full real-tree forward/reverse import-order
verification; exercise its identical collection, composition and comparison
engine against small synthetic outputs for detector fixtures. Batch only
read-only positive host-contract queries where assertions and diagnostics
can be retained. External provider tests, rejection tests and runtime
checks remain distinct. Do not reduce the set of real outputs verified.

Reject deleting negative tests, treating evaluation as runtime, and changing
repository CI selection in this scope. Defer batching that obscures a
failure's host/property or changes what is forced.

## Increments

1. Implement and verify the Unix-like check internals in one evaluation
   increment, carrying local and Linux CI evidence in this report and PR.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Skipped hosts remain evaluated and explicitly reported without informational build planning; native build selection and evaluation failures remain covered. | evaluation, review |
| AC2 | Real-tree composition remains checked once by lint; fixtures still accept valid contributions and reject both violations. | evaluation |
| AC3 | Every real output remains compared in both import orders; the same detector accepts a minimal stable input and refuses order-dependent derivations by name. | evaluation, review |
| AC4 | Safe query batching preserves host identity, state version, platform and graphical marker checks, with external consumer, negative and runtime coverage retained. | evaluation, review |
| AC5 | Record local and CI measurements, their comparability limits, and deferred candidates without claiming activation or a release. | review |

## Excluded

Repository workflows, dispatch, worker skills, Windows changes, deployment,
activation, merging dev and dependency updates are outside this increment.
