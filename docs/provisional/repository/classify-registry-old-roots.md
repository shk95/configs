id: repository/classify-registry-old-roots
kind: workaround
statement: The classifier and the local gate's selector still answer for the invariant and provisional registries' roots as they stood before the registries moved under `docs/`, so a range that spans the move can be classified and pushed.
since: 2026-09-19
exit-when: The commit that moved the registries under `docs/` is an ancestor of `master`, so no pull-request or promotion range spans the deletion of the old roots.
watch: manual
review-by: 2026-10-31
issue: #259
decision: docs/policy/decisions/repository/documents-classified-by-scope.md § Documents are classified by the scope directory that holds them
owner: repository maintainer

The move deleted every file under the two old roots. That deletion sits
inside every pull-request range and the promotion range that spans the move,
the classifier refuses a range holding a path it cannot place, and an
unclassified path cannot be pushed. The measure replaces nothing: without it
the move could not have been pushed or promoted. It costs four case arms that
name directories which no longer exist and one alternation in the selector's
document filter, each of which a reader would otherwise take for live policy.

Every disposable line carries the tag for this entry. The set is the old-root
arms at the end of the case statement in `tool/version-control/classify`, the
old roots in the document filter of `tool/dispatch/select`, and the fixtures
in `tool/version-control/test` that prove both. The arm for the removed common
scope's placeholder shares a line with them; the removal it served reached
`master` earlier, so it goes in the same retirement.

On review, ask one thing: is the moving commit an ancestor of `origin/master`?
If it is, retire the measure — delete this entry, the tagged lines and this
scope directory if it is then empty, in one repository commit. If no promotion
has happened by the review date, extend it; nothing else can end it.
