# Work is planned and verified in documents, and a branch is one increment

date: 2026-09-19
scope: repository
status: accepted
issue: #265
reopen-when: a spec's report cannot be ended because its criteria no longer describe the work and no amendment can say why, or the roadmap and the open issues disagree about what is in progress for longer than one review period.
supersedes: docs/policy/decisions/repository/branch-lives-as-long-as-its-milestone.md
source: 82e4c68:docs/work/repository/work-model/spec.md § Decisions

Planning lived in GitHub milestones and their issues, one milestone to one
scope, one branch and one pull request. Three things did not hold. The rules
could not express the host roadmap: seven lanes became chains of narrow
single-scope milestones, the second time the same block was met. Plans and
their verification could not be held to account, because an issue's
acceptance criteria can be edited after the fact and its evidence is spread
over comments. And the branch rule did not survive its first case: the first
milestone under it took ten pull requests across two milestones, and no
milestone-length branch has run since it was adopted. Its trip wire also
fired — on 2026-09-19 two pull requests were caught up with `dev` by a merge
GitHub authored, outside the hooks — though with branches that lived an hour,
which says the shortcut is a habit to correct and not a cost of long
branches.

Documents plan and verify; issues hold execution state. Work with more than
one acceptance criterion or more than one pull request has a spec and a
report, created in the same commit. The spec is fixed: its criteria, each
naming the evidence lanes that must be verified, change only by a dated
amendment that names them. The report answers every criterion and ends as
done, abandoned or superseded. An execution issue names its spec, holds the
increments as a checklist, carries no acceptance criteria and is never a
source of evidence; it closes from what the report says, and no commit
message or promotion body carries a closing keyword. Any other change is a
single pull request whose body carries its evidence.

GitHub milestones are no longer used. The roadmap is a tracked file beside
the work items that states lanes and order, not schedule. No lane labels are
introduced.

A branch is one reviewable increment — one issue, or what one judgement
covers — cut from `origin/dev` and merged through one pull request when it is
complete and green. A spec takes as many pull requests as it needs.
Unchanged: commits, branches and pull requests are single-scope; the branch
name rule; `dev`-only promotion; domain release tags; evidence reported per
lane and never upgraded; and a catch-up with `dev` is a local merge pushed
through the hooks.

A work document is still not policy. Authority stays where `AGENTS.md` puts
it, and a durable rule that a piece of work produces lands in a decision
record or an invariant. What changes in
`docs/policy/decisions/repository/design-documents-outside-the-authority-model.md` is one
sentence: work now does hand back a report. The report is owned by its spec,
which answers the objection that a document written by the work to describe
itself would be neither argument nor authority and owned by nothing.

Rejected:

- Keeping milestones and relaxing "one scope". A milestone that spans scopes
  still keeps its criteria in issue text, which is the part that cannot be
  held to account.
- Acceptance criteria in the issue with the report in the repository. The
  bar has to be fixed where the evidence is judged against it, or an edited
  criterion and its evidence can never be compared.
- Lane labels on issues. The roadmap already states the lanes, and a label
  is a second list nothing checks.
- Closing issues with keywords on the promotion. It ties closure to an event
  that certifies nothing about the work.
