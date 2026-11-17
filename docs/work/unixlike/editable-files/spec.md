# Writable configuration files with generation-relative backups
kind: spec
date: 2026-11-15
scope: unixlike
status: approved
review-by: 2026-12-15

Implement the maintainer-selected per-file opt-outs in the selected linked
workspace. Preserve Nix source ownership and normal symlink deployment for
unselected and future files. Commit the prepared result to the topic only;
master integration and consumer adoption/activation are separate operations.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Select exactly the named Zellij, Ghostty and Paneru files and ten current WezTerm files, preserving theme/future-file defaults and both Paneru XDG targets. | evaluation |
| AC2 | Preserve existing contents as sequential incoming-relative diffs with retained baselines, then deploy writable regular files; refuse unsafe inputs and preserve originals on backup failure. | native runtime |
| AC3 | Integrate read-only preflight, dry-run-safe placement, callbacks and directory-link migration with Home Manager, and pass the relevant provider checks. | evaluation, build, native runtime |
| AC4 | Record the policy, exact selection, evidence boundaries and operator implications without merging master or activating a host. | review |

## Delivery amendment — 2026-11-17

The maintainer imported the topic result into the current master working tree,
requested compatibility corrections and provider-internal ownership checks,
then explicitly authorized committing the complete prepared change there.
This extends the original topic-only delivery boundary to a local master source
commit. Publication and consumer adoption/activation remain separate operations.
