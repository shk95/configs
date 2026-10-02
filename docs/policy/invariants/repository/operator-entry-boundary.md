id: repository/operator-entry-boundary
statement: Repository operator commands have one documented entry point that forwards arguments and status to their implementation; hooks and CI invoke implementation tools without depending on that operator entry point.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: fixture tool/version-control/test
enforced-by: manual The reviewer confirms every documented operator command uses the entry point and every automation call uses an internal implementation
owner: repository maintainer
decision: docs/policy/decisions/repository/operator-entry-boundary.md § Separate operator and automation dependencies

The entry point selects known repository operations and does not add a deployment verb. Tests may run an operator entry point to verify its public contract; that is not an operational dependency. A person may inspect an internal tool for debugging, while normal instructions use the entry point.
