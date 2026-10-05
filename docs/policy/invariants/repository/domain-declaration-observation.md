id: repository/domain-declaration-observation
statement: A declaration observer preserves complete bounded original package and declaration bindings, observes only independently fixed source and review identities, refuses incomplete or moving evidence and returns data without granting introduction, approval, runtime or effect authority.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema tool/version-control/release-domain-declaration.py
enforced-by: fixture tool/version-control/test-domain-declaration
owner: repository maintainer
decision: docs/policy/decisions/repository/domain-declaration-observation.md § Decision

Original declaration bytes and their historical staging are distinct from the
independently accepted review source. Matching hashes and a run-scoped review
observation do not prove private introduction, completed staging, current effect
eligibility, actual hold, source approval or native/runtime qualification.
