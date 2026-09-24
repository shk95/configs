id: unixlike/install-target-explicit
statement: Every automated NixOS installation names one installable inventory host and one persistent disk path explicitly; desired state never discovers or guesses the destructive target.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: schema unixlike/modules/foundation/installation.nix
enforced-by: fixture unixlike/tool/checks/flake-test
enforced-by: fixture unixlike/tool/checks/install-plan-test
decision: docs/policy/decisions/unixlike/install-targets-are-explicit-runtime-inputs.md § Installation targets are explicit runtime inputs

The storage classes carry an inert `/dev/disk/by-id` target and keep the
runtime label contract that installed guests and the desktop already use. The
planning tool accepts only one declared disk named `main`, requires a
persistent by-id path and records the host, device and source in a generated
wrapper flake and review file. Its fixture proves the accepted path and
refuses a kernel-order device, an unknown or non-installable host, an existing
plan directory and surplus arguments. Disko's VM-only device replacement is
the disposable installation test, not target discovery.
