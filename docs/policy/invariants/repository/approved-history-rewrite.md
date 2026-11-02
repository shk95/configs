id: repository/approved-history-rewrite
statement: History replacement requires an isolated writer capability, explicit human approval bound to a fresh exact-source operation, preserved recovery and an exact expected-old lease without changing branch protection.
rationale: AGENTS.md § Governance design
enforced-by: schema tool/version-control/history_rewrite.py
enforced-by: tool tool/version-control/history-rewrite
enforced-by: fixture tool/version-control/test-mechanics.py
enforced-by: manual The maintainer verifies actual isolated App, protected environment reviewers, credential separation and remote operation evidence before adoption
enforced-by: schema tool/version-control/recovery.py
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Mechanical operation

Default force denial remains valid. An adopted exception uses an active
exact-master non-fast-forward branch ruleset with only the isolated App in
its bypass list, combined with classic administrator/deletion safeguards.
Unknown effective rules, hidden actors or insufficient API permissions refuse.
Preflight is read-only and grants no approval. Remote and native adoption
evidence is distinct from local fixture proof.
