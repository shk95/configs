id: unixlike/typed-identity
statement: Host identity reaches provider composition through typed constructor inputs, never through untyped arguments passed around the module system; the provider's local values are synthetic fixtures.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: schema unixlike/modules/flake/identity.nix
enforced-by: fixture unixlike/tool/checks/flake-test

`identity.nix` checks the provider's synthetic fixtures, and
`configurations.nix` validates the consumer's typed constructor arguments.
The evaluator refuses a wrong shape before composing a host. Real values
remain in the private consumer.
