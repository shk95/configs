id: windows/capture-publishes-through-dev
statement: A captured host change reaches shared history only through one pull request against dev from a topic branch, never as a commit on dev or master; a branch capture creates for it starts at the remote tip of dev, a rejected push leaves every commit local, and no branch that is dev, master or the current one is ever deleted.
rationale: docs/architecture.md § Version control and releases
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/status.md § Capture moves a host change into desired state

Capture is the one flow that writes history from a Windows host, so it is
held to the same one-way flow every other change follows. The branch
planner refuses on `master` before reading the remote; on `dev` it cuts a
topic branch from `origin/dev` and leaves `dev` where it was, and on any
other branch it commits where it stands. The publish step pushes, opens one
pull request against `dev`, refuses a head already proposed against another
base, arms auto-merge once, reuses a pull request already open from the
same head rather than opening a second, and stops at a rejected push with
every commit local. The prune step deletes only branches `origin/dev`
already contains and never the current branch, `dev` or `master`. Every
fixture runs against throwaway repositories under the suite's isolation
script. The Unix-like helper follows the same flow under an entry the
repository half of this change registers, `publish-through-dev`; the two
are copies by the copy-over-sharing rule and may diverge.
