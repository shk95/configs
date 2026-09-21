# Report: reconsider CI with the installed x86_64 headless guest

kind: report
spec: docs/work/repository/ci-headless-runtime/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Required pull-request run [`35571092957`](https://github.com/shk95/configs/actions/runs/35571092957) passed on the hosted KVM runner with the branch caught up to `dev`. The full required workflow took 8:30, the Unix-like job 8:06, and `unixlike/tool/checks/test` 3:01. |
| AC2 | verified | `docs/policy/decisions/repository/ci-evidence-without-hosted-runners.md` accepts the measured test on the existing required job and states its new review conditions; `docs/work/roadmap.md` records the judgement as done. The maintainer selected this direction on 2026-09-21, and the repository policy, work and invariant checks pass for this increment. |

## Evidence boundaries

The Unix-like report records evaluation, build and booted runtime evidence for
the test itself. This report records the hosted affected-dispatch result and
the repository policy judgement. Neither one upgrades the installed VMware
guest's separately recorded native runtime, activation or rollback evidence.
