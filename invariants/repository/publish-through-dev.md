id: repository/publish-through-dev
statement: A published change reaches shared history only through one pull request against dev from a topic branch, never as a commit on dev or master; a branch the helper creates for it starts at the remote tip of dev, a rejected push leaves the commit local, and no branch that is dev, master or the current one is ever deleted.
rationale: docs/architecture.md § Version control and releases
enforced-by: tool tool/version-control/commit
enforced-by: fixture tool/version-control/test

The commit helper is the one tool that writes history on a contributor's
behalf, so it is held to the same one-way flow every change follows. On
`master` it refuses before consulting anything; on `dev` it cuts a topic
branch from `origin/dev`, and on any other branch it commits where it
stands. Publishing pushes that branch, opens one pull request against
`dev`, arms auto-merge once, reuses a pull request already open from the
same head rather than opening a second, refuses a head already proposed
against another base, and stops at a rejected push with the commit local
and no pull request opened. Pruning deletes only branches `origin/dev`
already contains and never the current branch, `dev` or `master`. "Never
a commit on `dev`" has no assertion of its own: it follows from the helper
branching before it commits whenever it stands on `dev`, and the case run
from `dev` after a publish would meet the helper's own "dev is not at
origin/dev" refusal if that were ever false. The
Windows capture flow follows the same rule under
`INV windows/capture-publishes-through-dev`; the two are copies by the
copy-over-sharing rule and may diverge.
