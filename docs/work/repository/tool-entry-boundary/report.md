# Report: separate operator commands from automation tools
kind: report
spec: docs/work/repository/tool-entry-boundary/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Fixtures: `tool/version-control/test` passed in the implementation commit `ee5035e` and the push gate, including argument and exit-status forwarding and refusal of an unknown verb without executing a target. Policy checks: the staged work, invariant, hygiene, domain-read, design-citation, provisional and secret scans passed. |
| AC2 | verified | Fixtures cover `tool/configs` routing and the selected check for its path. Independent review of the `ee5035e` diff found stale operator examples in current repository-owned documents; they were corrected before merge. The operator interface is documented in root guidance, current document indexes and the canonical workflow skill, with implementation scripts still owned by their scopes. Affected dispatch selected `repository:fixtures`; PR #405 `Required checks` passed before this report update. |
| AC3 | verified | Fixtures in `tool/version-control/test` check direct Windows internal calls in pre-push and CI, including immediate exit handling and the unavailable path. Review found no operational call from these paths to `windows/win-env.ps1`. Affected dispatch skipped Windows native CI for this repository-only PR; the Windows-scope PR #406 supplies native runtime evidence. |

## Evidence lanes

- Fixtures: `tool/version-control/test` passed locally at `ee5035e`, in its pre-commit hook and pre-push hook on 2026-09-26.
- Policy checks: `tool/version-control/work --staged`, `tool/version-control/invariants`, `git diff --cached --check`, pre-commit checks, and PR #405 policy scan passed.
- Affected dispatch: the selected local push check was `repository:fixtures`. [PR #405 CI](https://github.com/shk95/configs/actions/runs/36206730059) classified the change as repository, passed `Version-control policy` and `Required checks`, and skipped the Windows native job.
- Review: an independent Astra medium review inspected the complete PR #405 diff and CI on 2026-09-26, found current operator examples that still named internal scripts, and confirmed no functional routing defect. Those examples were corrected. Native behavior is reserved for Windows PR #406.
