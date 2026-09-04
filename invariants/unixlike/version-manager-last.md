id: unixlike/version-manager-last
statement: An imperative version manager is never declared as a package, and its hook runs after every declarative PATH entry.
rationale: docs/architecture.md § Unix-like domain
enforced-by: schema modules/shell.nix
enforced-by: fixture tool/checks/flake-test
decision: docs/decisions/sdkman-adopted-not-owned.md § SDKMAN is adopted but not owned

The version manager rewrites PATH. Running it last is what lets declared
packages keep precedence on a name collision, and not declaring its
toolchain is what keeps one version authority per name. The shell module
contributes the hook at `mkAfter` and asserts on the merged initialisation
text, so a PATH line any module contributes later is refused at evaluation
rather than found on a host; a second assertion refuses a JDK or SDKMAN
package in the home. The fixture extends the real home with each violation
and requires the tag in the refusal (#129).
