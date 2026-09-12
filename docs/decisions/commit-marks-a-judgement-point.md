# A commit marks a judgement point

date: 2026-09-12
scope: repository
status: accepted
reopen-when: a change cannot be expressed as scope-pure commits without distorting it, or a second kind of two-scope commit is needed.
source: 88ee3ea:docs/design/commit-granularity-and-branch-lifetime.md § How much work one commit and one branch should carry

Nothing in this repository has ever constrained how much work a commit
carries. `CONTRIBUTING.md` says commits are scoped "where practical",
`INV repository/conventional-subject` holds the subject to seventy-two
characters, and `.githooks/pre-commit` refuses only a path with no owning
scope. Splitting a change into one commit per step was therefore a habit
rather than a rule, and it is not a free one: the pre-commit hook runs the
whole version-control fixture suite each time, and this tree's commit
messages are paragraphs of prose, so a commit that records no judgement costs
both for nothing.

A commit marks a judgement point. It carries the change that one decision
produced, however many files that is, and a change is not split further
merely because it has parts. The subject names the judgement, and the body
says what was decided and what was rejected, which is what the existing
messages already do.

One constraint survives unchanged and is the reason this is a rule about
judgement rather than about size: a commit owns one scope. Ownership is
decided per commit from the paths it touches, and the release tag, the CI
lanes and the right to change a path all follow from it, so a commit that
spans scopes makes all three ambiguous at once. Where one judgement would
produce a cross-scope commit, it is two commits, and the order between them
is usually forced anyway.

Rejected:

- Splitting per step. It is what this decision replaces, and its cost grows
  with a branch's length rather than with the change's difficulty.
- Widening what a two-scope commit may contain. Classifying each of the last
  sixty non-merge commits on `dev` gives none that spans more than one
  scope, so the question is moot in practice. The conflict a candidate had
  recorded — the agent workflow stating a general allowance the procedure
  does not — is decided by `AGENTS.md`, "Governance design": a procedure must
  not silently create policy, so the broader wording is not policy and
  `CONTRIBUTING.md`'s narrower sentence stands. That candidate is promoted
  and deleted with this decision. Widening the allowance stays available as a
  deliberate act.
- A checked rule. "Judgement point" is not decidable by a tool, and a check
  that approximated it by counting files or lines would refuse correct
  commits. The scope half is already enforced; this half is not, and says so.

What it costs. The rule is unenforceable by design, so the failure it invites
is the opposite of the one it removes: a commit that carries two judgements
because they happened at the same keyboard. A reviewer reads for that, and
the subject is the tell, because a subject that needs "and" usually names
two. First-parent bisection over `dev` is unaffected, since it already
narrows to a merge rather than to a commit. Nothing in `tool/`, the hooks or
CI changes.
