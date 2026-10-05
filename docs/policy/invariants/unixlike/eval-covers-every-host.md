id: unixlike/eval-covers-every-host
statement: The evaluation check reaches every exported configuration, and every explicitly selected native build has a passing result.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: tool unixlike/tool/checks/eval-build
enforced-by: fixture unixlike/tool/checks/eval-coverage-test

Evaluation is evidence only when it reached every configuration. The check
fails on a flavour the flake exports but that lists nothing, on a flavour
whose attribute fails to evaluate, and on a run that reached no
configuration at all; a flavour the flake does not export is reported as
absent. A selected build that is missing, foreign, or fails cannot count as
passing evidence. Build selection is independent of the running host's name
and never grants activation eligibility. The fixture flakes carry no inputs
and exercise these outcomes through `CHECKS_FLAKE` (#131).
