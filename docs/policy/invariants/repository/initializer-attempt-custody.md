id: repository/initializer-attempt-custody
statement: Initial publication requires a privately retained authorization for one independently observed source and run attempt, never reissues that authority, and permits later reconciliation only to observe exact original history without resuming incomplete publication.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema tool/version-control/release-initialize.py
enforced-by: fixture tool/version-control/test-release-operating-history
owner: repository maintainer
decision: docs/policy/decisions/repository/authenticated-release-transport.md § Private one-shot initializer custody

A private Environment certificate binds the exact original desired proposal, roles,
record construction and numeric run/attempt. Missing/deleted Actions rows, job
failure or empty refs supply no publishing authority. Original seed and deterministic
child verification precede observing initialized state. Source fixtures do not prove
private review, Environment custody, deployed permissions or operating enablement.
