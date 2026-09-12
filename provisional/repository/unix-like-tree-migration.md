id: repository/unix-like-tree-migration
kind: workaround
statement: The classifier, the check dispatcher and the domain-read scan answer for the Unix-like tree's current locations and for `unixlike/` at the same time, so the tree can move without a commit that no tool classifies.
since: 2026-09-12
exit-when: The Unix-like tree has merged under `unixlike/` and nothing remains at the old locations.
watch: manual
review-by: 2027-03-11
issue: #218
decision: docs/decisions/unixlike-domain-owns-its-tree.md § The Unix-like domain owns its tree
owner: repository maintainer

A path the classifier answers `unclassified` for cannot be committed, and the
three tools are the only map. A single commit that moved the tree and taught
the tools about it would pass, but it would be `repository` and `unixlike` at
once, which is the two-scope commit `CONTRIBUTING.md`, "Branch and commit
flow", refuses. So the tolerance comes first, the move second, and the
removal third; this entry is what keeps the middle state from becoming the
permanent one.

Every disposable line carries `PROV repository/unix-like-tree-migration`. The
set is one arm of `tool/version-control/classify`, one `case` block in
`tool/dispatch/select`, the two `scan` calls and the code map in the header
of `tool/version-control/domain-reads`, the fixture cases in
`tool/version-control/test` that assert the old spellings still answer, and
this entry.

Two root paths are not part of the measure and carry no tag: `.envrc`,
because direnv reads it at the root, and the `Justfile`, because where it
belongs is a separate decision. Both stay in the permanent arm.

`watch` is `manual` because the signal is #219 merging rather than a file
changing. `unixlike/flake.nix` would be the natural path to watch and cannot
be, since a watch must be indexed and that path does not exist until the
measure is nearly over.

Retirement is #221, one commit that deletes the tagged set above together
with this entry. Its order is fixed from outside: the deletion of the old
paths is itself unclassified while they are still inside an open pull-request
range, so it opens only after the move has merged into `dev`
(`docs/architecture.md`, "Common domain").

On review, run `tool/version-control/classify --files modules/bat.nix` and
the same for `unixlike/modules/bat.nix`. Two `unixlike` answers mean the
measure is still carrying both trees and the move has not finished; an
`unclassified` answer for the first means the measure is already gone and
this entry should have gone with it.
