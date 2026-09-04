id: windows/sources-total-function
statement: A conditional source list descends strictly and ends with an unconditional variant, so every host resolves to exactly one payload.
rationale: docs/architecture.md § Windows domain
enforced-by: schema windows/src/WinEnv.psm1
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

A variant chooses a payload and nothing else. The bounds must descend so the
first variant a host satisfies is the highest it meets, and the last must be
unconditional so resolution is total; the loader refuses every other shape
by name, before a host could fall through to no payload at all.
