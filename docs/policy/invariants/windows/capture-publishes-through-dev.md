id: windows/capture-publishes-through-dev
statement: A captured host change reaches shared history only through one pull request against dev from a topic branch, never as a commit on dev or master; a branch capture creates for it starts at the remote tip of dev, a rejected push leaves every commit local, a publish resumed by a run that captured nothing carries only commits capture made that change desired state alone and never resumes from dev, master or a detached head, and no branch that is dev, master or the current one is ever deleted.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/policy/decisions/windows/capture-moves-host-changes.md § Capture moves a host change into desired state

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

A capture's commit makes the host read as unchanged, so a rerun after a
publish that did not finish captures nothing. With `-Publish` such a run
resumes the publish on a topic branch that carries commits beyond
`origin/dev`, whether or not its upstream already has them, and only when
every one of those commits has a single parent, the subject capture gives
its commits, and changes under `windows/desired` alone; any other commit
refuses the run. `dev` and `master` never resume, and on `dev` the run names
a local capture branch that still carries commits. A branch origin already
has at the local tip is not pushed again, so the resumed pull request says
that nothing was pushed and no hook ran, and that its commits came from an
earlier run, rather than showing a placeholder (#241).
