# Minimal configs reconstruction: report
kind: report
spec: docs/work/repository/minimal-reconstruction/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review: remote archive/reconstruction-20261005-dev = fc2e1ab and archive/reconstruction-20261005-master = c98ce7d; consumer pin c76752d is reachable. Local snapshot preserves eight worktrees, index/rebase state and four stashes, with bundle verification and 9,335 checksums; notes excluded. Both shared refs adopted verified source 98ba4ef; original protection settings were restored and read back unchanged. Historical tag objects and consumer pins remain preserved. |
| AC2 | verified | Review: recovered domain source and fixtures are published at unixlike-v1.0.0 and windows-v1.0.0, both targeting adopted source 98ba4ef. Their annotations distinguish provider evaluation/build/native evidence from deployment. Domain reports retain pre-publication fixture checkpoints; current remote evidence is in Actions/annotations. No host adoption, activation or Apply. |
| AC3 | verified | Fixtures/dispatch: old operating suites are absent; evaluation coverage calls the core and independent suites run once (9 to 1). Repository fixture isolation and the native retired-capture guard are retained. Master promotion retains full PR CI and actual merge identity checks while redundant master push CI is removed; dev push coordinator reentry stays. Remote CI is authoritative in Actions/PRs; procedures no longer require a result-copy commit. |
| AC4 | verified | Bounded Git/API fixtures cover permitted patches, source/check identity, stale approval, immutable/conflicting tags, missing-tag-only recovery, lost-source stop and remote confirmation after lost create/merge responses. Workflow actionlint passed. The independent astra/high source review closed seven concrete defects; 14 bounded Git/API regression cases and actionlint pass. Matching-source checks and maintainer Environment review admitted the actual initial writer; both annotated tags were confirmed against their immutable source/declarations. Normal-path operation remains in AC5. |
| AC5 | pending | Review: exact source 98ba4ef passed matching-system/native gates, both refs adopted it and original protections were restored. Initial Environment-reviewed publication succeeded with the existing credential. Manual/CI continuation is enabled, schedule remains off. The bootstrap approval request reached the maintainer GitHub notification inbox (approval_requested, WorkflowRun); email delivery is not claimed. Normal PR/promotion operation and scheduled evidence remain open. |
