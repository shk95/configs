id: windows/precondition-declared
statement: A feature precondition names a type the domain evaluates and every field that type needs, and any other is refused when the manifest loads.
rationale: docs/policy/architecture.md § Windows domain
enforced-by: schema windows/src/WinEnv.psm1
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

The evaluator refuses an unknown type only when it reaches one, on the host
that selects the feature, and until 2026-09-20 it reached none
(`INV windows/selected-precondition-evaluated`). The loader now holds the
list of types and their fields, as it does for parsers and comparison modes,
and the fixture holds that list to the evaluator's arms so that a type the
loader accepts cannot be one the evaluator then refuses.
