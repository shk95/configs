id: repository/topic-source
statement: An optional master pull request uses a same-repository top-level topic with owned changes, and an automated input patch also satisfies its bounded current-master contract.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool tool/version-control/topic-source
enforced-by: schema tool/version-control/topic_scope.py
enforced-by: fixture tool/version-control/test
enforced-by: fixture tool/version-control/test-workflow.py
enforced-by: fixture tool/version-control/test-release.py
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Decision

The incoming range audit checks ownership per source commit. Existing
scope-named topics also retain their branch-wide scope check. Direct master
commits need no pull request.
