# Conditional merge verification
kind: report
spec: docs/work/repository/conditional-merge/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Fixtures and policy checks pass: the conditional-merge suite passes 19 cases; operator, workflow, worker handoff and integration wiring retain the existing role boundaries. Parent review approved the final diff. The pull-request CI lane is delivery evidence, not a substitute for these policy/review lanes. |
| AC2 | pending | Fixtures: successful orchestration checks the frozen SHA and makes one merge request only after the exact-source gate. Affected dispatch: pending; no live protected merge was authorized. |
| AC3 | pending | Fixtures: changed head/target, Draft/fork/stack ancestor, blocker, CI failure/superseding run, protection and timeout refusals are covered locally. Affected dispatch: pending. |
| AC4 | pending | Fixtures: retained queue configuration and target serialization are checked; master reuses the input-patch writer group. Affected dispatch: pending live concurrent-writer qualification. |
| AC5 | pending | Fixtures: ambiguous dispatch/merge is not retried, cancellation refuses, expired merged requests recover without another write, and post-merge audit failure remains distinct. Affected dispatch: pending live recovery qualification. |
| AC6 | pending | Fixtures: strict protection audit passes for both branches and refuses simulated loose master protection. Review: writer remains disabled; dev-only environment restriction and target-move race are not qualified. Affected dispatch: pending. |

The local fixture command is
`nix shell github:NixOS/nixpkgs/151fa4e8ddfdd8dd25d945ad94ed54a13de9f6e4#python3 --command python3 -B tool/version-control/test-conditional-merge.py`;
it passes 19 cases. The read-only remote audit passes with strict Required
checks on both `dev` and `master`. This is protection-state evidence, not a
workflow dispatch or protected-merge qualification.

`tool/configs test` passes under the pinned Python runtime: 17 release fixtures
and 19 conditional-merge fixtures pass. The plain host invocation cannot find
`python3`; no host runtime was installed or changed. The pinned `actionlint`
parser does not yet recognize GitHub Actions `concurrency.queue: max`; GitHub
supports that syntax, and the workflow source follows its documented form.
Staged policy checks
pass: `work --staged`, `invariants` (79 registered, none pending), `records`,
`design-citations`, `provisional`, `domain-reads`, `hygiene`, and
`git diff --cached --check`.

The `merge-control` environment, dev-only deployment restriction, actor
allowlist and dedicated writer credential have not been created or configured;
`CONFIGS_MERGE_ENABLED` remains unset or zero. No live merge or target-move
race qualification is claimed. Actual target qualification requires separate
explicit merge authorization; retain these report rows as pending until those
remote lanes run.
