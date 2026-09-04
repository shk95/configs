id: repository/hygiene-machine-identity
statement: A machine-unique identifier is host identity and never desired state; a constant that names an interface or is derived from a name is not.
rationale: docs/architecture.md § Desired-state hygiene
enforced-by: tool tool/version-control/hygiene
enforced-by: fixture tool/version-control/test
decision: docs/decisions/hygiene-tool-owns-enforcement.md § The hygiene tool owns desired-state hygiene

Axis 4 of the hygiene scan: GUID, MAC address, Windows SID, with the
well-known constants listed in the scan itself.
