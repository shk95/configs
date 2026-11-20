# Separate reusable program settings from host preferences
kind: spec
date: 2026-11-20
scope: unixlike
status: approved
review-by: 2026-12-04

Use the existing Unix-like provider and linked host checkouts. Keep provider
install and integration defaults. Move selected user preferences to the host
repository. Combine native Nix options and select complete host application
files through the existing options. Use each host's previous evaluated
configuration as the migration baseline.

Amended 2026-11-20. AC2 requires the same final configuration values and
the same host and Home Manager output derivations with inputs held fixed.
The Mac's local Paneru edits remain on the host.

Amended 2026-11-20. AC2 permits the Darwin derivation change caused by
Karabiner switching to host-owned source documents. Prove the applied
Karabiner and hotkey values, generated home files, and the rest of the
activation script match the baseline.

| Scope | Work |
| --- | --- |
| Public environment | Retain install, shell, desktop, compatibility and validation behavior with minimal public application defaults. |
| Host environment | Preserve the eight declared hosts' evaluated settings using explicit host modules. |

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Provider and hosts own their respective options and whole application files. Public defaults contain reusable behavior. | review, evaluation |
| AC2 | All eight hosts preserve their effective configuration values and generated files with the existing pin and with the local provider. Output derivations match except for the Darwin Karabiner source change described above. | review, evaluation |
| AC3 | Checked provider fixtures and applicable native configuration parsers accept the changed files and their ownership. | evaluation, build, native runtime |

Working-tree delivery suffices. Host activation, publication, and pin adoption
remain separate operations.
