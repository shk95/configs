# Report: source-bound production receipts and independent review custody
kind: report
spec: docs/work/repository/production-receipt-custody/spec.md
status: done

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
consideration, separate from forbidden job operating writes. The following design resolution replaces those earlier pending observations.
Design verification does not deploy or certify the proposed mechanism.

## Design resolution, 2026-10-04

Root's study and typed-production-receipt-source spec/report make the design
pickup concrete. Independent operating_plan review checked them against actual
protocol-3 records/engine/transcript fields, loader global replay, Journal path
allowlist and Actions collector requirements. Eleven-field evidence projection
preserves original schemas; content-addressed private packets remove hash/run
self-reference and recover old custody independently of a mutable index.

Actual approved exact comment hash supplies narrow human acknowledgement;
workflow title alone and unobserved inputs supply none. Timestamp, historical
Environment policy and native execution truth remain unclaimed. Original template
ancestry/delivery and reviewed actual override-pair compatibility are distinct;
current provider pin need not equal candidate. Exact Actions runtime descriptors
require a reviewed producer contract or approved raw runtime records.

The source child assigns bounded readers/collector/review-only source and durable
adoption to one worker, keeps rules/semantic manifest/shared docs closure under
root, and orders positive/negative/local/native checks. Its initial review job is
statically disabled. Actual Environment IDs/hold, approval, packet/index maintenance,
genuine native/template evidence, baseline adoption and all manual/scheduled
operations remain separate unperformed gates. No source implementation is delivered.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review: root study and independent operating_plan analysis specify strict typed packet/index coverage, original provenance, tool/profile honesty and invalidation; genuine execution remains operator assertion. |
| AC2 | verified | Review: exact approved comment hash plus original sole-job attempt-1 source/reviewer/Environment observations define narrow custody; unsupported timing/input guarantees, actual hold evidence, reuse and alternative boundaries are explicit. |
| AC3 | verified | Review: actual records/engine/loader/Journal analysis supports transport-only original row projection and content-addressed restart; fixed anonymous endpoint/role scope, historical closure and next-protocol replan are enumerated. |
| AC4 | verified | Review: dedicated decision/invariant adoption, worker/root closure responsibilities, ordered source child and actual operator gates are specified. Policy checks: tool/configs work --working-tree passed both production-receipt-custody and typed-production-receipt-source pairs; staged/history/current-head delivery remain separate. |
