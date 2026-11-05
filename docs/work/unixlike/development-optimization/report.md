# Unix-like development optimization results
kind: report
spec: docs/work/unixlike/development-optimization/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Baseline Just JSON signatures/dependencies/privacy and aliases match. Five real Just fixtures prove early refusals, unchanged source and active delegation; independent review confirms dead-body removal and utility retention. |
| AC2 | verified | Real Just argv/cwd spies in a path with spaces prove named/all intent boundaries, literal hostile input, option/empty refusal and the owning Unix-like flake. |
| AC3 | verified | Six CLI/Git/lock query tests and corrected promotion-plan evidence pass with all 21 dev-host tests; independent review accepts the 35-line implementation increase and preserved mutator coordination. |
| AC4 | verified | Format/lint, the full twelve-suite provider run and seven toplevel evaluations exit 0; independent review accepts the source. Local commits are scope-pure; master and actual input/release files are unchanged. Native/host/deployment limits are stated below. |

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

## Loop 2: consumer info without initialization

The baseline constructor creates the Git-local development directory and the
common command path opens/truncates an exclusive lock even for info. Move
creation to explicit mutators; info uses an existing shared lock, or reports
uninitialized without creating anything. Malformed/uncoordinated state refuses
without repair. Git reads disable optional index refresh. No adapter, Nix,
host probe, new state file or provisioning capability is introduced.

Reuse the exploration's small implementation and six query tests, and correct
the existing promotion-plan evidence. Keep the existing consumer protocol,
application and promotion fixtures. This increases
implementation size to eliminate an actual implicit write and prerequisite:
an unconnected operator can inspect without first mutating state. A simple
existence test alone would allow reading concurrent writes; preserving lock
coordination justifies the small shared read/write lock helper.

## Final evidence and bounds

The narrow dev-host process exits 0 with 21 tests, including six new read-only
query cases (`/tmp/configs-optimization-unix-loop2-dev.log`). Independent Astra
high review accepts the locking/source changes; the author separately confirms
the process exit. The full provider run also exercises these cases and the five
Just cases, preserving the existing consumer protocol/promotion tests.

Compared with the baseline, implementation is 987 to 895 lines (-92): Just
removes 127, while the actual read-only info boundary adds 35. Test sources and
runners add 281 lines. The latter is a verification cost, not runtime reduction.
The recipe dump comparison preserves all 56 original interfaces and five
aliases; one private refusal helper is added. Info removes the implicit
initialization prerequisite, not an explicit user command. No operator timing
or total-context benchmark was performed.

No broader producer, provisioning or capability framework is necessary. A
lock-free existence check would weaken concurrent-state safety; keeping the
small shared/exclusive lock helper is proportionate. Topic commits are local,
independent of the repository topic, and not integrated into master. Actual
provider locks and release metadata stay at the baseline; disposable fixture
locks in test output are not source input updates. No host activation or Apply,
remote publication, or consumer adoption occurred. Prose review found no added
undeclared account/machine identity.

The complete `unixlike/tool/checks/test` process exits 0 (log
`/tmp/configs-optimization-unix-final-provider.log`): twelve fixture suites,
then flake validation and all seven synthetic home/NixOS/Darwin toplevels.
The prerequisite fixture reports its existing minimal-PATH skip because the
wrapped shell can reach Nix; this is not missing-tool evidence. The final
flake check reports zero runnable checks on x86_64-linux and omits incompatible
aarch64-linux/aarch64-darwin checks. No new native artifact-build evidence is
claimed from that step. A tiny real Nix fixture build exercises dev-host CLI
output handling; host closure builds, macOS/ARM runtime, activation and Apply
are unperformed. Format/lint and staged registry/work checks also pass.
