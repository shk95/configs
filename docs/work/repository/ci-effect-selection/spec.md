# Select CI suites by change effect

kind: spec
date: 2026-09-26
scope: repository
status: approved
review-by: 2026-10-10
issue: #409

## Problem

Documentation-only PR #392 ran the Unix-like job for 13:02 (run
36109055733); lock refresh #408 ran it for 12:42 (run 36216060416).
Ownership alone selects a suite even when no executable input changed.
The maintainer approved effect selection on 2026-09-26.

## Decisions

Extend the existing selector with a conservative CI mode. Documents retain
ownership and global policy scans but select no platform suite. All executable
platform changes, including payloads, select that platform's whole suite.
Workflow, dispatch, classifier and stable-gate changes exercise all suites.
Other repository tooling selects repository fixtures. Invalid input, unknown
ownership, selection failure or unsupported stack events cannot pass the gate.
Native stacks are refused until trunk-wide selection and policy are proven;
a layer-only base is never accepted as integration coverage.

The repository maintainer owns the decision. The failure prevented is a false
green from skipped affected checks; the cost removed is unrelated execution.
Policy belongs in the existing effect-selection invariant and decisions;
deterministic selection belongs in dispatch and Actions, with positive and
negative repository fixtures. Parent work owns procedure, skills and current
status. No host output, activation, new runner or merge queue is introduced.

Rejected: narrowing arbitrary Nix modules without dependency evidence, copying
local payload shortcuts into CI, adding cross-run state or trusting a prior
PR result for a different merge tree. PR and push retain separate validation;
#408's roughly 13-minute PR and 12-minute push show the remaining cost, not
proof their results are interchangeable. Internal suite optimization is later
work in the owning domains.

## Increments

One repository PR carries the selector, CI and gate contract, policy amendment,
fixtures and this report. Publish Draft before implementation is complete;
mark Ready after native CI passes. The integration session merges separately.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Docs-only changes retain ownership and global scans without platform suites; real platform and shared dispatch inputs select conservative suites, including renames and deletions. | fixtures, affected dispatch |
| AC2 | Invalid selection, skipped selected jobs, failed scans and unsupported stack events cannot yield Required checks success. | fixtures, policy checks |
| AC3 | Repository fixtures and selected native jobs pass, with remaining performance and support limits recorded. | fixtures, affected dispatch, review |
