id: repository/release-inspection-without-authority
statement: Release inspectors and waiters bind public run observations to actual source and attempts, receive no operating credential or private connection, and never turn completion or elapsed waiting into ownership, approval, cancellation or operating certification.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema tool/version-control/release-inspect.py
enforced-by: fixture tool/version-control/test-release-inspect
owner: repository maintainer
decision: docs/policy/decisions/repository/authenticated-release-transport.md § Credential-free public inspection

The inspector has an independent execution and no writer concurrency or
Environment. Public metadata observations are conservative: incomplete,
foreign, moving or ambiguous data refuse. A completed run observation is
not a retained owner transition; the trusted writer performs its own fresh
authenticated reconciliation before it can acquire an outstanding batch.
