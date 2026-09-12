# How much work one commit and one branch should carry

kind: study
date: 2026-09-12
scope: repository
status: open

The proposal: commit only at important judgement points rather than splitting
every step, run one branch per milestone, and merge when the milestone is
complete. It was raised as a deliberate change to current policy, and it is
one. This document measures what the policy actually is, separates the
proposal into the two independent changes it contains, and finds that one of
them is already close to policy while the other is incompatible with the
migration it would first be used on.

Measured at `dev` c118e2f on 2026-09-12.

## What the policy is today, and what the tree did

`CONTRIBUTING.md`, "Branch and commit flow", says a topic branch is
`feature/<domain>-<topic>` or `fix/<domain>-<topic>` off `dev`, that completed
work merges with a merge commit, and that commits are scoped "where
practical". Nothing states how much work a commit or a branch should carry.

What is actually enforced is narrower than it looks:

- `tool/version-control/audit` holds the branch name to
  `^(feature|fix)/(unixlike|windows|common|repository)-[a-z0-9][a-z0-9-]*$`.
  A milestone-named branch satisfies it unchanged.
- `.githooks/pre-commit` refuses a commit only when a staged path has no
  owning scope. Nothing counts scopes, so a two-scope commit passes the gate.
- `INV repository/publish-through-dev` requires one pull request against
  `dev` from a topic branch. It says nothing about the branch's age or how
  many commits it carries.
- `INV repository/conventional-subject` holds the subject to seventy-two
  characters. Nothing else constrains a commit's size.

So neither half of the proposal is forbidden. Both are changes of practice
that the documents would have to describe.

The practice, over the last twenty-five pull requests merged into `dev`:

| Commits in the pull request | Pull requests |
|---|---|
| 1 | 11 |
| 2 | 5 |
| 3 | 6 |
| 5 | 2 |
| 6 | 1 |

Branch lifetime, first commit to merge, over the last twenty: eighteen were
under an hour, and the two longest were twelve and fourteen hours. The tree
has never had a branch that lived for days. Against that, `dev`'s history
holds twenty-seven `Merge branch 'dev' into <branch>` commits, so catching a
branch up is already routine at a lifetime of under an hour.

The milestones are a separate axis today and already drift from merges: of
three that exist, `unixlike: headless NixOS-WSL host` holds four closed
issues and no open ones and is still open. Under the proposal a milestone's
closure would become a merge event, which is a real tightening rather than a
relabelling.

## A. Committing at judgement points

This is close to a clarification rather than a change. Nothing enforces
granularity, `CONTRIBUTING.md` already says "where practical", and the
measured median is one commit per pull request, so the tree is already at the
small end. What it buys is real: the pre-commit hook runs the version-control
fixture suite, and this tree's commit messages are paragraphs of prose, so a
commit that records no judgement costs both.

One constraint has to survive the change, and it is the only hard one. Scope
is decided per commit, from the paths that commit touches, and the tag, the
CI lanes and the right to change a path all follow from it. A larger commit
is more likely to span scopes, and what a two-scope commit is allowed to
contain is currently unwritten:
`docs/candidates/subject-scope-and-two-scope-allowance.md` records that
`CONTRIBUTING.md` calls one pairing "the one accepted two-scope commit" while
the agent workflow states a general allowance, and leaves the question open
for the maintainer. Adopting A pulls that candidate's `promote-when`, which
fires when the branch-and-commit section is edited anyway.

The rule to write is therefore not "one commit per judgement point" but one
commit per judgement point that is pure in scope.

## B. One branch per milestone, merged at completion

In the general case this composes well with what exists. A milestone already
owns exactly one scope, so a milestone branch is single-scope by
construction; the branch name rule already accepts one; and `dev` stops
holding half-finished work.

It does not compose with the migration it would first be used on. That
migration is split across two milestones on purpose, and they block each
other.

```text
repository milestone   3a expand ────┐             ┌──── 3c contract
                                     │             │
unixlike milestone                   └──> 3b move ─┘
```

- 3b cannot even be committed unless 3a is already present. `git mv` of
  `modules/` to `unixlike/modules/` makes the classifier answer
  `unclassified`, and `.githooks/pre-commit` fails there.
- 3c cannot be opened until 3b has merged into `dev`, because deleting the
  old paths while they are still inside an open pull-request range is itself
  an unclassified change (`docs/architecture.md`, "Common domain").

