id: repository/release-preview-read-only
statement: An offline release preview accepts only pinned structured inputs, produces deterministic decisions or explicit refusals, and leaves source and remote state unchanged.
rationale: AGENTS.md § Governance design
enforced-by: tool tool/version-control/release-preview
enforced-by: fixture tool/version-control/test-release-preview
owner: repository maintainer

This contract constrains the additive preview command, not the production release
flow. Input validation and reproducibility do not authenticate an asserted live
check or adopt a production bootstrap. The existing annotated calendar releases,
promotion authorization, supported-domain guarantees and host boundaries retain
their own authority. The seven fixture families test accepted and refused data,
pinning, isolation and command behavior without performing a remote mutation.
