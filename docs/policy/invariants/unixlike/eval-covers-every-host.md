id: unixlike/eval-covers-every-host
statement: Provider verification evaluates every advertised constructor/system/environment composition and every exported synthetic example without realizing a host closure, and refuses absent, empty or invalid required coverage.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: tool unixlike/tool/checks/evaluate
enforced-by: fixture unixlike/tool/checks/eval-coverage-test
enforced-by: fixture unixlike/tool/checks/composition-witnesses-test
enforced-by: fixture unixlike/tool/checks/provider-api-test
decision: docs/policy/decisions/unixlike/provider-verification-boundary.md § Provider verification follows the public composition boundary

Synthetic outputs witness the provider API. They are evaluated to derivation
paths, not deployed or built as hosts. Fixture flakes may omit output families;
the provider may not. A run reaching no composition fails. Native and foreign
compositions receive the same evaluation evidence. Focused flake checks realize
provider-owned artifacts separately from the configuration outputs.

The public constructor/system/environment witness matrix independently forces
complete toplevel derivations, so removing or renaming example outputs cannot
remove a supported system from coverage. A detector keeps ARM state readable
while refusing its toplevel to prove that state-version probes are insufficient.
