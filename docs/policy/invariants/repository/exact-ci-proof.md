id: repository/exact-ci-proof
statement: External verification binds each claimed check to a successful same-repository run attempt, the actual workflow definition, its execution platform and the exact reviewed source and event.
rationale: AGENTS.md § Governance design
enforced-by: schema tool/version-control/github_proof.py
enforced-by: schema .github/scripts/ci-source.py
enforced-by: schema .github/scripts/ci-reuse.py
enforced-by: fixture tool/version-control/test-mechanics.py
enforced-by: fixture tool/version-control/test-release.py
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Mechanical operation

Local integration and bounded publication read the same attempt-aware evidence.
It identifies the event, source base and head, tested checkout and tree, actual
workflow revision and file, and required jobs and successful steps on their
selected platforms. A PR binds the synthetic checkout to the reviewed parents.
A candidate dispatch runs the definition from the reviewed master. A matching
master push can reuse the provider suites with identical tree and workflow
definition from its PR. That push owns its incoming checks. Remote native
adoption and provider consumer verification are separate evidence.
