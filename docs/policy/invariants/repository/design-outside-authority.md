id: repository/design-outside-authority
statement: A repository rule does not cite a work document as its authority.
rationale: AGENTS.md § Governance design
enforced-by: tool tool/version-control/design-citations
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/design-documents-outside-the-authority-model.md § Design documents sit outside the authority model
decision: docs/policy/decisions/repository/work-planned-and-verified-in-documents.md § Work is planned and verified in documents, and a branch is one increment

A work document binds only the work it describes. A durable rule belongs in a
decision record or invariant, and a temporary measure in the provisional
registry. A decision record or provisional entry may name the work as its
source; other rule-bearing material cites the adopted result. A candidate
records an observation and an issue records execution, so neither adopts a
rule.

The check is lexical and rests on a distinction the tree already draws: a
citation names a document (`docs/work/` and a file name), while a placement
rule names the directory (`docs/work/` and nothing that could continue a
name). Placement rules can therefore name the directory without borrowing a
work item's argument.

Status files may link a report instead of repeating its evidence, and the map
of the document tree may name a work item. The area's format contract and
roadmap hold no argument, so naming either is not a citation and passes
anywhere.

Accepted limits, which are the reviewer's rather than the check's: a citation
written in words carries no path and passes; a template such as the slug form
in a format contract is not a file name and passes; and permitted locations
are excluded whole rather than by key, so a decision record may name a work
document anywhere in its prose and not only in `source:`.
