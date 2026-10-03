id: repository/authenticated-release-transport
statement: Operating transport binds independently observed entry and evidence to immutable retained context, durably records intent before external effects, refuses incomplete or conflicting observations and foreign cancellation targets, and does not infer operating enablement or certification from source fixtures.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema tool/version-control/release-transport.py
enforced-by: schema tool/version-control/release-transport-retained.py
enforced-by: fixture tool/version-control/test-release-transport
owner: repository maintainer
decision: docs/policy/decisions/repository/authenticated-release-transport.md § Decision

The separate trusted transport inventory does not replace or expand historical
semantic packages. Exact original history and semantic projections are checked by
the retained loader. Fixture endpoint responses are explicitly synthetic. The
operator preflight and source workflows stay disabled; real deployment and actual
permission, protection and notification delivery require separate operating proof.

Generic retained proposals derive framing, preserve prior transcript obligations
and undergo complete prospective global replay before journal publication. Fresh
entry/owner/head/job/stop observations bind proposal and publication. Failed or
outstanding proposals and uncertain journal writes fence further proposals/retries
within the instance; source tests do not certify durable cross-run recovery.
