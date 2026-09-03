id: unixlike/eval-covers-every-host
statement: The evaluation check fails when it reaches no configuration.
rationale: docs/architecture.md § Unix-like domain
enforced-by: pending #131
owner: repository maintainer

Evaluation is evidence only when it reached every configuration. The check
today returns success for a flavour that lists nothing and for an empty
report, so a flake that stopped exporting its hosts would pass. #131 owns the
fix and its fixture.
