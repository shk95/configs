id: repository/conditional-protected-merge
statement: An unattended protected merge is admitted only for an allowlisted authorized actor and a same-repository pull request whose reviewed source is unchanged, whose current strict protection and newest exact-source required CI pass, and whose only permitted dev head extensions are bounded deterministic merges of accepted dev history; confirmed results remain recoverable without duplicate writes.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/conditional-merge.py
enforced-by: fixture tool/version-control/test-conditional-merge.py
enforced-by: manual docs/policy/definition-of-done/repository.md
owner: repository maintainer
decision: docs/policy/decisions/repository/conditional-protected-merge.md § Decision

On dev base drift, only the bounded deterministic integration chain defined by
the adopted decision may extend the approved source head. GitHub's update API
CASes the PR head, not the dev base; current-base exact-source CI and strict
protection remain required. Both branch protections stay strict, and live
target-race qualification remains an explicit evidence item before the
disabled writer is enabled.
