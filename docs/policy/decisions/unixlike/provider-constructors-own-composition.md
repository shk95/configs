# External hosts call typed provider constructors

date: 2026-09-24
scope: unixlike
status: accepted
source: docs/work/unixlike/host-provider-api/spec.md § Provider owns the policy, consumer owns the instance

`configs` exports `lib.mkNixos`, `lib.mkDarwin`, and `lib.mkHome`. A consumer
calls a constructor with its host values and its own Git identity; it does not
import files under `unixlike/modules/` or select deferred module classes.
`mkNixos` accepts `name`, a typed `host` (`system`, `kind`, optional
`hypervisor`, `user`, `stateVersion`), and an explicit `profiles` list. All
three constructors require `git.name` and `git.email`. `mkDarwin` accepts a
typed `host` with `system`, `hostName`, and `user`; `mkHome` accepts `system`
and `user`. The NixOS and Darwin constructors accept `systemModules` and
`homeModules`; standalone Home Manager accepts `homeModules`. Those are
host-owned extension points for hardware and secret delivery, not a way to
select provider-internal classes.

The provider validates the five supported NixOS machine combinations and
profile choices before returning a host configuration. It owns the mapping
from a machine kind to required and offered classes in
`unixlike/modules/flake/configurations.nix`. The consumer owns output names,
host values, its lock pin, and final build and runtime evidence. The provider's
current seven outputs remain during the transition and use the same
constructors; their derivation paths are compared with the pre-API tree.

The constructor inputs are typed with the Nix module system. Host values
reach each final NixOS, nix-darwin, or Home Manager evaluator as typed options
instead of being captured from the provider flake's inventory. No identity
value is passed through `specialArgs`. `provider-api-test` calls only the
exported attributes and proves both accepted and refused consumer inputs.

The public template is a separate example and the private consumer repository
is its own owner after creation. Template changes do not automatically change
an existing host; a host intentionally updates its pinned `configs` revision.

Amended 2026-09-25: all seven real outputs now have private consumer owners.
The provider's former inventory is replaced by synthetic fixture values.
Those outputs exercise the constructors and machine-kind coverage only;
their `fixture-*` names do not identify deployable hosts. Host-specific
evaluation, native build, runtime and activation evidence stays with each
private consumer.