So the first half of the `repository` milestone has to merge before the
`unixlike` milestone can start, and the second half cannot start until the
`unixlike` milestone has merged. Merging only at milestone completion
deadlocks. The expand, migrate, contract shape is not a stylistic
preference: `INV repository/scope-ownership` forces it.

The condition is mechanically decidable, which is what makes it writable as a
rule rather than as judgement. A branch must merge before another branch can
continue whenever a commit on the second would make the classifier answer
`unclassified` until the first has landed. Moves and deletions are the two
ways that happens.

## The alternative that does not work here

Stacking the pull requests — opening 3b against 3a's branch rather than
against `dev` — would let one milestone branch carry the whole sequence. Two
things stop it. `.github/workflows/ci.yml` triggers on pull requests whose
base is `master` or `dev`, so a pull request between topic branches runs no
job at all, and branch protection guards only those two branches; the
intermediate step would land with no gate. And
`INV repository/publish-through-dev` states that a published change reaches
shared history through one pull request against `dev`, with the helper
refusing a head already proposed against another base. Stacking would need
both the workflow and that invariant changed, which is a larger change than
the one being considered.

## What gets worse as a branch gets older

- **The base goes stale.** `dev`'s protection is strict, so a branch that
  falls behind cannot merge until it catches up, and GitHub's auto-merge does
  not do it. The procedure is a local merge of `dev` into the branch, which
  reruns the hooks and the native lanes against the tree that will actually
  land; `docs/candidates/topic-branch-catch-up-procedure.md` holds it, its
  `promote-when` is already satisfied, and under milestone branches it stops
  being occasional.
- **Evidence ages with it.** The local gate runs per commit against whatever
  base the branch had at the time. On a branch that lives an hour that is the
  landing tree; on one that lives a week it is not, and only the final
  catch-up rerun tests what merges. That candidate's `promote-when` names
  exactly this failure — a pull request merged whose native evidence came
  from a tip that did not contain `dev`.
- **`--publish` collides with it.** `tool/version-control/commit --publish`
  commits where it stands on any branch that is not `dev`, then pushes, opens
  a pull request against `dev` and arms auto-merge. A routine
  `brew add --publish` run while a milestone branch is checked out would arm
  auto-merge on the entire unfinished milestone. Either the helper learns
  about milestone branches or the practice is to leave the branch before
  running it.
- **Bisection coarsens.** A milestone merge puts many commits on `dev` at
  once, so a first-parent bisect over `dev` narrows to the milestone rather
  than to a commit.

## What adoption would change

| Location | Change |
|---|---|
| `AGENTS.md`, milestone paragraph | Today a closed milestone means its planned source work is complete and says nothing about merging. Tying closure to a merge is a tightening and has to be stated |
| `CONTRIBUTING.md`, "Branch and commit flow" | Branch lifetime and the exception condition; the scope-purity rule for commit size |
| `docs/candidates/subject-scope-and-two-scope-allowance.md` | Promoted, because the section is being edited and A depends on the answer |
| `docs/candidates/topic-branch-catch-up-procedure.md` | Promoted, because catching up stops being occasional |
| `tool/version-control/commit` | Either taught about milestone branches or documented as something to run from `dev` |

Nothing in `tool/`, the hooks or CI has to change for either half. That is
worth stating plainly: this is a practice change with a documentation cost,
not an enforcement change.

## What the maintainer has to decide

1. Whether A is adopted as written, with scope purity as the surviving hard
   constraint, and what a two-scope commit may contain.
2. Whether B is adopted as the default with a named exception, or not
   adopted. If adopted, whether the exception is written as the decidable
   condition above or left to judgement.
3. Whether a closed milestone means its branch has merged. This is the part
   that changes what a milestone asserts.
4. What `--publish` does when a milestone branch is checked out.

## Recommendation

Adopt A, as one commit per scope-pure judgement point, and promote the
two-scope candidate with it. It costs a paragraph and removes real ceremony.

Adopt B as the default, with the exception written as the decidable
condition: where a commit would be refused as unclassified until another
branch merges, the branches interleave and each half merges when it is ready.
The migration is the first thing to hit that exception, so it keeps its three
pull requests, and B applies to the milestones that follow.

Do not adopt B as an absolute rule. The deadlock above is not an edge case in
this repository; it is the shape every move and every deletion takes, and a
rule that has to be broken the first time it is used is not a rule.
