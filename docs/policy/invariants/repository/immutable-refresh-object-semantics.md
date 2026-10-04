id: repository/immutable-refresh-object-semantics
statement: Immutable refresh effects bind complete bounded original lock-only construction, deterministic object identities and observed prerequisites, refuse uncertain ordering and cross-batch preparation reuse, and preserve each historical package's original semantics without inferring operating or domain approval from supplied data.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema tool/version-control/release-control-package/adapter.py
enforced-by: schema tool/version-control/release-control-loader.py
enforced-by: fixture tool/version-control/test-release-control.py
owner: repository maintainer
decision: docs/policy/decisions/repository/immutable-refresh-object-semantics.md § Decision

Positive disposable Git and synthetic observations prove signed original-base,
canonical generated construction, ordered effects/recovery and original replay.
Negative fixtures cover incomplete/contaminated objects, unsupported updates,
wrong metadata/declarations, missing dependencies, unknown effects and foreign
preparation consumption. Actual API/producer/declaration custody remains separate.
