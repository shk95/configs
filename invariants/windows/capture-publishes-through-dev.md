id: windows/capture-publishes-through-dev
statement: A captured host change reaches shared history only as a topic branch cut from the remote tip of dev through one pull request against dev, never as a commit on master; a rejected push leaves it local, and no branch that is dev, master or the current one is ever deleted.
rationale: docs/architecture.md § Version control and releases
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/status.md § Capture moves a host change into desired state

Capture is the one flow that writes history from a Windows host, so it is
held to the same one-way flow every other change follows. The branch
planner refuses on `master` before reading the remote, cuts the topic branch
from `origin/dev` and leaves `dev` where it was; the publish step pushes,
opens one pull request against `dev`, arms auto-merge once, reuses a pull
request already open from the same head, and stops at a rejected push with
every commit local; the prune step deletes only branches `origin/dev`
already contains and never the current branch, `dev` or `master`. Every
fixture runs against throwaway repositories under the suite's isolation
script. The Unix-like helper follows the same flow under the
repository-scope entry `publish-through-dev`, registered by the repository
half of this change; the two are copies by the copy-over-sharing rule and
may diverge.
