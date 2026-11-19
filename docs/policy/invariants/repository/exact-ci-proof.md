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
It identifies the event, source base and head, tested checkout and tree, and
actual workflow revision and file. A successful required job on its selected
platform covers its unconditional steps when the workflow matches the
reviewed base. A changed workflow requires proof that these required steps
ran successfully. CI rejects failure-tolerance declarations in its workflow
definition. The incoming policy and topic source checks each form a required
execution unit. Selected steps that can be skipped within a job always require
their own success. A PR binds the synthetic checkout to the reviewed parents.
A diagnostic job failure does not invalidate successful required checks.
Missing or duplicate required jobs invalidate the proof.
A candidate dispatch runs the definition from the reviewed master. A matching
master push can reuse the provider suites with identical tree and workflow
definition from its PR. That push owns its incoming checks. Remote native
adoption and provider consumer verification are separate evidence.
