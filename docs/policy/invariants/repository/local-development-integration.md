id: repository/local-development-integration
statement: Integration helpers merge a top-level topic into master and a subtopic into its immediate parent using reviewed source and destination commits, without publishing or pruning implicitly.
rationale: AGENTS.md § Governance design
enforced-by: tool tool/worktree.sh
enforced-by: tool tool/version-control/commit
enforced-by: tool tool/version-control/workflow
enforced-by: schema tool/version-control/topic_scope.py
enforced-by: tool .githooks/pre-push
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test-local-workflow
enforced-by: manual The reviewer confirms logical commit grouping and explicit Git authorization
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Decision

Integration preserves both parents and the source topic name. The top-level
topic is the unit for combined verification. The reviewer confirms the
coherent outcome, any blocking prerequisite and its completion condition, and
the authorization to integrate.

An optional candidate plan exposes the same ordered steps consumed by check.
Planning executes no checks or hosted proof and supplies no mutation authority.
