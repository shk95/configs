# Report: select CI suites by change effect

kind: report
spec: docs/work/repository/ci-effect-selection/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Repository fixtures cover docs, lock, modules, payloads, deletion, cross-scope rename and shared dispatch inputs. Replaying #392's actual six-file diff selects no suite while retaining Unix-like ownership; #408's lock diff selects the Unix-like suite. Workflow review confirms global scans keep ownership outputs. Hosted run 36222023513 selected all three suites for the shared CI change. |
| AC2 | verified | Repository fixtures reject unknown paths, malformed input, failed selection/scans, skipped or cancelled selected jobs, invalid booleans, unselected jobs running, native stack metadata and mismatched/layer event bases. Invariant and work checks pass. |
| AC3 | verified | Local repository suite and both commit/push hooks passed on 2026-09-26. Hosted [run 36222023513](https://github.com/shk95/configs/actions/runs/36222023513) passed classification, repository fixtures, global scans, Unix-like and native Windows jobs, and Required checks on 68cca35654031e90cac1890c3eddb021d99964e3. Manual prose and diff review found no account or machine identifier introduced by this change. |

## Limits

The CI mode narrows by documentation versus executable inputs, not by a full
dependency graph. Platform payload changes still select the whole native suite.
Shared CI machinery deliberately exercises unrelated platforms to verify its
routing. Native stacked PRs fail before selection; supporting them requires a
separate trunk-range and history-policy change. Cross-run reuse is absent, so
PR and push checks can repeat. No deployment or real-host readiness is claimed.

Documentation-only production execution has not yet been observed on the new
workflow in dev. The documentation optimization evidence above is deterministic
fixture coverage and replay of the historical diff, not a production timing
claim. A documentation update on this same PR still selects all suites because
its cumulative diff contains CI machinery; prior runs are not reused.

## Adoption and integration

Adoption prerequisite: [PR #416](https://github.com/shk95/configs/pull/416), then
[PR #413](https://github.com/shk95/configs/pull/413). Both branches were authored
independently from dev. Preserve the parent's session operator mapping, MSYS
scan, cask diagnostic and final session-test invocation when combining the
repository fixtures; retain one work-session path in classifier and selector.
The parent's integration rationale and this change's CI architecture paragraphs
are complementary. The integration session validates the combined result and
owns dev admission. This report records the implemented and verified increment,
not a claim that either PR has merged or that combined-parent CI has run.
