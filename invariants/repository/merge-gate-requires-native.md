id: repository/merge-gate-requires-native
statement: Every merge-gate job that runs a check converts an unverified result into a failure.
rationale: docs/architecture.md § Repository governance plane
enforced-by: fixture tool/version-control/test
decision: docs/decisions/check-evidence-three-states.md § A check reports verified, failed or unverified

The local gate lets an unverified check pass so a clone can push work for a
domain it cannot verify. The merge gate is the one place that must not,
and a job added without the conversion would reintroduce the silent skip
the evidence contract was written to remove.
