# Provider verification adjustment evidence
kind: report
spec: docs/work/unixlike/provider-verification/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Complete provider suite exited 0 on aarch64-darwin after review corrections. All seven exported synthetic toplevels evaluated without host closure or VM realization. Native refusing-builder fixtures passed on Darwin and ARM Linux. |
| AC2 | verified | Complete suite passed 71 finite contract cases, eleven independent constructor/system/environment toplevels, external consumers, payload and provider-tool fixtures, and forward/reverse import-order checks. Format and lint passed. Payload/lint tools use the locked input; full toplevel traversal is no longer duplicated in flake-test. |
| AC3 | verified | Three focused Zellij source-patch checks passed on aarch64-darwin. Five generated-file positive/refusal checks passed on native aarch64-linux. Reviewed current policy and definition of done: host closure realization, boot, sessions and activation belong to consumers. |
| AC4 | verified | The semantic matrix forces eleven advertised combinations independently of example names. Detector fixtures accept a provider without examples and reject an ARM-only toplevel error while its state version remains readable. Strict-family fixtures refuse each missing family on Darwin and ARM Linux. Native ARM Linux built Niri default/repeat and Noctalia positive checks plus parser-specific malformed KDL/TOML refusal checks; x86_64-linux focused-check derivations evaluated without building. |

## Independent review and correction

On 2026-10-13 Sol 6.1 medium and Astra medium independently reproduced the
previous-writer publication retry regression. Astra also found lost native
validation of generated Niri/Noctalia files. Both noted that state-version
probes do not preserve ARM toplevel coverage. Original passing tests did not
exclude these gaps; this report records the corrected source and added
refusal fixtures rather than treating the initial pass as final evidence.

## Evidence boundary

Evaluation: seven exported examples and eleven finite advertised API
combinations passed on aarch64-darwin. All x86_64-linux focused-check derivations
also evaluated; their artifacts were not built locally.

Build: three source-patch checks passed on aarch64-darwin. Five generated-file
checks passed in an already-running native aarch64-linux NixOS/OrbStack machine,
using a copied temporary source snapshot and Nix 2.34.8. Positive checks invoke
the pinned Niri/Noctalia parsers explicitly on actual generated sources, so
removing a generator validation flag cannot silently remove this evidence.
Refusal logs named KDL parsing and TOML table-header syntax. No host closure or
home activation package was built.

Native runtime: parser/CLI execution occurred within artifact checks; no host
boot, graphical session or deployed consumer runtime is claimed. Activation
and Windows Apply were not performed. Linux x86_64 CI and native Windows CI
were not run. Guard cases skipped on Darwin do not prove other platforms.

The copied Linux snapshot had no configured Git hooks. Doctor confirmed Nix
capabilities but reported that clone-specific gap. It was used only for reading
and artifact builds, with no setup/authentication, kernel-global change or Git
publication. Primary dev and master were not advanced.

Source preparation and local verification are complete. Changes remain
uncommitted in separate linked worktrees after the earlier authorized master
reflection. Integration, push and remote CI were not performed; local delivery
is not claimed. Existing tag objects remain unchanged.

## Local evidence files

- /tmp/configs-provider-suite-fixed.log: complete provider suite.
- /tmp/configs-provider-repository-suite-fixed.log: complete repository fixtures.
- /tmp/configs-provider-release-final.log: final 21 release fixtures.
- /tmp/configs-provider-generated-artifacts-final.log: native generated-file builds.
- /tmp/configs-provider-linux-coverage.log: native Linux coverage detectors.
- /tmp/configs-provider-composition-matrix.json: eleven semantic toplevels.
- /tmp/configs-provider-x86-check-derivations.json: x86 focused-check evaluation.

## Retained verification

Contract, native-module extension and independently locked consumption fixtures
protect the API. Semantic witnesses protect finite advertised system/environment
selections; exported-example traversal protects the examples themselves. Payload
parsers, generated-file validators, owned scripts and internal composition/order
checks retain distinct evidence. Focused source transformations and generated
files need builds; host closure, boot and session qualification belong to
consumers. Template verification belongs to its own source and pin.
