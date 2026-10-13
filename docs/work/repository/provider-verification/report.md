# Provider verification adjustment evidence
kind: report
spec: docs/work/repository/provider-verification/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Full tool/version-control/test exited 0 under locked Python, including effect selection and the stable gate. CI invokes the complete Unix-like suite once beside format/lint; Justfile wiring belongs to the companion Unix-like change. |
| AC2 | verified | Twenty-one release fixtures passed. New annotations report provider-owned artifact builds and no host runtime. Existing-publication fixtures cover old/current formats, missing evidence, altered metadata, wrong targets, duplicate/conflicting fields including indentation and unexpected host blocks. New-write confirmation rejects old evidence after an ambiguous write. |
| AC3 | verified | The combined corrected-source snapshot passed invariant registration (76), domain reads, design citations, hygiene, records, provisional registry and both work-item checks. Reviewed architecture, contributor workflow, doctor and README; the older CI decision now points to its replacement. |
| AC4 | verified | Initial publish lookup recognizes complete current or previous writer forms without writes. Post-write checks remain current-format-only. Full repository fixtures passed; a final targeted run of all 21 release fixtures passed after tightening indented-field conflict detection. |

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
