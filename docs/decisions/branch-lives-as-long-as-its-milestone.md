# A branch lives as long as its milestone

date: 2026-09-12
scope: repository
status: accepted
reopen-when: a pull request merges whose catch-up with `dev` was authored by GitHub rather than pushed through the hook, or a milestone branch grows past what one review can hold.
source: 88ee3ea:docs/design/commit-granularity-and-branch-lifetime.md § How much work one commit and one branch should carry

A topic branch here has meant one change. Of the last twenty merged into
`dev`, eighteen lived under an hour and the longest lived fourteen, so a
branch has been a way to satisfy branch protection rather than a place work
accumulates. Every judgement point therefore cost a pull request, a review
and a merge.

A branch is a milestone's. It is cut from `origin/dev` when the milestone's
work starts, carries every commit that milestone produces, and merges through
one pull request when the milestone's work is complete. The existing name
rule needs no change: `tool/version-control/audit` holds a branch to
`feature/<scope>-<topic>` or the `fix/` form over the four scopes, and a
milestone's title is already `<scope>: <outcome>`, so the branch is named
from it. Nor does the scope rule: a milestone owns exactly one scope, so a
milestone branch is single-scope by construction, and each commit on it marks
one judgement point (`docs/decisions/commit-marks-a-judgement-point.md`).

Branches still interleave where one blocks another, and that is not written
as an exception because nothing could be gained by writing it.
`.githooks/pre-commit` fails on a staged path with no owning scope, so the
sequence enforces itself: the Unix-like tree cannot be moved before the
classifier accepts the new paths, and the old paths cannot be deleted before
the move has merged, because each is an unclassified change until the other
lands (`docs/architecture.md`, "Common domain"). The planned migration is the
first case, and it keeps its three pull requests across two milestones for
that reason rather than by choice.

The risk is taken deliberately rather than hedged. A longer branch catches up
with `dev` more often, because protection on `dev` is strict and includes
administrators, and each catch-up is an opportunity to take the shortcut that
actually loses evidence: `gh pr update-branch` has GitHub author the merge,
outside the pre-push hook, which is where the native lanes run because this
repository adds no hosted runner
(`docs/decisions/ci-evidence-without-hosted-runners.md`). The correct
catch-up is a local merge of `dev` into the branch, whose push reruns the
hook against the tree that will land; `dev` already holds twenty-seven of
them. A longer branch also makes a larger diff to review and narrows a
first-parent bisect to a milestone rather than to a change.

None of that is measurable from here. This tree has never run a branch longer
than fourteen hours, so every claim about what a week-long one costs is a
prediction, and the way to find out is to run one and record what it did.
That is why the decision is taken whole rather than as a trial with a
narrower scope.

It is not registered under `provisional/`. That registry records what must
eventually become false, and this is not a measure expected to be removed;
the instrument for a policy adopted with a trip wire is the `reopen-when`
line above, and the trip wire is the shortcut rather than the branch's age.

Rejected:

- Merging only when a milestone completes, with no interleaving. It
  deadlocks on the first use: the migration's two milestones each need half
  of the other merged before they can continue.
- Stacking the pull requests, one topic branch based on another.
  `.github/workflows/ci.yml` triggers on pull requests based on `master` or
  `dev`, so a pull request between topic branches runs no job at all and
  branch protection guards neither, and
  `INV repository/publish-through-dev` states that a published change
  reaches shared history through one pull request against `dev`. Both would
  have to change.
- Keeping hour-long branches. It is the status quo and it works; what it
  costs is a pull request per judgement point, which is the ceremony this
  decision is spending a risk to remove.

What it costs. `tool/version-control/commit --publish` is run from `dev` and
not from a milestone branch: on any other branch it commits where it stands
and arms auto-merge on the pull request already open from that head, which on
a milestone branch would merge the unfinished milestone. Every templated edit
it owns is `unixlike`, so running one on a `repository` milestone branch
would also produce the two-scope commit the scope rule refuses. Two
candidates promote with this decision and their files are deleted in the same
change: the one that had recorded how a topic branch catches up with a moved
`dev`, because catching up stops being occasional, and the one that had
recorded what a commit subject's scope names and which two-scope commits are
allowed, because the branch and commit section is being rewritten anyway.
Both are now sentences in `CONTRIBUTING.md`. `AGENTS.md` gains the
sentence that a milestone's branch merges when the milestone's work is
complete; closure itself stays the maintainer's, and an issue already closes
when its pull request merges. Nothing in `tool/`, the hooks or CI changes.
