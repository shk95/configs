# Moving the Unix-like domain into its own tree, in stages

kind: plan
date: 2026-09-10
scope: unixlike
scope: repository
status: open
outcome: #213
outcome: #214
outcome: docs/decisions/unixlike-domain-owns-its-tree.md
outcome: docs/decisions/concern-first-inside-the-domain.md

The cheap parts of `docs/design/unixlike-restructure-study.md` were carried
out; the rest is written down here. Each stage writes its predictions before
it runs and compares them with what happened afterwards, because a prediction
written after the result is not one and is not added to the ledger at all.
Drift is sorted into three kinds: tool drift, where the environment did not
behave as expected; content drift, where the repository was not as expected;
and judgement drift, where the expectation itself was wrong. The third is the
valuable one, and it is corrected in the study rather than only here,
otherwise the reasoning goes quietly stale.

## The stages

| | What | Scope | State | Needs |
|---|---|---|---|---|
| 0 | Correct text that is false today | repository, unixlike | merged into `dev` as #213 and #214 | — |
| 1 | Record the observations as candidates | repository | merged with them | — |
| 2 | Two decisions: the domain tree, and concern first | repository | recorded on 2026-09-12, in the outcome list above | — |
| 3 | Migrate: expand, migrate, contract | repository, unixlike, repository | blocked | 2 |
| 4 | Split `commit`, moving authoring knowledge into the domain | repository, unixlike | blocked | 3 |
| 5 | A domain entry point | unixlike | blocked | 3 |

Stage 3 blocks 4 and 5 structurally rather than by schedule. Without a domain
directory there is nowhere to put the pieces the split produces, and building
an entry point at the root repeats a rejection
`docs/decisions/windows-entry-point-in-domain.md` already records.

## Stages 0 and 1: predicted against actual

P1 to P11 were written before any editing started. The actual column was
measured afterwards.

| | Check | Predicted | Actual | |
|---|---|---|---|---|
| P1 | classify, the two tools | `repository` | `repository` | match |
| P2 | classify, `module-classes.nix` | `unixlike` | `unixlike` | match |
| P3 | classify, the candidate documents | `repository` | `repository` | match |
| P4 | select, the two tool files | `repository:fixtures` | `repository:fixtures` | match |
| P5 | select, `module-classes.nix` | format, lint, payloads | format, lint, payloads | match |
| P6 | select, candidates only | empty | empty | match |
| P7 | invariants | exit 0 | 0, 56 registered, 0 pending | match |
| P8 | hygiene | exit 0 | 0, 307 paths | match |
| P9 | format, lint, payloads | exit 0 | 0, 0, 0 over 15 payloads | match |
| P10 | the version-control fixtures | exit 0 | exit 0 | match |
| P11 | remaining `AGENTS.md line` sites | 0 | 1 | drift |

Also run: `domain-reads` clean over 83 Unix-like and 13 Windows files, and
`provisional` with 1 registered and 0 overdue.

What changed: three citations in `tool/version-control/commit` and one in
`tool/version-control/test` moved from a line number to a section name, with
the paragraphs rewrapped; one sentence in `modules/flake/module-classes.nix`
that cited a record which does not exist was deleted, and the rest of its
reasoning kept; two new candidate files with their index rows; and one
occurrence line on an existing candidate.

Both landed on 2026-09-10. `dev` is protected, so each went up as a topic
branch in its own scope and both were pruned after merging: #213 for
`repository`, #214 for `unixlike`. The classifier dispatch behaved as
designed and was observed doing so — #213 ran only the version-control lane
and #214 only the flake lane, everything else skipped, which is the sentence
about one domain's change not needing another domain's pass, executed.

## Where it drifted

