id: repository/design-outside-authority
statement: Nothing that carries authority cites a design document; only an adoption record names one as its source.
rationale: AGENTS.md § Governance design
enforced-by: tool tool/version-control/design-citations
enforced-by: fixture tool/version-control/test
decision: docs/decisions/design-documents-outside-the-authority-model.md § Design documents sit outside the authority model

A design document argues for a direction and binds nothing. If a rationale
paragraph, a registry entry, a procedure or a script could rest on one, the
argument would acquire the force of the thing citing it without ever passing
an inlet, and the repository would be enforcing a direction nobody accepted.
The four inlets — a decision record, a candidate, a provisional entry, an
issue — are reviewed on their own terms and are where a document is named as
a source.

The check is lexical and rests on a distinction the tree already draws: a
citation names a document (`docs/design/` and a file name), while a placement
rule names the directory (`docs/design/` and nothing that could continue a
name). That is the same separation `CONTRIBUTING.md` already makes for the
other document directories, which is why the ownership table, the placement
paragraph in `AGENTS.md` and this entry's own statement can all say where
design documents live without citing one.

Accepted limits, which are the reviewer's rather than the check's: a citation
written in words carries no path and passes; a template such as the slug form
in a format contract is not a file name and passes; and the inlets are
excluded whole rather than by key, so a decision record may name a design
document anywhere in its prose and not only in `source:`.
