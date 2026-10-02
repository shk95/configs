# Reconsider CI with the installed x86_64 headless guest

kind: spec
date: 2026-09-21
scope: repository
status: approved
review-by: 2026-10-05
issue: #327

Agreed with the maintainer on 2026-09-21 after the VMware guest completed its
native runtime, activation and rollback evidence. The installed guest now
declares the account, ssh service and firewall behaviour named by the CI
decision's second `reopen-when` condition.

## Problem

The merge gate evaluates the headless account, ssh and firewall declarations,
but it does not boot them together. Evaluation can reject a wrong option value;
it cannot show that a key reaches the account, that password and root logins
are refused, or that the running firewall admits ssh while refusing another
listening port. The earlier decision deferred that cost until an installed
x86_64 guest gave such a test real behaviour to assert. That condition is now
met, so leaving the decision pending would discard its own review trigger.

## Decisions

### Measure one minimal test before changing the decision

The Unix-like increment adds one `runNixOSTest` flake check around the real
shared and headless module classes. It retains the existing evaluation fixture,
uses one guest plus a network namespace rather than two guests, and puts every
test credential into the disposable machine after boot. The test must run
without assuming KVM because the hosted runner does not promise it.

The local TCG run establishes feasibility and an initial time, memory and store
cost. The pull request's required Unix-like dispatch then establishes whether
the same check is practical on the actual hosted merge-gate runner.

### Reuse the required Unix-like dispatch

The existing Unix-like job already runs `nix flake check` through
`unixlike/tool/checks/test`. A flake check therefore becomes required without a
new runner or a workflow edit. If the hosted run exposes a missing prerequisite
or an unacceptable cost, that result is recorded before the CI decision is
changed.

### Close the judgement where it became pending

After the hosted run, one repository increment records the measured result in
the CI decision and changes the pending roadmap judgement to its outcome. The
record states evaluation, booted runtime and affected-dispatch evidence at
their actual strengths; it does not turn the test into VMware native-runtime or
activation evidence.

## Increments

1. Publish this plan and its pending report for review.
2. Complete the linked Unix-like work item
   `docs/work/unixlike/headless-runtime-ci/` and observe its required hosted
   dispatch.
3. Record the decision, roadmap result and terminal report in one repository
   pull request.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The required Unix-like pull-request dispatch runs the booted headless check successfully on its hosted runner, with its wall time recorded. | affected dispatch |
| AC2 | The CI decision records the maintainer's judgement from the local and hosted measurements, and the roadmap no longer calls that judgement pending. | policy checks, review |
