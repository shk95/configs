# Codex Work Cycle source separation
kind: spec
date: 2026-10-07
scope: repository
status: approved
review-by: 2026-11-07

## Outcome

Move the six tracked local role skills into Agent Rack's existing Work Cycle
package, refresh its stale remote-first extraction, and prepare configs for
operation without an installed replacement. Remove active Claude workflow
adapters. Preserve earlier import archives and local Context Bridge files.

Source basis: configs dev 4c72b000ad23b2a32c564c6f907192bd34f82870.
Destination basis: Agent Rack c3d238a2fec5c7e394a09b0470b370cec0a8e834.
Earlier uncommitted external-context cleanup is retained in this worktree.
Each repository owns its changes. No commit, push, installation or integration
is authorized by this source preparation.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The six tracked skills and three Claude workflow aliases leave configs; local Context Bridge data is preserved. | review, policy checks |
| AC2 | Configs instructions, ownership, current state and contributor procedures work without local role skills or an installed replacement. | review, policy checks, affected dispatch |
| AC3 | Agent Rack reuses Work Cycle with a pinned current-source archive, target-policy-driven local workflows, and Codex-only active distribution. | review, fixtures |
| AC4 | Both results remain uncommitted and installation, host discovery, publication and integration evidence are reported separately. | review |
| AC5 | Model-specific discovery rules are consistent with optional external skills, and task entry follows relevant current contracts without mandatory historical-context loading. | review, policy checks, affected dispatch |

## Verification

Use a disposable review index for configs policy checks, plus working-tree
spec/report preflight and changed-path dispatch. Validate Agent Rack manifests,
contained references and Codex-only packaging; run its structural refusal
fixtures and retained checkpoint fixtures. Compare imported skill bytes to
the pinned source and compare local Context Bridge hashes before and after.
Actual-model behavior verification is not required for this source preparation.
Installation and adoption are separate user-selected operations.

Amended 2026-10-07: AC5 records the two necessary findings of the independent
Astra high source review. AC1-AC4 remain unchanged. Retain existing project
tools; no runtime/model-use experiment is required. Align manual discovery
evidence and current decision pointers, then validate source documents only.

Authorization update 2026-10-07: after source preparation and independent
review, the maintainer requested local configs dev integration. This authorizes
the configs source commit, task topic branch and verified exact-SHA fast-forward
into local dev. AC4 records the earlier source-preparation boundary, not a
continuing prohibition on this authorized integration. Agent Rack remains
uncommitted. Push, installation, publication and deployment remain separate.

## Stop conditions

Preserve unrelated work. A changed source/destination or conflicting ownership
requires review before overwrite. Do not recreate a configs-local skill or
external-source pointer as a replacement connection.