| | Kind | Predicted | Actual | Resolution |
|---|---|---|---|---|
| D1 | tool | `sed -i ''` substitutes in place | the empty suffix argument did not survive the shell and sed read the script as a file | write the substitution to a script file and apply it with `sed -f`, then write the result back with `cat > file` so the mode and identity are kept, which is the tree's own idiom |
| D2 | tool | `perl -e '\x{00A7}'` gives UTF-8 | a latin-1 single byte | as above |
| D3 | tool | `perl -CSD` with a literal gives correct output | double encoding | as above |
| D4 | content | line widths unchanged by the substitution | three comment lines over 79 columns | rewrapped; the 173-column refusal string was one line to begin with and was left |
| D5 | content | no `AGENTS.md line` sites left | one | correct behaviour, not fixed: the new candidate quotes the broken form as its evidence |
| D6 | content | the commit subject passes | the hook refused a 77-character subject against its 72-character rule | shortened and recommitted. The gate worked; leaving the commit-message convention out of the predictions was the omission |
| D7 | content | auto-merge merges once the checks pass | every check passed, `MERGEABLE`, auto-merge armed, and nothing merged for twenty minutes | #213 merging first moved `dev`, so #214's base was stale and `dev`'s protection is strict. GitHub's auto-merge does not update a branch itself. Merging `dev` into the topic branch locally and pushing reruns the pre-push hook and the native lanes against the tree that will actually land; a candidate had already recorded the procedure, since promoted into `CONTRIBUTING.md`, and history holds 23 of the same merge |

D5 has a consequence for any future citation check: it will catch the
document that explains the broken form as a violation of itself. The tree
holds two precedents — `tool/version-control/domain-reads` strips comments
before applying its patterns, and `tool/version-control/hygiene` has declared
exceptions in `hygiene.allow` — and the check has to follow one of them.

All three tool drifts came out of one UTF-8 substitution. In this
environment, put non-ASCII into a file through a script file rather than
through an inline script that passes through shell quoting. It cost under
fifteen minutes, which is below the bar for `docs/troubleshooting.md`, but it
is candidate material if it recurs.

## Stage 2: the two decisions

The domain tree. What is executed and owned by a domain is scope first, and
`modules/karabiner.nix` interpolates `${../tool/darwin/karabiner}` into an
activation, so that script is domain material: B2. Rejected are layout A,
which gains nothing and breaks the import-order check; an `src/` wrapper,
which changes every path reference and adds no information; and B, which
leaves the reference escaping the domain. The measurement on 2026-09-10
withdrew the rebuild cost once attributed to B, leaving copy time and the
flakeref, so ownership is what decides.

Concern first inside the domain. `homeManager.shared` is written by 20 of the
42 feature files, so a class-first tree cannot hold its largest group;
`homeManager` is an evaluator rather than a flavour, so it is not exclusive
with `darwin` or `nixos`; WSL spans two flavours; and five files write into
two classes. A class in a directory name would also state twice what the
fragment states once, and only the fragment is checked, so the tree would
assert something no evaluator enforces.

Nothing moves at this stage. No candidate is promoted here either: the
trigger for `docs/candidates/domain-tool-placement-and-justfile-exception.md`
is stage 3a, when the classifier is edited anyway.

Recorded on 2026-09-12, and both records settled a question this plan had
left ambiguous. The first is `tool/checks/`: this document's stage 3b listed
only `tool/darwin/` as moving and left the checks to a path update, while the
study's split principle applies to both, and the record follows the
principle. The checks and their fixtures move into the domain, which adds to
stage 3b the `enforced-by` locator of every Unix-like invariant that names
one, since `tool/version-control/invariants` refuses a locator that is not a
tracked executable. The second is the depth of the concern directories, which
this document never fixed: the record fixes the module root at
`unixlike/modules/<concern>/`, because `flake.nix`, `tool/checks/composition`
and `tool/checks/import-order` all already assume a `modules/` beside the
flake, and concern directories placed directly beside `flake.nix` would pull
the flake file and the deliberately broken check fixtures into all three
walks.

## Stage 3: three commits, each in one scope

`classify` answers `unclassified` for a moved path and the hooks and CI
refuse there, so a commit holding both the move and the classifier change
mixes scopes. Expand, migrate and contract keep all three single-scope.

**3a, expand, `repository`.** `classify`, `tool/dispatch/select` and
`tool/version-control/domain-reads` accept both the old and the new paths.
The tolerance is registered under `provisional/repository/` with its
`exit-when`, `watch` and `review-by`, and every line it touches carries a
`PROV` tag. The precedent is `invariants/common/.gitkeep`, an arm kept for a
path that no longer exists.

