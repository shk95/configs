# Minimal configs reconstruction: report
kind: report
spec: docs/work/repository/minimal-reconstruction/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review: remote archive/reconstruction-20261005-dev = fc2e1ab and archive/reconstruction-20261005-master = c98ce7d; consumer pin c76752d is reachable. Retired local worktrees and stashes were preserved in the remote recovery record #518 before reclamation; they are not current pickup work. The initial adoption of original source 98ba4ef and its protection restoration are historical evidence in the original PR/Actions records. Historical tag objects and consumer pins remain preserved. |
| AC2 | verified | Review: recovered domain source and fixtures are published at unixlike-v1.0.0 and windows-v1.0.0, originally targeting source 98ba4ef, before the authorized unconsumed-tag reissue. Their annotations distinguish provider evaluation/build/native evidence from deployment. Domain reports retain source/fixture evidence; exact current revision proof is in Actions/annotations. No host adoption, activation or Apply. |
| AC3 | verified | Fixtures/dispatch: old operating suites are absent; evaluation coverage calls the core and independent suites run once (9 to 1). Repository fixture isolation and the native retired-capture guard are retained. Master promotion retains full PR CI and actual merge identity checks while redundant master push CI is removed; dev push coordinator reentry stays. Remote CI is authoritative in Actions/PRs; procedures no longer require a result-copy commit. |
| AC4 | verified | Bounded Git/API fixtures cover permitted patches, source/check identity, stale approval, immutable/conflicting tags, missing-tag-only recovery, lost-source stop and remote confirmation after lost create/merge responses. Workflow actionlint passed. The independent astra/high source review closed seven concrete defects; 14 bounded Git/API regression cases and actionlint pass. Matching-source checks and maintainer Environment review admitted the actual initial writer; both annotated tags were confirmed against their immutable source/declarations. Original normal promotion was observed through #517; rewritten-source CI and tag proof are separate. |
| AC5 | pending | Review: original source 98ba4ef passed native gates; original cutover and initial Environment-reviewed publication succeeded. #517 records normal protected promotion and schedules were enabled afterward. Approval requests reached the maintainer notification inbox; email is not claimed. Exact rewritten-source qualification stays in Actions/annotations, and an actual scheduled run remains unobserved here. |
