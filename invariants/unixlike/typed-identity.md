id: unixlike/typed-identity
statement: Host identity is declared through typed options whose values live in the inventory, never through untyped arguments passed around the module system.
rationale: docs/architecture.md § Unix-like domain
enforced-by: schema modules/flake/identity.nix
enforced-by: fixture tool/checks/flake-test

The contract and the values are two files on purpose: `identity.nix` is the
schema and `inventory.nix` the non-secret declaration, so a wrong shape is
refused by the evaluator before any host configuration is composed. An
untyped special argument would carry the same values with no refusal at all.
