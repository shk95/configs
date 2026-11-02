id: repository/merge-gate-requires-native
statement: Every merge-gate job that runs a check converts an unverified result into a failure.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/check-evidence-three-states.md § A check reports verified, failed or unverified

Local hooks may report unavailable checks without blocking source preparation.
CI validation jobs must fail unavailable selected checks. The historical
merge-gate name does not impose PR/status admission on ordinary master writes.
