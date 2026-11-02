id: repository/topic-source
statement: An optional master pull request uses a same-repository topic whose changes belong to its named scope; an automated input patch also satisfies its bounded current-master contract.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool tool/version-control/topic-source
enforced-by: schema tool/version-control/topic_scope.py
enforced-by: fixture tool/version-control/test
enforced-by: fixture tool/version-control/test-workflow.py
enforced-by: fixture tool/version-control/test-release.py
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Decision

Direct commits need no pull request. The optional topic check does not impose PR admission on ordinary work.
