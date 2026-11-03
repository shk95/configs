id: repository/worker-checkpoint
statement: An optional checkpoint is untracked local handoff text saved atomically in the selected workspace, refuses empty or unsafe writes, and never supplies policy, approval, liveness or deletion authority.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/work-session.sh
enforced-by: fixture tool/version-control/session-test
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Decision
