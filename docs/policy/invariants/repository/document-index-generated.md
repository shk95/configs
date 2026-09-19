id: repository/document-index-generated
statement: No document area keeps a hand-maintained list of its own documents; the list is printed from their headers.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/records
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/documents-classified-by-scope.md § Documents are classified by the scope directory that holds them

A list kept by hand in an area's README makes every new record an edit of a
repository file, so a domain's decision could not land in its own scope, and
it drifts from the files it names because nothing reads it. The check is
lexical: no line of the decision, candidate or work area's README names one
of that area's documents by its file name. A file name written as a template
(`<slug>.md`) names no document and passes.
