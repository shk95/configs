id: unixlike/provider-input-refresh-bounded
statement: Provider input refresh selects independent direct sources with validated exclusions and preserves all permanent source files except a complete validated lock, refusing stale or failed candidates and empty-selection update-all.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: tool unixlike/tool/refresh-inputs
enforced-by: fixture unixlike/tool/checks/refresh-inputs-test
enforced-by: fixture unixlike/tool/checks/refresh_inputs_test.py
decision: docs/policy/decisions/unixlike/bounded-provider-input-refresh.md § Adopted utility boundary

Exclusions preserve their own locked source, while followed owners retain
normal ownership. A refresh does not commit, schedule, release or deploy.
