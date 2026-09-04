id: unixlike/payload-declared-and-parsed
statement: Every source payload declares its format and is parsed by the tool that will consume it, and the declaration and the payload tree agree in both directions.
rationale: docs/architecture.md § Unix-like domain
enforced-by: tool tool/checks/payloads
enforced-by: fixture tool/checks/payloads-test
decision: docs/decisions/payloads-declared-and-parsed.md § Every payload declares its format and is parsed

Nix delivers payloads with `.source`, which copies without reading, so
evaluation and build evidence say nothing about payload content. The
declaration is `assets/payloads.json`; it carries no comment, so the tag
lives on the tool that reads it and refuses a mismatch, and on the fixture
that proves each way a payload can escape validation.
