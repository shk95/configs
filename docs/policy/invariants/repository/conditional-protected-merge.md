id: repository/conditional-protected-merge
statement: An unattended protected merge is admitted only for an allowlisted authorized actor and an unchanged same-repository pull request whose current strict protection and newest exact-source required CI pass, and its confirmed result remains recoverable without a duplicate write.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/conditional-merge.py
enforced-by: fixture tool/version-control/test-conditional-merge.py
enforced-by: manual docs/policy/definition-of-done/repository.md
owner: repository maintainer
decision: docs/policy/decisions/repository/conditional-protected-merge.md § Decision

The expected-head merge condition is atomic; the target identity is not. Both
branch protections stay strict, and target-race qualification remains an
explicit evidence item before the disabled writer is enabled.
