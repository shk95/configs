id: repository/mechanical-policy
statement: Mechanical values have one tracked declaration at their owning execution boundary; shared operating values are validated and private agent configuration supplies no project policy.
rationale: AGENTS.md § Governance design
enforced-by: schema tool/version-control/repo_policy.py
enforced-by: tool tool/version-control/policy
enforced-by: fixture tool/version-control/test-mechanics.py
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Mechanical operation

Remote and native adoption evidence is distinct from local fixture proof.
