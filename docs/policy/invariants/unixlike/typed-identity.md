id: unixlike/typed-identity
statement: Host identity reaches provider composition through typed constructor inputs, never through untyped arguments passed around the module system; the provider's local values are synthetic fixtures.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: schema unixlike/modules/flake/configurations.nix
enforced-by: fixture unixlike/tool/checks/provider-api-test

`configurations.nix` validates public constructor arguments and creates the
synthetic examples. The evaluator refuses a wrong shape before composing a
configuration. Real values remain in the consumer. The accepted interface is
recorded in `docs/policy/decisions/unixlike/public-environment-host-boundary.md`.
