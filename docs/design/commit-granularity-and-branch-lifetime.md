# How much work one commit and one branch should carry

kind: study
date: 2026-09-12
scope: repository
status: open
outcome: docs/decisions/commit-marks-a-judgement-point.md
outcome: docs/decisions/branch-lives-as-long-as-its-milestone.md

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
contain is currently unwritten. A candidate open at the time of writing recorded that
`CONTRIBUTING.md` calls one pairing "the one accepted two-scope commit" while
the agent workflow states a general allowance, and left the question to the
maintainer; its `promote-when` fires when the branch-and-commit section is
edited anyway, which adopting A does.

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
  land. A candidate held that procedure with its `promote-when` already
  satisfied, and under milestone branches catching up stops being
  occasional.
- **Evidence ages with it, but less than this first said.** Corrected on
  2026-09-12 after checking the protection settings: `dev` requires
  `Required checks`, `strict` is on and administrators are included, so a
  branch cannot merge until it contains `dev`, and the catch-up is a local
  merge whose push reruns the pre-push hook. The native lanes live in that
  hook rather than in CI, because this repository adds no hosted runner
  (`docs/decisions/ci-evidence-without-hosted-runners.md`), and CI itself
  tests the synthetic merge of head and base. So the landing tree is tested
  either way, and the hole is narrower and specific: `gh pr update-branch`
  has GitHub author the catch-up merge, outside the hook and therefore
  outside the native lanes. A longer branch does not age the evidence by
  itself; it multiplies the catch-ups, and each one is an opportunity to
  take the shortcut that does.
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
| The two-scope allowance candidate | Promoted and deleted, because the section is being edited and A depends on the answer |
| The catch-up procedure candidate | Promoted and deleted, because catching up stops being occasional |
| `tool/version-control/commit` | Either taught about milestone branches or documented as something to run from `dev` |

Nothing in `tool/`, the hooks or CI has to change for either half. That is
worth stating plainly: this is a practice change with a documentation cost,
not an enforcement change.

## Four questions, and what already answers three of them

The first draft left four questions for the maintainer. Checked against the
tree on 2026-09-12, three of them are settled by mechanisms that exist, and
asking them again would be asking the repository to choose something it has
already arranged.

**The exception needs no rule, because the hook is the rule.**
`.githooks/pre-commit` fails on a staged path with no owning scope, so
committing the move before the classifier accepts the new tree is not a
policy someone may decide to violate; it is refused. Writing the interleave
as a rule would restate a refusal that already happens. What is missing is a
sentence in `CONTRIBUTING.md` saying why branches interleave, not a rule and
not a check.

**The two-scope question is moot in practice, and its conflict is already
decided.** Classifying each of the last sixty non-merge commits on `dev`
gives no commit spanning more than one scope, so widening the allowance buys
nothing today. And `AGENTS.md`, "Governance design", already settles which
text is in force: procedures and tools implement policy and must not
silently create new policy, so the agent workflow's broader wording is not
policy and the narrower sentence in `CONTRIBUTING.md` stands. The default is
the narrow rule, and widening it would be a separate, deliberate act. The
planned migration is single-scope at every step and needs nothing wider.

**Milestone closure already follows merges.** Eight of the last twelve pull
requests carry a `Closes #<n>` line, so an issue closes when its pull request
merges and a milestone's open count reaches zero as merges land; the ones
without such a line had no issue. `AGENTS.md` already gives closure to the
maintainer with the milestone description and the final evidence issue as its
manual evidence. A rule tying closure to a merge would restate what GitHub
produces. What is worth writing is the convention rather than the rule: a
pull request that resolves an issue says so.

**What `--publish` does follows from the scope rule.** Read in
`tool/version-control/commit`: on a branch that is not `dev`, with a pull
request already open from that head, it runs `gh pr merge --auto --merge` on
that pull request, which on a milestone branch would arm auto-merge over the
unfinished milestone. But every templated edit the helper owns is `unixlike`
— a formula, a cask, a Mac App Store entry, a lock refresh, a Karabiner
capture — and a milestone branch is single-scope, so running one on a
`repository` milestone branch would produce the two-scope commit the narrow
rule refuses, and on a `unixlike` milestone branch it would be a different
unit of work wearing the milestone's branch. Either way the answer is forced:
run it from `dev`, which is the path the helper was built for. No tool
change.

## Decided

**Commit granularity, A: adopted.** One commit per judgement point that is
pure in scope. Nothing measured changes, because the tree is already there;
what changes is that splitting for its own sake stops.

**Branch lifetime, B: adopted, with the risk accepted deliberately.** A
branch lives as long as its milestone and merges when the milestone is
complete. The maintainer's reason for taking it rather than hedging it is
that the cost is not decidable from here and has to be met in a real case:
this tree has never run a branch longer than fourteen hours, so every
argument about what a week-long branch does to review size, to catch-up
frequency and to the temptation of `gh pr update-branch` is a prediction
rather than an observation.

The exception is not written as a rule, for the reason above. Where a commit
would be refused as unclassified until another branch merges, the branches
interleave because the hook makes them; the migration is the first case and
keeps its three pull requests.

What would reverse it is named in the decision record rather than left to
memory, and the honest trip wire is not "evidence aged" but the shortcut:
a pull request merged whose catch-up was authored by GitHub rather than by a
push through the hook.

## Still open

Nothing, for these two questions. What remains is to watch the first
milestone-length branch and record what it actually cost, which belongs in
this document as a dated paragraph rather than in a new one.
