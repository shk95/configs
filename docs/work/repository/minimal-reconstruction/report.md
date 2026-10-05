# Minimal configs reconstruction: report
kind: report
spec: docs/work/repository/minimal-reconstruction/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review: remote archive/reconstruction-20261005-dev = fc2e1ab and archive/reconstruction-20261005-master = c98ce7d; consumer pin c76752d is reachable. Local snapshot preserves eight worktrees, index/rebase state and four stashes, with bundle verification and 9,335 checksums; notes excluded. Shared refs/protection are unchanged. |
| AC2 | pending | Domain source and required fixtures are recovered in their reports. Final matching-system build and native Windows CI remain endpoint gates; no host adoption or deployment. |
| AC3 | verified | Fixtures/dispatch: old operating suites are absent; evaluation coverage calls the core and independent suites run once (9 to 1). Repository fixture isolation and the native retired-capture guard are retained. Remote CI is authoritative in Actions/PRs; procedures no longer require a result-copy commit. |
| AC4 | pending | Bounded Git/API fixtures cover permitted patches, source/check identity, stale approval, immutable/conflicting tags, missing-tag-only recovery, lost-source stop and remote confirmation after lost create/merge responses. Workflow actionlint passed. The independent astra/high source review closed seven concrete defects; 14 bounded Git/API regression cases and actionlint pass. Current endpoint CI remains the separate remote gate. |
| AC5 | pending | Automation remains off. dev/master adoption, protection restoration, credential/Environment settings, actual notification and scheduled operation belong to the concrete cutover, after exact source checks. |
