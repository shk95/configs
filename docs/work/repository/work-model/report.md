# Report: plan and verify work in documents, and keep issues for execution state

kind: report
spec: docs/work/repository/work-model/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC2 | verified | `tool/version-control/test` at b49e0fb, in the unit tagged `INV repository/work-spec-has-report`: `work` refuses a spec without a report and a report without a spec (W2); a criterion with no row and a row with no criterion (W5); `done` while a criterion is not verified (W6); a spec whose scope is not its directory's and one that lists two (W3); and, with `--staged` and with `--range`, a criterion rewritten, a criterion whose lanes were weakened and a criterion removed after its report existed, as well as an amendment that names another criterion (W7). It accepts a pending pair, a carried `study` with two scopes, `done` with every row verified, `abandoned` with the unmet criterion stated, the same changes under a dated amendment naming them, and a first commit, which has no base. Mutation runs, each restored: switching off the W3 scope check, the W5 missing-row check, the W6 done check, the W7 rewrite check, the W7 removal check, or accepting any amendment, each fails the unit. |
| AC3 | verified | `tool/version-control/work` at b49e0fb: 7 work items, 3 specs paired with a report, this one and `docs-layout` included; `--range 790ca6c HEAD`, which spans the AC12 and AC4 amendments of `docs-layout` and the amendments here, passes. It runs in `.githooks/pre-commit` with `--staged` and in the CI scan job with the range under test. |
| AC4 | pending | |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | verified | `tool/version-control/test` at b49e0fb, in the unit tagged `INV repository/design-outside-authority`: a work item's path is refused in `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `docs/policy/architecture.md`, an invariant entry, a script under `tool/`, `.githooks/`, `.github/`, `unixlike/` and `windows/`, the `README.md` line also naming the format contract beside it; it is accepted in `docs/status/`, `docs/README.md`, `docs/work/`, and, as before, in the decision, candidate and provisional inlets and the classifier's path table; the area's `README.md` and `roadmap.md` are accepted from `AGENTS.md`, an invariant entry and a script. Mutation runs, each restored: stripping every work path from a hit, removing the `docs/status` exclusion, or no longer excusing the area's files, each fails the unit. |
| AC8 | pending | |
| AC9 | pending | |
| AC10 | pending | |
