# Local consumer development evidence
kind: report
spec: docs/work/unixlike/local-consumer-development/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | `unixlike/tool/checks/dev-host-test`: source filtering, new-file inclusion, snapshot tampering/source-change refusal and independent linked-checkout state. Review: all connection, recipe and receipt writes use the checkout's Git metadata; public fixtures contain synthetic selections only. |
| AC2 | verified | Real Nix CLI fixture evaluates a changed provider differently from its pinned version while preserving consumer flake and lock bytes. A real consumer NixOS toplevel also evaluated against the current local provider without a source/lock edit; no consumer identity is recorded here. |
| AC3 | verified | Consumer adapter fixtures cover native target/account/package refusal and matching-account acceptance, frozen-source activation arguments and active-generation comparison. Provider fixtures invalidate receipts before failed activation and require an actual functional-check note. Activation calls are intercepted in these fixtures; actual native activation is separately recorded under AC8. |
| AC4 | verified | Provider fixtures cover a read-only plan, changed-recipe refusal, exact released-source comparison, pinned-closure mismatch, complete orchestration and idempotent retry, and partial-adoption resumption without repeated provider publication. Review: publication runs only through local explicit argv procedures; repository audits and immutable remote identities are checked. Remote publication is fixture evidence only. |
| AC5 | verified | Just parses the development recipes and forwards spaced arguments intact. The provider development fixture suite, consumer adapter fixtures and existing consumer provider-input fixtures pass. Provider formatting/lint/composition checks pass; invariant, hygiene, provisional and design-citation checks pass using a temporary index, preserving the user's real index. Usage and protocol are documented in `unixlike/tool/dev-host/README.md`; no private consumer is needed by provider CI. |

Evaluation: synthetic override/pin evaluation, public constructor compositions
and all declared consumer outputs succeeded. Build: tiny synthetic fixtures,
provider artifacts and isolated consumer NixOS closures in both directions
succeeded. Native runtime: exact test-marker reads and active-generation checks
passed in three NixOS cases. Activation: the maintainer ran all three switches;
each restored the original running system and default profile and removed the
marker. This is marker smoke-test evidence, not a complete application test.

Promotion commits, tags and pushes exercised by integration tests belong to
disposable local repositories; production remote release/adoption/publication
was not performed. Hosted CI was not run. The consumer adapter and checks are
prepared in the adjacent selected checkout. Production connection identities,
recipes, source snapshots and native receipts remain private in Git metadata.
Configure actual publication procedures separately before production promotion;
provider automation does not invent a general-development release writer.

Manual review found no actual account names or private host identifiers in new
public prose. The new invariant's positive and negative fixtures were reviewed
against its declaration; the actual generation checks remain consumer-owned.

## Follow-up evidence — 2026-11-04

| ID | State | Evidence |
| --- | --- | --- |
| AC6 | verified | Two subprocess-only provider integration cases pass with real Git/Nix, exact annotated fixture releases and local bare remotes. They cover changed-provider delivery, consumer-owned extraction with identical built output, stale receipt refusal, read-only planning, exact pinned promotion and repeat execution without duplicate publication. Activation and audit are explicitly synthetic. |
| AC7 | verified | The consumer native runner completed both directions in isolated copies: three successful development/local-pin NixOS closure comparisons, identical host-owned/extracted system store paths, and unchanged original source/index/HEAD/branch/status fingerprints. The initial run requested no switch; the final native run is recorded under AC8. Private receipts remain in the consumer's Git metadata. |
| AC8 | verified | Five consumer recovery fixtures pass: exact active/profile restoration checks, absent-marker check, activation attempted despite profile restoration failure, partial activation/interruption recovery, successful runtime/restoration and failed recovery not marked restored. The maintainer then ran the opt-in native test: all three cases report evaluation/build, local-pin equality, activation, marker runtime and restoration success; extraction preserves the complete store path. The agent independently checked the original active system/default profile and absent marker, and matched current original source/index/HEAD/branch/status to the receipt's identical before/after fingerprints. |

The amendment authorizes implementation commits after the requested tests.
Native acceptance is complete. Implementation and test code are the accepted
source changes; disposable marker modules, connection identities, runtime
receipts and local paths remain outside the commits. Publication/release is not requested.

Follow-up fast checks: 15 provider fixtures (including the two real-process
integration cases), 8 adapter fixtures, 5 native recovery fixtures and 5
provider-input fixtures pass, totaling 33. All declared consumer host outputs
also evaluate against the existing committed provider pin without overrides.
These foreign evaluations are not native builds or runtime evidence.

The first full provider run found an existing Karabiner prerequisite fixture
failure: this NixOS environment wraps `/bin/sh` and reinserts Nix into an
intentionally empty PATH. The unchanged HEAD fixture reproduced the failure in
an independent source archive. The fixture now invokes the selected interpreter
explicitly for the empty-PATH guard only, preserving its missing-tool condition;
the focused Karabiner suite passes. Production Karabiner behavior is unchanged.
The remaining provider suites pass when resumed individually: flake contract,
composition, evaluation coverage, prerequisite, import-order and final provider
evaluation. The prerequisite suite reports its existing minimal-PATH skip
because this wrapped shell can reach Nix; that skip is not missing-tool evidence.
Provider artifact builds ran; foreign-system checks omitted by Nix remain
unverified as native builds. The initial `just check` failure is retained in
run output rather than represented as an uninterrupted successful command.

The final development wrapper also passes all 15 fixtures with Just absent
from the caller PATH, using only the locked Nix `just.out` output. This checks
CI's ability to run the integration cases without a preinstalled Just.
