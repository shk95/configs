id: repository/issue-closes-from-report
statement: An execution issue is closed automatically only from a report that is done, abandoned or superseded, and an issue left open beside such a report is reported.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/close-issues
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/work-planned-and-verified-in-documents.md § Work is planned and verified in documents, and a branch is one increment

Every pull request targets `dev` and GitHub closes a linked issue only on a
merge into `master`, so closure was manual, and a closing keyword would move
it to a promotion, which certifies nothing about the work. The one automatic
path reads the reports: on a push to `dev`, a report that became terminal in
that push, and whose spec names an issue, closes the issue with a comment
linking the report — completed when it is done, not planned when it is
abandoned or superseded. A pending report closes nothing, a spec that names
no issue closes nothing, and a tree the work check refuses closes nothing.

The workflow's token can read the repository and write issues, and nothing
else. What it misses — an issue reopened by hand, a report that ended before
the workflow existed, a run that failed — the remote audit reports as an
execution issue open beside a terminal report. A spec past its review-by
whose report is still pending is the other half of the same neglect, and
the local audit warns about it.

Accepted limits: the workflow runs only for pushes to `dev`, which is where
every report lands; and it trusts the report's state once the work check
accepts it, so whether the evidence behind a verified row is evidence stays
the reviewer's.
