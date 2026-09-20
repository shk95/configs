# Work documents

Work that needs more than one judgement is planned and verified here. A
work item is one directory, `docs/work/<scope>/<slug>/`:

| File | Nature | Holds |
|---|---|---|
| `spec.md` | fixed | the goal, the decisions, the acceptance criteria with the evidence lanes each requires, and a `review-by` date |
| `report.md` | fixed | for each acceptance criterion, its state and the evidence behind it |
| `study.md` | optional | what was measured and argued before a spec existed |

An issue holds what changes while the work runs — the increments as a
checklist, their order, blockers, links to pull requests. It carries no
acceptance criteria and is never a source of evidence; what matters after it
closes is written into the report.

A work document is not policy. It binds only the work it describes, and
nothing in `AGENTS.md`, `CONTRIBUTING.md`, `docs/policy/`, the provisional
registry, the tools, the hooks or CI rests on one. A durable rule that a
piece of work produces lands in a decision record or an invariant, which
names the document as its source; adoption through such an inlet is what
makes a direction binding, and the repository maintainer owns it.
`tool/version-control/design-citations` refuses a work item's path from
anything that carries authority
(`INV repository/design-outside-authority`). The status files may link a
report instead of repeating it, and this file may be named from anywhere,
because a format contract holds no argument.

What does not belong here: current state, which is `docs/status/`; a
sentence someone would like a policy document to carry, which waits in
`docs/policy/candidates/`; and a change with one acceptance criterion and
one pull request, whose evidence goes in the pull request's body. Scratch
thinking that promises nothing stays untracked in `notes/`.

`tool/version-control/work` checks every work item. A failure names its rule
as `W1` to `W7`; the checker's header defines each. It runs on every commit
and in CI. It reads the index, so stage a new pair before running it by hand.

## Scope

A spec has one scope, the scope of its outcome, and that scope names its
directory; the classifier reads the same position, so a Unix-like spec and
its report are a `unixlike` change. The increments of a spec may classify
differently — a Unix-like spec whose procedure lives in `CONTRIBUTING.md` has
a `repository` increment — and each increment's commit and pull request
stays single-scope. Work whose outcome spans scopes is one spec per scope.

An increment is what one evidence lane verifies, not a step of the work. A
spec lists one for the criteria an evaluation decides, one for those only a
host decides, and one for each other scope it owes something in; the report
rows a pull request verifies, the status sentence and the report's end
travel in that pull request and are not increments of their own
(`INV repository/pull-request-spans-an-evidence-lane`).

## Format

Line 1 is `# <Title>`; then a header of `key: value` lines up to the first
blank line, parsed the way decision records are
(`docs/policy/decisions/README.md`); then prose.

`spec.md`:

| Key | Count | Meaning |
|---|---|---|
| `kind` | 1 | `spec`. |
| `date` | 1 | `YYYY-MM-DD` the spec was agreed. |
| `scope` | 1 | `unixlike`, `windows` or `repository`; equal to the directory's. |
| `status` | 1 | `approved`. A spec enters the tree agreed; how far the work has got is the report's to say. |
| `review-by` | 1 | `YYYY-MM-DD`. A spec past it whose report is still pending is reported as overdue. |
| `issue` | 0–1 | `#<n>`, the execution issue, added when implementation starts. |

`report.md`:

| Key | Count | Meaning |
|---|---|---|
| `kind` | 1 | `report`. |
| `spec` | 1 | The path of the spec beside it. |
| `status` | 1 | `pending`, `done`, `abandoned` or `superseded`. |
| `superseded-by` | 0–1 | The path of the spec that replaces this one; required when, and only when, the report is `superseded`. |

## Acceptance

The spec carries a section `## Acceptance` holding one table, a row per
criterion:

```text
| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | <what must be true> | <lane>, <lane> |
```

Ids are `AC<n>` and unique. The lanes are the ones evidence is reported in:
`evaluation`, `build`, `native runtime`, `activation` and `Apply` for a
configuration scope; `fixtures`, `policy checks` and `affected dispatch` for
`repository`. A criterion no check can decide — what a document states, what
remote state was observed — names `review`: its evidence is the reviewer and
the commit or the URL they read, the standing an invariant's `manual`
enforcement has.

The report carries the same section with one row for every criterion and no
other:

```text
| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
```

A row is `pending`, `verified` or `unmet`, and a `verified` row says what
verified it. Evidence is reported per lane and never upgraded: a criterion
that requires a build is not verified by an evaluation.

## Life of a work item

The spec and its report are created in the same commit, the report with
every row `pending`, so no commit holds a spec without the place its evidence
goes. The report ends in exactly one of three states:

| State | Means | Rows |
|---|---|---|
| `done` | Every criterion is verified in its required lanes. | all `verified` |
| `abandoned` | The work stopped. The report says why, how far it got and what it left. | none `pending`; an unmet criterion is stated as `unmet` |
| `superseded` | Another spec replaces this one. The report names it and says what was achieved. | none `pending` |

Once the report exists, a criterion is never removed or weakened in place.
A change is a paragraph in the spec that opens `Amended YYYY-MM-DD` and names
each criterion it touches by its id, so the bar is visibly set before the
work and every move of it is dated. The checker compares the commit being
made, or the range being merged, with its base, and refuses a criterion that
was removed or rewritten — in its text or its lanes — without such a
paragraph. Adding a criterion needs none. A work item is never deleted: a
decision record cites it as the source of what was adopted.

## Carried documents

The documents written in this area before 2026-09-19 keep the kinds and the
headers they were written with — `study`, `plan` and `map`, one or more
`scope` lines, a `status` of `open`, `closed` or `superseded`, and `issue`,
`outcome`, `supersedes` and `superseded-by` lines — and live under
`repository`. `plan` and `map` are not written again; only `spec` and
`report` are held to a single scope. A measurement in a `study` is quoted
with the date and the commit it was taken at, because the tree moves and the
document does not.

## Index

The list is printed from the documents' headers, not kept here:
`tool/version-control/records --table work`
(`INV repository/document-index-generated`).
