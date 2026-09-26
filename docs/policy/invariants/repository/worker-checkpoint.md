id: repository/worker-checkpoint
statement: A worker checkpoint is untracked local execution data written only in its isolated workspace, refuses invalid lifecycle transitions and empty handoffs, and does not authorize integration or deletion.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/work-session.sh
enforced-by: fixture tool/version-control/session-test
decision: docs/policy/decisions/repository/github-agent-workflow.md § GitHub-centered agent workflow

The local tool cannot prove session liveness or semantic completeness of a
handoff. The role skills require reviewing Git and remote evidence before
resuming or reclaiming a workspace. Missing local state is unknown, never
proof of completed delivery. Role adherence itself is agent procedure, not an
OS sandbox or credential boundary; protected dev supplies the remote gate.
