# Design documents sit outside the authority model

date: 2026-09-12
scope: repository
status: accepted
reopen-when: an authority document needs to cite a design document directly, or a year passes with no document under `docs/design/` producing an outcome.

Everything this repository tracks is a result. `AGENTS.md` and
`docs/architecture.md` hold rationale, `invariants/` what must remain true,
`docs/decisions/` the choices, `docs/candidates/` an observation waiting to
become a sentence, `docs/status.md` the state, and `tool/` the enforcement.
Nothing tracked holds the work that produced any of them: the survey, the
spike and its measurements, the argument that weighed three layouts, the plan
that predicted what each step would cost. That work had four homes, none of
them the repository — a private artefact URL, an agent's memory, an untracked
`notes/` the repository's own charter says not to read, and GitHub issues the
repository already refuses authority to.

It showed. `docs/decisions/unixlike-domain-owns-its-tree.md` had to write "a
spike on 2026-09-10 found" with no path to name, and picking the work back up
a session later meant recovering a link out of one machine's memory.

`docs/design/` is that work's home, and it carries no authority. A design
document is an argument: it observes the tracked tree and quotes it with a
date and a commit, and it binds nothing by existing. The repository adopts
from it only through an inlet that is reviewed on its own terms — a decision
record, a promoted candidate, a registered provisional measure, or an issue —
and the inlet names the document as its source, which is what `source:` in a
decision record has always been for. `INV repository/design-outside-authority`
holds the direction of that traffic: an authority document, a registry entry
or a piece of executable policy may not cite a document here, so a rule can
never come to rest on an argument nobody accepted.

The division is not between kinds of judgement. Deciding where the repository
should go is proposed outside and becomes internal the moment an inlet accepts
it; deciding how to satisfy an accepted constraint is internal and stays in
the commit, the comment and the record. What the internal side hands back is
not a report but its ordinary output — commits, check evidence, a
`docs/status.md` line — and the outside reads that directly. A third kind of
document, written by the work to describe itself, is exactly what this
decision refuses: it would be neither argument nor authority, and nothing
would own it.

Rejected:

- A separate repository, the way cross-project methods live in the sibling
  `skills` project. That project's admission test is that the material
  contains no repository decision, path convention, branch name,
  infrastructure identity or current state (`AGENTS.md`, "Governance
  design"). A design document is made of those, and a record there could not
  be cited by a tracked path.
- Tracking `notes/`. It is ignored so that free-form thinking stays out of a
  public history and out of every ignore-aware search, which is the whole of
  what it offers; tracking it would remove that and put unreviewed text in
  the same tree as reviewed text.
- Folding the documents into `docs/decisions/`. A record is one choice, and
  the index is readable because that is true. An argument that yields two
  records, two candidates and a milestone is not one choice.
- Folding them into `docs/candidates/`. A candidate is one sentence's
  observation and is deleted on promotion because its content moves into the
  text it proposed. A design document is cited after adoption and has to
  survive it.
- Leaving them in issues, a wiki or Discussions. Milestones are already a
  planning surface and not a source of authority; none of these is reviewed
  as a diff, versioned with the code, or citable by path.

What it costs. A seventh repository-wide scan runs on every commit and in CI.
The tree gains a directory whose contents are never authoritative, which a
reader has to learn to read as argument and an agent must not follow as rule;
the charter in `docs/design/README.md` is the whole of that warning. Documents
are never deleted, so the directory only grows and `superseded` is its only
retirement. Porting the three documents that opened the area costs a
translation: they were written as Korean HTML artefacts, and the repository is
public and its text is English (`CONTRIBUTING.md`, "Documentation
ownership"). And the checked rule
is lexical: it separates citing a document from naming the directory, so a
citation written in words rather than as a path passes, and a reviewer is what
catches it.
