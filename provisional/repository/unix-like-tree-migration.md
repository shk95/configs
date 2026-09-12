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
of `tool/version-control/domain-reads`, the `unixlike_check` function in
`.githooks/evidence` with its two call sites in `.githooks/pre-commit` and
`.githooks/pre-push`, the `checks` step in the Unix-like CI job and the ten
lines that read its output, the fixture cases in
`tool/version-control/test` that assert the old spellings still answer and
that a check is resolved at either location, the `unixlike_path` function in
`tool/version-control/commit` with the four paths it resolves, the overlay
path the zellij watcher reads, the second pattern in each of `.gitattributes`
and `.gitignore`, and the second allowlist entry in `.claude/settings.json`,
and this entry.

Classification and resolution are two halves and the first shipped without
the second, which #219 would have hit as a merge failure. Knowing where a
path belongs does not tell a hook where to find an executable: the hooks
resolve `tool/checks/<name>` by literal path, and CI names each check by
path. Unresolved, `pre-commit` would have reported every Unix-like check
unverified and passed, which loses evidence more quietly than failing, and
the Unix-like CI job would have failed on a missing file.

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
