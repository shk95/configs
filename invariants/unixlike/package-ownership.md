id: unixlike/package-ownership
statement: A package is declared by exactly one module: a feature module when that module generates its configuration, otherwise the shared package list, and a system module only when a service, activation script, or system account needs it.
rationale: docs/architecture.md § Unix-like domain
enforced-by: schema modules/packages.nix
enforced-by: fixture tool/checks/flake-test
decision: docs/decisions/package-ownership-by-generating-module.md § A package is owned by the module that configures it

Two declaring modules make precedence an accident of merge order. The rule
follows the shared package list's own header rather than the availability of
a module for the package: enabling an unused module is a behaviour change
(shell integration, generated files, environment variables), and a rule keyed
to the pinned input's module catalogue would break on a lock refresh. The
maintainer chose this wording on 2026-09-03; the twelve packages that have an
unused module stay in the shared list. The shared list's file asserts, per
home, that no package name is defined from two owners — a file of this
repository, or the evaluator's own modules taken together — and, per system
layer, that no name this repository declares is in both the system packages
and the managed home, outside the two evaluator-owned shells the decision
names. Which packages a system module *should* hold stays a reviewer's
question; the check decides only that nothing is declared twice (#130).
