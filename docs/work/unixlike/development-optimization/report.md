# Unix-like development optimization results
kind: report
spec: docs/work/unixlike/development-optimization/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Baseline Just JSON signatures/dependencies/privacy and aliases match. Five real Just fixtures prove early refusals, unchanged source and active delegation; independent review confirms dead-body removal and utility retention. |
| AC2 | verified | Real Just argv/cwd spies in a path with spaces prove named/all intent boundaries, literal hostile input, option/empty refusal and the owning Unix-like flake. |
| AC3 | pending | |
| AC4 | pending | |

## Baseline and loop 1

Baseline master is e824c6f328edb9f9a73a66b5c00ae6523aefc23c; this topic is
independent of the repository topic. The exploratory work remains preserved.
The old provider-host target helpers already refuse, but later recipe bodies
still describe/build/activate those impossible targets, and `_nixos-host`
reads the host before refusal. `upp` and `fmt` incorrectly use the root cwd
despite the domain flake living in `unixlike/`.

Reuse only the exploration's bounded Just cleanup and its runtime fixtures;
omit the new source-authoring recipe and producer. Preserve all old signatures,
dependencies and aliases, remove unreachable effects, and bind active commands
to the provider flake. Group labels distinguish work/effect: the old repository
label contained Unix-like checks, while nix mixed formatting/input edits with
host garbage collection. The labels add no execution or readiness requirement.

All 56 baseline recipe parameter/dependency/privacy declarations and five
aliases match the actual Just JSON dump; one private refusal helper is added.
Preserve the original recipe order to avoid the exploratory menu's wholesale
reordering. The Justfile drops from 496 to 369 lines. Five real Just fixture
cases pass in a path containing spaces: literal input/option boundaries,
flake/cwd binding, all compatibility refusals with no tool/source effects,
menu semantics and active delegated utilities. No actual input was updated.
The wrapper needs Nix only when acquiring a missing Just/Python runtime.

Format/lint pass. Independent review found two already-stale nixos-stage
instructions (a refusing archive builder and a removed installation heading);
both now point to consumer-owned archive creation and installation. Its actual
copy/validation behavior is unchanged. Consumer info's writes are not claimed
removed in this loop; they are the next candidate.
