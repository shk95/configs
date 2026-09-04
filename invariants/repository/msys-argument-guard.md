id: repository/msys-argument-guard
statement: A governance shell script that invokes a text tool disables MSYS argument conversion, so a leading-slash argument reaches the tool unchanged on a Git for Windows clone.
rationale: docs/architecture.md § Repository governance plane
enforced-by: fixture tool/version-control/test
decision: docs/decisions/hooks-run-under-git-for-windows.md § Hooks run under Git for Windows

Observed as #79: a hook rejected a clean Windows commit because a search
string had become a Windows path. The value can come through a variable, so
the rule keys on the call, not on a literal.

tool/checks/* is unixlike scope and outside this rule by the maintainer's
ruling.
