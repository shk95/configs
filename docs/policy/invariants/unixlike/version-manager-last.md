id: unixlike/version-manager-last
statement: The adopted user-installed JVM manager and its toolchain are not also evaluator packages, and its hook runs after every declarative PATH entry.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: schema unixlike/modules/foundation/shell/shared.nix
enforced-by: fixture unixlike/tool/checks/provider-api-test
decision: docs/policy/decisions/unixlike/sdkman-adopted-not-owned.md § SDKMAN is adopted but not owned

This contract concerns SDKMAN and its JVM toolchain. Nix-supplied mise manages
supplementary tools through appended shims, without a later PATH-prepending
prompt hook. SDKMAN rewrites PATH. Running it last is what lets declared
packages keep precedence on a name collision, and not declaring its
toolchain is what keeps one version authority per name. The shell module
contributes the hook at `mkAfter` and asserts on the merged initialisation
text, so a PATH assignment any module contributes later — `path+=`,
`path=`, `path[…]=`, `PATH=`, bare or behind `export`/`typeset`/`declare` —
is refused at evaluation rather than found on a host; a second assertion
refuses a JDK or SDKMAN package in the home. A script sourced or `eval`ed
later that rewrites PATH is outside what a lexical rule can read and is the
reviewer's to notice; the statement's "declarative PATH entry" means an
assignment a module writes. The fixture extends the real home with each
violation and requires the tag in the refusal (#129).
