# Classify and author a change

## Classify the change

The classifier recognizes three active owners.

- `unixlike` owns Nix, Home Manager, NixOS, WSL guest, and nix-darwin behavior.
- `windows` owns native Windows desired state and reconciliation.
- `repository` owns version-control policy, hooks, CI dispatch, and reusable
  workflow support.

The `common` boundary needs its own contract and checks before it can own
paths. An explicit adoption modifies files owned by the receiving domain.

`repository` is a governance scope, not a fourth configuration domain. It has
no release tag and must not contain platform behavior that belongs to
`unixlike`, `windows`, or `common`.

Each source commit has one owning scope. The classifier answers over the
paths a commit touches. That scope determines ownership and domain release
scope. Check selection follows change effect:
domain documents may select no suite, while repository dispatch changes can
select several suites. Global scans still apply. The
subject's scope is a different thing: it names the domain the change
describes, so `docs(windows)` over `docs/policy/architecture.md`, which classifies
`repository`, is correct. If a common change and its platform adoption are
both needed, land them separately so neither release is synchronously coupled
to the other.

## Branch and commit flow

When starting a task, use one top-level topic when its commits need to be
reviewed together to deliver one result. For example, the implementation of a
command and the repository entry point that exposes it belong to the same
topic. Use separate topics for independently deliverable results.

At topic start, agree on the result and identify any prerequisite that blocks
later work. State what will show that each prerequisite is met. Settle a
foundational policy or interface before relying on it in implementation.
Use the existing [work plan](handoff.md#plan-and-verify-work) when the
dependency needs a durable record. Express actual source dependencies through
commit ancestry.

Master is the release and normal authoring branch. One logical commit normally
stays there. Use `--commits one` for direct master work or `--topic` to name
a topic. Linked worktrees use a named topic. An issue or ordinary PR is
optional.

Agree on the current checkout or a linked worktree before starting. Keep that
choice while continuing the same task and isolate parallel authors.

```sh
tool/configs policy show
tool/configs workflow inspect
tool/configs workflow start --commits one --workspace current
tool/configs workflow start --topic program-supply --workspace current
# If the user selected isolation:
tool/configs workflow start --topic program-supply --workspace linked
```

The start examples are alternatives. Policy show and inspect answer specific
questions; they are not mandatory preliminary commands. Use start for a clean
new task, and inspect existing Git state when resuming or continuing instead
of rerunning start. Top-level topics start at the local master snapshot.
Workflow inspect reports live Git state and the merge destination.

Start ordinary topics as `topic/<outcome>`. Work on existing
`feature/<scope>-<topic>` and `fix/<scope>-<topic>` follows their named scope.

Use `workflow start --workspace linked` to create an isolated workspace.
When a part needs its own branch, pass the immediate parent:

```sh
tool/configs workflow start --parent topic/program-supply --topic inventory --workspace linked
```

This creates `topic/program-supply+inventory` at the parent's current commit.
A deeper branch can start from that branch and append another segment. For
`--workspace current`, run start in the checked-out parent. Integrate each
subtopic into its parent using the [integration procedure](verification.md#local-verification-and-integration).

Continue an existing task on its agreed branch. For an authorized, in-scope
fix after CI fails on a master push, commit the fix on master and follow the
[direct master verification procedure](verification.md#local-verification-and-integration).

Move remaining work from master to a topic only when the maintainer explicitly
chooses that transition. Create the topic in place:

```sh
git switch -c topic/<outcome>
```

Run this on master at its current HEAD with no Git operation in progress.
The new topic keeps staged, unstaged and untracked work in the same checkout;
review `git status` before and after. Preserve all existing master commits and
group the remaining work on the topic.

## Specialized lock refresh

`tool/configs commit [--dry-run] flake refresh [INPUT]` retains the explicit
direct Nix update and confirmed local commit. It requires an untouched lock
and empty index, uses tracked hooks, and leaves a rejected commit staged for
recovery. This is distinct from exclusion-aware `just up`; neither publishes.
Imperative brew/cask/mas editing is retired. Use ordinary authoring for
individual program declarations and their suppliers in the Unix-like provider and for host-owned selection overrides, App Store entries and lifecycle
policy.
