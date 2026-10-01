# Classify retained Unix-like migration history
kind: spec
date: 2026-10-01
scope: repository
status: approved
review-by: 2026-10-15
issue: #472

## Outcome and pickup

Root plans and owns this repository-only prerequisite to production qualification
#471. Its approved provisional revision is published before Ready handoff. Use
current dev and the reviewed plan snapshot separately. One repository PR updates
classification and its immutable semantic-package digest; no domain output changes.

The current dev tree retains a Nix-only .vscode/settings.json pointing to the removed
root flake. Current master retains the historical Unix-like root tree. The original
master classifier identifies flake.nix, flake.lock, assets/, modules/, tool/checks/
and tool/darwin/ as Unix-like. Restore only those historical namespace answers and
the exact Nix editor settings path under a registered temporary measure. Unknown
root files and unrelated .vscode files remain refused. This is history/migration
classification, not permission to author new root-domain material. A separate
Unix-like lane relocates the unchanged settings into unixlike/.vscode/ after this
prerequisite integrates. Do not read scratch notes or change release inputs.

## Verification and retirement

Exercise positive old/new paths and negative similar prefixes, and run repository
fixtures, policy and dispatch checks on Linux and native Git-for-Windows. Update the
exact eight-file semantic manifest after changing its classifier. Register the
measure with a review date and retire it only when master no longer retains any
legacy root files or the old editor path; source integration is not promotion.
Checkpoint/replan if another owner exists or ownership/history contradicts these
observations. No credentials, live operating effects, promotion, tag or activation.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Known historical Unix-like roots and the exact Nix editor settings classify as unixlike; unrelated and similar paths refuse. | review, fixtures, policy checks, affected dispatch |
| AC2 | Temporary history classification has a bounded review and observable retirement condition; its semantic package digest is exact. | review, fixtures, policy checks |
