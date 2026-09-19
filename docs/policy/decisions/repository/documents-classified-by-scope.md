# Documents are classified by the scope directory that holds them

date: 2026-09-19
scope: repository
status: accepted
issue: #259
reopen-when: a document area needs an owner its directory cannot express, or a document move again has to cross scopes in one commit.

The repository's documents stood in three root directories — `docs/`,
`invariants/` and `provisional/` — that form one flow: observe, adopt,
enforce, beside one code-side registry, the model, current state and design
arguments. Everything under `docs/` classified as `repository`, although of
the 42 decision records 13 were Unix-like, 14 Windows and one both, and the
status file and the definition of done already held one section per domain.
One scope per commit is policy, so a domain change that recorded its state or
its evidence item needed a second, repository change, and `CONTRIBUTING.md`
carried a standing exception for the one pair that could not be separated.

Everything the repository writes about itself now lives under `docs/`:
`docs/policy/` for the model, the definition of done, the candidates, the
decision records and the invariant registry; `docs/provisional/`,
`docs/work/`, `docs/status/` and `docs/reference/` beside it. Each area has
one scope position — the directory directly under a registry or `docs/work/`,
the file name under `docs/status/` and `docs/policy/definition-of-done/` — and
the scope named there owns the document. Anything else inside an area is
unclassified: a scope position that names no domain, as an unknown scope
under the invariant registry already was, a scope name in another position,
or a file beside the area's format contract. A document outside the areas is
repository's. A document that spans
scopes lives under `repository` and lists every scope in its header.
`docs/policy/architecture.md` stays one repository file: it is the
cross-domain model, and a domain invariant that needs a new rationale still
edits it, which is accepted as rare. The two-scope exception in
`CONTRIBUTING.md` is gone, because an invariant entry and its evidence item
now sit in the same scope.

No document area keeps a hand-written list of its own documents
(`INV repository/document-index-generated`). `tool/version-control/records
--table <area>` prints one from the headers, as the invariant and provisional
checkers already did for their registries.

Ownership is not selection. `tool/dispatch/select` leaves documents out of
the scopes it reads, so a Unix-like status line selects no Unix-like suite
locally (`INV repository/local-gate-selects-by-effect`). CI's job selection
follows classification, so the same change runs that domain's CI job; the
cost is accepted.

The move itself is the one commit this decision exempts from the one-scope
rule. Moving a document into a domain's directory touches two scopes, and so
does rewriting the pointers the checkers validate — the invariant entries'
rationale and decision paths, the definition-of-done path, the provisional
entry's decision path and the hygiene allow list — and a rename alone fails
those checks. The commit that lands this record therefore moves every
document, rewrites every pointer and moves every tool to the new roots at
once, across `repository`, `unixlike` and `windows` paths. It creates no
configuration output, and CI selects every lane the change touches, so the
exception loses no evidence. It also narrows
`docs/policy/decisions/unixlike/unixlike-domain-owns-its-tree.md`: besides
`.envrc` and the `Justfile`, the Unix-like domain's documents are the third
thing the classifier answers `unixlike` for outside `unixlike/`. The comments in the domain trees that cite a
moved path follow as ordinary single-scope changes. The classifier keeps the
registries' old roots until the move has reached `master`, because their
deletion sits inside every range that spans it.

Rejected:

- Keeping `docs/` flat and reading ownership from each document's `scope:`
  header. The classifier maps paths, and a header read would make it parse
  every document it classifies.
- A provisional measure that classified the whole new tree as `repository`
  for the migration and moved it in five steps. It needs its own decision
  record and issue in any case, withholds the domain suites while it stands,
  and adds two steps to reach the same tree.
- Moving the registries under their domains' trees (`unixlike/invariants/`).
  It follows domain ownership more literally, and scatters the documents a
  reader looks for together across three roots again.
