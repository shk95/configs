id: repository/local-development-integration
statement: Ordinary work uses master, multiple logical commits are grouped on a topic and integrated by a verified exact-base/head no-ff merge, and helpers never publish or prune implicitly.
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
