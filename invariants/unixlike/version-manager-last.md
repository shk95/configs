id: unixlike/version-manager-last
statement: An imperative version manager is never declared as a package, and its hook runs after every declarative PATH entry.
rationale: docs/architecture.md § Unix-like domain
enforced-by: pending #129
owner: repository maintainer
decision: docs/status.md § Unix-like Home Manager and package ownership

The version manager rewrites PATH. Running it last is what lets declared
packages keep precedence on a name collision, and not declaring its toolchain
is what keeps one version authority per name. Nothing proves either today;
#129 owns a check on the generated shell initialisation.
