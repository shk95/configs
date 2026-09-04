id: windows/no-inherited-git-context
statement: The Windows suite reaches only the repositories it creates; a repository context inherited from its caller is dropped before any command runs.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

A hook run from a linked worktree carries an absolute repository path in its
environment, and a fixture that runs its commands against a temporary
directory silently acts on that repository instead. The first push of this
change did exactly that to the maintainer's clone. The isolation script drops
the inherited context; the fixture runs a command under a decoy context both
with and without it, so the defence and the hazard stay visible together.
