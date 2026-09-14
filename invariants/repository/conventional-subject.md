id: repository/conventional-subject
statement: A non-merge commit subject is a Conventional Commit of at most seventy-two characters.
rationale: docs/architecture.md § Version control and releases
enforced-by: tool .githooks/commit-msg
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test

The commit-message hook is the owner of the grammar, including which
subjects Git writes itself and are exempt. `tool/version-control/audit`
asks the hook rather than keeping a pattern of its own, so history audit and
the commit gate cannot disagree.

2026-09-14 (#243): the merge gate judges a pull request's own commits. The
history audit walked only `dev`, which in a `pull_request` run is the base,
so a pull request's commits were first read by the `push` run on `dev` after
the merge, when the subject was already permanent history; a clone without
the tracked hooks, or a `--no-verify` commit, reached a pull request
unchecked. `audit --history` now also takes the revisions a caller is about
to publish and judges their non-merge subjects with `dev`'s through the same
hook. The workflow names `HEAD`, the commit under test, which for a pull
request is the merge GitHub would make; `.githooks/pre-push` names the tips
it pushes. Deriving the range as `HEAD --not origin/dev` whenever `HEAD` is
not `dev` was rejected because pre-push runs the same audit and a push need
not carry `HEAD`: a refused subject on the checked-out branch would block a
push of another branch, which is clone state the local gate must not judge
(`INV repository/local-gate-selects-by-effect`), and one on the pushed
branch would go unread. A base argument was not needed either: the walk is
the union with `dev`, so a promotion pull request, whose non-merge commits
are already on `dev`, adds nothing to read, and a `push` run on `dev` names
the commit `dev` already resolves to. Pull-request titles and the merge
commits GitHub writes are not judged.
