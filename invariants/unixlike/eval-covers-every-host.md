id: unixlike/eval-covers-every-host
statement: The evaluation check fails when it reaches no configuration.
rationale: docs/architecture.md § Unix-like domain
enforced-by: tool tool/checks/test
enforced-by: fixture tool/checks/eval-coverage-test

Evaluation is evidence only when it reached every configuration. The check
fails on a flavour the flake exports but that lists nothing, on a flavour
whose attribute fails to evaluate, and on a run that reached no
configuration at all; a flavour the flake does not export is reported as
absent. The fixture flakes carry no inputs and exercise each outcome
through `CHECKS_FLAKE` (#131).
