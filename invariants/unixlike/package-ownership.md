id: unixlike/package-ownership
statement: A package is declared by exactly one module: a feature module when that module generates its configuration, otherwise the shared package list, and a system module only when a service, activation script, or system account needs it.
rationale: docs/architecture.md § Unix-like domain
enforced-by: pending #130
owner: repository maintainer
decision: docs/status.md § Unix-like Home Manager and package ownership

Two declaring modules make precedence an accident of merge order. The rule
follows the shared package list's own header rather than the availability of
a module for the package: enabling an unused module is a behaviour change
(shell integration, generated files, environment variables), and a rule keyed
to the pinned input's module catalogue would break on a lock refresh. The
maintainer chose this wording on 2026-09-03; the twelve packages that have an
unused module stay in the shared list. #130 owns an evaluation-based check.