Predicted: `classify --files unixlike/modules/bat.nix` answers `unixlike`
where it answers `unclassified` today; `classify --files modules/bat.nix`
still answers `unixlike`; `provisional` reports 2 registered and 0 overdue;
and `tool/version-control/test` exits 0, which is the likeliest drift point,
because a fixture that asserts the classifier's arm list as a string will
fail.

Measured on 2026-09-12, at `dev` 282206c, in #218. All four held, including
the one expected to drift: no fixture asserted the arm list as a string, so
the suite passed with the new cases added and nothing rewritten. Also run:
`domain-reads` clean over 83 Unix-like and 14 Windows files, `hygiene` over
321 paths, `invariants` at 59 registered, and `tool/dispatch/select` giving
`repository:fixtures` for the change itself.

Two things the predictions did not cover and a later stage now has to.
`.envrc` and the `Justfile` are not part of the measure: they stay at the
root, so they moved into the permanent arm rather than the disposable one,
and the contraction must not take them. And the Unix-like pathspec in
`domain-reads` needed `:(exclude)unixlike/assets` added with it, because
`unixlike/*` would otherwise pull the payload tree into a scan that has
always excluded payloads on the ground that data reads nothing. Neither is
drift against a prediction; both are predictions that should have existed.

**Judgement drift, found on 2026-09-12 while starting the move.** This
document, the issue and the expansion itself all treated 3a as a
classification problem. It is two: where a path belongs, and where an
executable is found. The three tools answer the first. The hooks resolve
`tool/checks/<name>` by literal path and the Unix-like CI job names each
check by path, and none of that moved, so the expansion as shipped would have
met the move as a merge failure — the CI job on a missing file, and, worse,
`pre-commit` reporting every Unix-like check unverified and passing, which
loses evidence more quietly than failing. The measure was extended the same
day with a resolver in `.githooks/evidence` that both hooks call and a
`checks` step in the CI job, all tagged `PROV`. The lesson generalises past
this migration: an expansion has to widen every plane that names the old
location, and "the classifier answers" is not the same claim as "the tooling
finds it".

**And the planes were more than two.** Starting the move a second time, with
the tree actually moved in the index, turned up five more places outside the
domain that name a moving path and would break: `tool/version-control/commit`
edits the Homebrew module and both Karabiner payloads by literal path, the
zellij watcher reads `modules/zellij.nix` with `sed`, `.gitattributes` holds
the line endings of the PowerShell payload, `.gitignore` keeps a host-local
WezTerm file out, and the agent settings allow the checks directory. None of
them would have failed a gate — which is what makes them worse than the CI
job, not better. The expansion is three commits rather than one, and the
number was not knowable from reading the plan; it came from moving the tree
and grepping for what pointed at it.

The general form of the correction: before a path moves, every reference to
it that is *executed* has to resolve at either location, and the way to find
them is to perform the move and search, not to reason about it.

**And grepping was not enough either.** A fourth round came out of running the
gates with the tree moved rather than reading them. `tool/version-control/hygiene`
reads the inventory to learn which names are declared, `tool/doctor.sh` asks
the flake two questions by path, `tool/version-control/audit` reads the
lock's history by pathspec, and the commit fixtures copy the Karabiner tool
and payloads out of the real tree. Hygiene and doctor failed outright, which
is the right direction; audit would have gone on passing while silently
covering no new refresh. The counting method that worked, in the end, was
neither reading the plan nor grepping the tree but applying the move and
running every gate.

The move also exposed a latent bug it did not cause.
`tool/checks/karabiner-test` resolved its prerequisite library from `$0`
*after* `cd`-ing to the repository root, which worked only while the two were
the same directory. Every other check resolves it before. Fixed with the move,
in the domain's own commit.

