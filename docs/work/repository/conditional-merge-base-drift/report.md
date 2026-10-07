# Base-drift conditional merge verification
kind: report
spec: docs/work/repository/conditional-merge-base-drift/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | The focused suite exercises clean 1- and 3-merge chains and refuses a 4th update, an extra source commit, a malformed parent chain, conflicts, and a non-deterministic tree. The real Git graph recovery fixture preserves the original source SHA. |
| AC2 | verified | The A-to-B writer fixture submits CI evidence with current base B and the exact integration head; stale-base artifact identity is refused. The recovery fixture requires exact CI for actual merge parents after dev advances again. |
| AC3 | verified | Fixtures verify `expected_head_sha`, conflicting-tree refusal before update, an ambiguous response recovered from the remote head with no repeated PUT, latest failed Required checks stopping an update, and the 60-minute deadline refusing further writes. |
| AC4 | verified | Fixtures refuse master base movement without an update and check strict protection behavior. The implementation does not call the branch-update endpoint for master. |
| AC5 | verified | Fixtures and workflow inspection verify accepted-revision safety-path checks, a second preflight after queueing and before App token minting, PR rechecks on updated heads, and candidate CI has no writer credentials. The App token is used only by the writer; actual GitHub token-triggered CI behavior remains a separate live qualification item in the repository DoD. |
| AC6 | verified | Repository parent reviewed the complete staged implementation and policy in the execution lane tracked by issue #535. Staged checks passed: `work --staged` (43 items, 39 pairs), invariants (79 registered, 0 pending, 0 untagged), classification, design citations, records, provisional, domain reads, hygiene, and cached diff check. `tool/configs test` passed 17 release and 28 conditional-merge fixtures. No live update, merge, App-trigger qualification, or enablement is claimed. |

The original 19 fixtures and policy evidence in the initial conditional-merge
report predate this follow-up and do not verify its base-drift criteria. The
current focused command is
`nix shell github:NixOS/nixpkgs/151fa4e8ddfdd8dd25d945ad94ed54a13de9f6e4#python3 --command python3 -B tool/version-control/test-conditional-merge.py`;
it passes 28 cases. The complete `tool/configs test` suite passes 17 release
and 28 conditional-merge fixtures. The remote dispatch/merge qualification is
unperformed and unauthorized; no live branch update, merge, remote enablement,
or qualification is claimed. The repository Definition of Done retains actual
App-trigger and protected-merge qualification as a prerequisite to any future
enablement.
