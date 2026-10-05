id: repository/public-refresh-object-transport
statement: Immutable object effects require exact retained construction, complete independent typed proof and observed prerequisites, and private publication accepts a new logical head only after verified original object delivery and complete retained replay; uncertain effects or delivery fence continuation without retry authority.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema tool/version-control/release-public-objects.py
enforced-by: schema tool/version-control/release-transport.py
enforced-by: schema tool/version-control/release-transport-retained.py
enforced-by: fixture tool/version-control/test-release-transport.py
owner: repository maintainer
decision: docs/policy/decisions/repository/public-refresh-object-transport.md § Decision

Disposable Git and synthetic fixed API responses prove positive object publication,
signed-original structural comparison, separate original object stores and repeated
publication. Incomplete proof, masked absence and failed local delivery refuse or
fence. Source proof never establishes actual credentials, operation or host effects.
