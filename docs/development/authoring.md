# Classify and author a change

## Classify the change

Every change belongs to one of these scopes:

- `unixlike`: Nix, Home Manager, NixOS, WSL guest, or nix-darwin behavior.
- `windows`: native Windows desired state and reconciliation.
- `common`: explicitly platform-neutral material with its own contract.
- `adopt`: an explicit copy or pinned import from one domain into another.
- `repository`: version-control policy, hooks, CI dispatch, or reusable agent
  workflow support with no configuration or deployment output.

`repository` is a governance scope, not a fourth configuration domain. It has
no release tag and must not contain platform behavior that belongs to
`unixlike`, `windows`, or `common`.

One scope per source commit and topic. Master may accumulate independently
scoped outcomes. A commit's
scope is the classifier's answer over the paths it touches; it determines
ownership and domain release scope. Check selection follows change effect:
domain documents may select no suite, while repository dispatch changes can
select several suites. Global scans still apply. The
subject's scope is a different thing: it names the domain the change
describes, so `docs(windows)` over `docs/policy/architecture.md`, which classifies
`repository`, is correct. If a common change and its platform adoption are
both needed, land them separately so neither release is synchronously coupled
to the other.

## Branch and commit flow

Master is the release and normal authoring branch. One logical commit normally
stays there; several commits for one coherent same-scope result use a
master-based topic and no-ff integration. A selected linked worktree also uses
a topic for a one-commit task. An issue or ordinary PR is optional.

For new work, ask current checkout versus linked worktree if the user has not
chosen. Keep that choice when continuing the same task; ask again only if it
must change. Parallel authors need isolation. An explicit tool argument is not
evidence of an unanswered preference.

```sh
tool/configs policy show
tool/configs workflow inspect
tool/configs workflow start --scope repository --commits one --workspace current
tool/configs workflow start --scope repository --commits many --topic example --workspace current
# If the user selected isolation instead:
tool/configs workflow start --scope repository --commits many --topic example --workspace linked
```

The start examples are alternatives. Policy show and inspect answer specific
questions; they are not mandatory preliminary commands. Use start for a clean
new task, and inspect existing Git state when resuming or continuing instead
of rerunning start. Start records the chosen scope, count, workspace and base in Git-local
operation data, visible through workflow inspect. The record is not approval
or evidence of process liveness. Start neither fetches nor changes master; topic bases use the selected local master snapshot. Inspect
and explicitly synchronize remote history when needed.
Topic names are `feature/<scope>-<topic>` or `fix/<scope>-<topic>`.

Use `workflow start --workspace linked` to create an isolated workspace;
there is one creation path. Primary and linked workspaces use identical hooks
and checks. Source commits remain single-scope.

If direct master work grows into several logical commits, use an authorized
in-place transition instead of rerunning clean-start initialization:

```sh
git switch -c feature/<scope>-<topic>
```

Run this on master at its current HEAD with no Git operation in progress.
The new topic keeps staged, unstaged and untracked work in the same checkout;
review `git status` before and after. If master already contains a completed
commit, keep it there and group the remaining work on the topic. Do not reset
master or rewrite accepted history to retroactively regroup it. The start
record, if present, remains the original estimate rather than new approval.
