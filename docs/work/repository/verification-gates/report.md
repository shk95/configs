# Verification and publication gates report
kind: report
spec: docs/work/repository/verification-gates/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Local Git fixtures exercise full commit messages, merge-only paths and lock values, receiver-bound pushes and tag reachability. Gitleaks 8.30.1 refused synthetic credentials present only at a merge, in reverted side history, and at a root. Clean controls passed. The wiring fixture checks that CI invokes only incoming-mode audit and secret scans. |
| AC2 | verified | Local dispatch fixtures cover distinct selections for release declarations, the release workflow, Git for Windows fixture inputs and both Windows runtime declaration inputs. GitHub run 44490447228 passed all five selected units, including native Git for Windows and separate Windows runtime and domain steps. |
| AC3 | verified | The local workflow command and the bounded release reader accepted PR 592 run 44490447228, attempt 1, for base `78b19ff`, head `296a8fd`, synthetic merge and workflow revision `ad63434`, and tree `4d2ed29`. Live checks refused a legacy artifact and a different PR number. Fixtures refuse wrong workflow content, checkout, source, unit, platform, job, attempt and artifact. |
| AC4 | verified | In a disposable clone, the real PR artifact supplied both provider suites for an exact two-parent merge. A different tree and a direct commit received no reuse. Fixtures exercise unavailable evidence, the current-date provisional veto and release write guards for changed PR metadata and master. A simulated bounded patch publishes an immutable tag with the verified run and attempt. |
| AC5 | verified | The complete repository suite passed locally and the scoped GitHub jobs passed. Reviewed procedure and invariant references against the actual entry points. Reviewed the added prose and release evidence format for private account and machine values. Domain sources and consumer runtime and deployment procedures retain their separate ownership. |

## Qualification

The local repository suite passed on macOS, including 22 workflow, 22
mechanical, 14 staged-check and 22 release cases. Repository policy scans,
Gitleaks and actionlint passed. The GitHub proof supplied the exact candidate
checks to `workflow check`, which reran its current-date provisional check.
[Implementation CI](https://github.com/shk95/configs/actions/runs/44490447228)

Native provider and Windows evidence reflects the jobs on their respective
hosted platforms. The master-push reuse decision was replayed with a temporary
Git merge and live reference evidence. Remote publication guards were exercised
in fixtures. Host runtime and deployment remain consumer operations. The
change is available for review in [Draft PR #592](https://github.com/shk95/configs/pull/592).
