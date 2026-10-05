# Minimal configs reconstruction
kind: spec
date: 2026-10-05
scope: repository
status: approved
review-by: 2026-10-20
issue: #515

## Implementation

Recover required functionality from a886934 without inheriting the old operating system or AC12 as a whole. This is the active entry point; the Unix-like and Windows minimal-reconstruction pairs describe the domain outcomes. Refs #515.

The maintainer authorized a fixed-base, multi-scope assembly branch and preservation refs. Commits retain their owning scopes. This branch is checked directly and is not merged into old dev. dev/master replacement, protection changes and live enablement remain a separate concrete cutover step after endpoint verification. Normal PR promotion resumes afterward.

Initial domain versions are independently 1.0.0. Automatic input updates admit only nixpkgs, home-manager, nix-darwin and nixos-wsl. The local refresh default may be broader. Automatic patch declarations may update the exact previous release basis, version and fixed refresh description; compatibility/approval policy is not mutable input.

Keep only permitted change scope, current candidate/check/approval agreement, credential separation, immutable tags and remote confirmation after ambiguous writes. Recover one unfinished promotion before admitting the next. Lost source identity requires an explicit original SHA. No journal, retained runtime, object transport, receipt, global fencing or complete notification deduplication.

Order: preserve; recover domains; remove observed CI waste; connect automation off; check exact N; review cutover; verify normal and scheduled operation. 05/06/07 Asia/Seoul remain refresh, promotion opening and refresh-wait cutoff. Mandatory checks and approval still apply after cutoff. First publication uses explicit N; normal publication uses actual promotion M. Fixtures cover failures; live evidence covers normal operation, permissions, notification and schedule.

Donors and old work documents are evidence, not inherited acceptance. No host pin adoption, activation or Apply. Remote CI results stay in Actions/PRs and do not require another report-only push. Stop a write for conflicting refs/tags, stale candidate/approval or lost original SHA; do not add a recovery framework.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Previous source and unfinished work remain recoverable. | review |
| AC2 | The required domain features are recovered through the linked domain reports. | review |
| AC3 | Obsolete suites, repeated independent checks and CI-result follow-up commits are removed. | fixtures, affected dispatch |
| AC4 | Bounded automation validates current candidates, isolates credentials and resumes one publication without mutable tags. | fixtures, affected dispatch |
| AC5 | The exact endpoint is checked and the cutover and live scheduled evidence are reported separately. | review |
