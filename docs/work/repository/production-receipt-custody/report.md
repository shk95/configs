# Report: source-bound production receipts and independent review custody
kind: report
spec: docs/work/repository/production-receipt-custody/spec.md
status: pending

## Planning return, 2026-10-04

Root prepared this design child from dev 978f999c827ea78e3d33462bec928b53f1c4b046.
Independent read-only review distinguishes exact observed Actions checks from
required human review, representative native provenance and template pairing.
The bounded observed candidate intentionally refuses unsupported review receipts.
Those production gaps require an accepted custody design before source pickup.

Review-only GitHub custody is an option, not an adopted endpoint or workflow.
Official review-history fields do not establish approval timestamps, attempt/job
binding or dispatch input bytes. Current Environment policy is not historical
hold evidence. Source-derived title binding, alternatives and actual hold proof
remain to decide. No source, packet issuer, Environment or operation was changed.

Sources examined by the independent reviewer:

- [Review history](https://docs.github.com/en/rest/actions/workflow-runs#get-the-review-history-for-a-workflow-run)
- [Environment metadata](https://docs.github.com/en/rest/deployments/environments#get-an-environment)
- [Workflow run-name](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#run-name)
- [Required reviewers](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)

Parent manual/scheduled acceptance remains pending. Root owns continuation.
Independent read-only review of this pair found no premature authority or API
observation claim. Platform-created deployment metadata is an explicit design
consideration, separate from forbidden job operating writes. All design criteria
remain pending; reviewed planning delivery does not accept the proposed mechanism.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | Producer categories identified; exact grammar and provenance remain to review. |
| AC2 | pending | GitHub proposal limits identified; narrow authority and alternatives remain unresolved. |
| AC3 | pending | Original projection versus next protocol and endpoint authority remain undecided. |
| AC4 | pending | Separate design/source/operating gates identified; adoption and source pickup not complete. |
