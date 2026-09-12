# Design documents

A design document is an argument, never a rule. It is where a direction is
proposed, measured and argued before the repository adopts any part of it,
and it sits outside the authority model on purpose: nothing in `AGENTS.md`,
`docs/architecture.md`, the registries, the tools, the hooks or CI rests on
one, and an agent does not follow one as a rule.
`docs/decisions/design-documents-outside-the-authority-model.md` records why
the area exists; `CONTRIBUTING.md`, "Write a design document", is the
procedure.

Traffic between the two layers runs one way. A design document observes the
repository: it reads the tracked tree, the registries and the history, and
quotes what it finds with the date and the commit it was read at. The
repository adopts a design document only through an inlet that is reviewed on
its own terms — a decision record, a promoted candidate, a registered
provisional measure, or an issue — and each inlet names the document as its
source. Adoption is what makes a direction binding and the repository
maintainer owns it. Writing a design document changes nothing.

The division is not between kinds of thinking but between proposed and
adopted. Judgement about what must remain true of this repository is internal
and lives where the authority model puts it. Judgement about where the
repository should go next is proposed here and becomes internal the moment an
inlet accepts it. Work under the adopted direction produces commits, check
evidence and a `docs/status.md` line rather than a report; this area reads
those and writes the next argument.

What does not belong here: current state, which is `docs/status.md`; a
schedule, which is a milestone and its issues; and a sentence someone would
like a policy document to carry, which waits in `docs/candidates/`. Scratch
thinking that promises nothing stays untracked in `notes/`.

## Format

One file per document, `docs/design/<slug>.md`. Line 1 is `# <Title>`; then a
header of `key: value` lines up to the first blank line, parsed the way
decision records are (`docs/decisions/README.md`); then prose.

| Key | Count | Meaning |
|---|---|---|
| `kind` | 1 | `study` for what was measured and judged, `plan` for what to do next and what it predicts, `map` for a picture of the tree as it stands. |
| `date` | 1 | `YYYY-MM-DD` the document was opened; later work carries its own date in prose. |
| `scope` | 1+ | The scope adopted work would classify as: `unixlike`, `windows`, `repository` or `common`; repeated where the argument spans more than one. |
| `status` | 1 | `open` while the document is still producing outcomes, `closed` once it has produced them all, `superseded` when another document replaces it. |
| `issue` | 0+ | `#<n>`. |
| `outcome` | 0+ | One thing the document produced: a decision record, a candidate, a provisional entry, an issue, or a merged pull request. |
| `supersedes`, `superseded-by` | 0–1 each | A document path. |

## Life of a document

A document opens `open`, gains an `outcome` line for each thing it produces,
and becomes `closed` when the last one has landed. After that only `outcome`
lines are added. It is never deleted: an adoption record cites it as the
source of what was adopted, and deleting a source turns that citation into a
claim about nothing. Reconsidering a direction writes a new document that
`supersedes` the old one, which becomes `superseded`. This is where a design
document differs from a candidate, which is deleted on promotion because its
whole content moves into the text it was proposing.

A `plan` carries its predictions, written before the work runs, with the
measured result beside each afterwards. That ledger is the one part of a
document edited after the fact, and it is worth keeping only under one rule:
a prediction written after its result is not a prediction and is not added to
the ledger at all. A result that contradicts the argument behind the plan is
recorded in the ledger and then corrected in the `study` it came from,
because correcting the ledger alone leaves the reasoning quietly stale.

A measurement is quoted with the date and the commit it was taken at, because
the tree moves and the document does not. A document that describes current
state rather than a measurement has taken `docs/status.md`'s work and will be
wrong without anyone noticing.

There is no checker for this directory, for the reason `docs/candidates/` has
none: a malformed header costs a reader a moment and no gate depends on it.
The one rule that is checked runs the other way.
`tool/version-control/design-citations` refuses a citation of a document here
from anything that carries authority
(`INV repository/design-outside-authority`).

## Index

| Kind | Scope | Title | Status | Record |
|---|---|---|---|---|
| map | unixlike, windows, repository | What the three scopes own and what a change passes through | closed | repository-domain-map.md |
| study | unixlike, repository | Why the Unix-like domain's shape costs what it does | closed | unixlike-restructure-study.md |
| plan | unixlike, repository | Moving the Unix-like domain into its own tree, in stages | open | unixlike-restructure-plan.md |
| study | repository | How much work one commit and one branch should carry | open | commit-granularity-and-branch-lifetime.md |
