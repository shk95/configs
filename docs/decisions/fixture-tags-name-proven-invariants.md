# A fixture tag names only an invariant its case proves

date: 2026-09-04
scope: repository
status: accepted
issue: #137
issue: #139
source: 9f1e8ce:docs/status.md § Invariant registry

The rule used was that a tag names an invariant only if the case fails on
that violation. Four architecture sentences and five entries now hold the
rules: `INV windows/external-profile-blocks-preserved`,
`INV windows/subset-owns-declared-keys`,
`INV windows/selection-closed-and-explicit`, `INV windows/font-state-total`
and `INV windows/capture-publishes-through-dev`, each tagged on the case
that exercises its statement; a ninth unit's payload-declared-once case
names `INV windows/feature-owns-every-item`, which it already proved. Two
units were deleted rather than tagged — `version gate`, a semantic-version
cast with no schema and no message, and `Windows host guard`, which
fixtured an override that existed only for it — and the parse gate moved
out of the suite into `windows/tools/test.ps1`, where it runs after the
Pester gate and before the suite. Three candidate tags were dropped on
review because their cases would have passed the exact violation the entry
describes: `unique-ids` on the payload-declared-once case, which checks
source paths rather than ids; `parser-declared` on the parser-missing
cases, which are about a parser the host lacks rather than an undeclared
name; and `schema-version-refused` on a semantic-version cast with no
schema and no message.

The repository half of the fixture pruning landed on 2026-09-04 and made
C10 the default. The three remaining untagged units were sections of the
commit-helper suite. `INV repository/publish-through-dev` now holds what the
`--publish` and `prune` cases prove — one pull request against `dev` from a
topic branch, never a commit on `dev` or `master`, a created branch starts
at `origin/dev`, a rejected push stays local, protected branches are never
pruned — with the same narrowed wording as its Windows twin, because both
helpers commit where they stand on a topic branch. The mas section's
negative cases name `INV repository/scope-ownership`,
`INV repository/evidence-three-states`, `INV repository/flake-lock-isolated`
and `INV repository/hooks-are-the-tracked-ones`, which they had proved
untagged. With the count at zero, `tool/version-control/invariants` fails an
untagged unit on every commit and in CI; `INVARIANTS_ENFORCE_C10=0` restores
the report mode for a local survey. Known limit: content before a shell
suite's first banner is in no unit and invisible to C10 — in the repository
suite that is everything before the `commit mas add/remove` banner: the
index and `GIT_DIR` guards, the gate, promotion, evidence and flake cases,
the pwsh detection cases and the brew/cask half of the commit-helper cases,
most already tagged but unchecked; a follow-up may give that span banners.
