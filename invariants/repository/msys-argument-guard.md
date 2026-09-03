id: repository/msys-argument-guard
statement: A governance shell script that invokes a text tool disables MSYS argument conversion, so a leading-slash argument reaches the tool unchanged on a Git for Windows clone.
rationale: docs/architecture.md § Repository governance plane
enforced-by: fixture tool/version-control/test
decision: docs/status.md § Capture moves a host change into desired state

Observed as #79: a hook rejected a clean Windows commit because a search
string had become a Windows path. The value can come through a variable, so
the rule keys on the call, not on a literal.