**3b, migrate, `unixlike`.** `git mv` of `flake.nix`, `flake.lock`,
`modules/`, `assets/`, `tool/checks/` and `tool/darwin/` into `unixlike/`;
the Karabiner interpolation rewritten for the new layout; `.envrc` to
`use flake ./unixlike`; the `Justfile`'s fourteen `path:.` flakerefs and the
default paths in the checks; and the `enforced-by` locator of every Unix-like
invariant that names a check, which `tool/version-control/invariants` refuses
when it is not a tracked executable.

Predicted: the three toplevel derivation paths are byte-identical across the
move. The comparison is only meaningful within one clone and one flakeref
spelling — the spike's absolute values did not reproduce in this clone and
the cause was never found — so it is taken immediately before and after, in
the same place. `tool/checks/composition unixlike/modules` answers 42 feature
files. `tool/checks/test` exits 1 with "flake.nix does not exist" unless the
flake path is updated, and 0 with it. The `path:.?dir=unixlike` spelling in
`.envrc` works but silently stops direnv watching the flake files, and
`.?dir=unixlike` without `path:` fails with a message that does not hint at
the cause.

**3c, contract, `repository`.** The old arms leave the three tools, and the
`PROV` tags and the `provisional/` entry are deleted together.

Predicted: `provisional` reports 1 registered. The subtle part is that
deleting the old paths while they are still inside an open pull-request range
blocks the push on its own, because a path nothing classifies cannot be
pushed and that includes its own removal (`docs/architecture.md`, "Common
domain"). 3c opens only after the move has merged into `dev`.

The milestone rule splits this in two. "One milestone, one scope" has no
exception, so `repository: migration arms` and `unixlike: domain tree` stand
separately and are only linked, and neither has a visible result alone. That
is one of the two places with no way around.

## Stages 4 and 5

**4, splitting `commit`.** The authoring knowledge — the Homebrew list
syntax, the `masApps` attribute set, the Karabiner projection — moves to
`unixlike/<concern>/tool`, and `commit` stays an engine that takes an edit
plan and confirms, commits and publishes it. This is the actual bottleneck,
the gate every new extra has to pass.

Predicted: the regression test is that for the same input, `brew add
<formula>`, the diff and the commit message are identical before and after;
`tool/version-control/commit` shrinks substantially from its 1448 lines; and
the existing fixtures need updating to cover the new interface, without which
failure is expected rather than surprising.

**5, a domain entry point.** `unixlike/unix-env`, a thin file holding a verb
table and forwarding status unchanged, the counterpart of
`windows/win-env.ps1`.

Predicted: `unix-env help` prints the verb table and exits 0, and an unknown
verb exits 64, a status that collides with no check outcome. Each verb
forwards its target's exit status unchanged, which needs a new invariant,
`unixlike/entry-point-forwards-status`, with fixtures in both directions. The
`Justfile` is not deleted but becomes a thin adapter calling the entry point.

## Still unverified

One run of `home-manager news` against the subdirectory flakeref on a WSL
host. The script's own parsing and the `nix eval` it performs were both
checked and no failing path is visible.

## 2026-09-12: the sequence, revised

An external layer was added to the repository first, so that this document
and the study could be tracked at all
(`docs/decisions/design-documents-outside-the-authority-model.md`). The
stages above are unchanged; the order they are executed in is now:

1. the design area, merged
2. these three documents, ported from the artefacts they were written as
3. the two stage-2 decision records, each citing its source here
4. the two milestones and their issues
5. stage 3a, expand, which is where the placement candidate is promoted
6. stage 3b-1, the tree move alone
7. stage 3b-2, the concern-first rearrangement
8. stage 3c, contract, opened only after 7 has merged
9. stages 4 and 5, each opening with a design document of its own, because
   both rest on questions the study left to the maintainer

Splitting the migration into 6 and 7 is new. The spike proved that moving the
tree leaves the derivation paths byte-identical; it proved nothing about
renaming the files inside it. The class merge is keyed by defining file, so
renaming a file can reorder a list two files contribute to, which moved every
generation's hash once already on 2026-09-04. Predicted for 6: the derivation
paths are identical. Predicted for 7: they may move, and if they do the cause
is the rename rather than the relocation. In one commit the two would be
indistinguishable.
