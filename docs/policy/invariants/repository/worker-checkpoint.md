id: repository/worker-checkpoint
statement: A worker checkpoint is untracked local execution data written only in its isolated workspace, refuses invalid lifecycle transitions and empty handoffs, and does not authorize integration or deletion.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/work-session.sh
enforced-by: fixture tool/version-control/session-test
decision: docs/policy/decisions/repository/local-development-workflow.md § Decision
decision: docs/policy/decisions/repository/external-work-role-orchestration.md § Decision

The local tool cannot prove session liveness or semantic completeness of a
handoff. The contributor procedure requires reviewing actual Git state before
resuming or reclaiming a workspace, with remote evidence only when relevant
to the requested operation or preservation review. Missing local state is
unknown, never proof of completed delivery. Role adherence itself is agent
procedure, not an OS sandbox or credential boundary; local dev preserves
integration, while protected master supplies remote admission.
