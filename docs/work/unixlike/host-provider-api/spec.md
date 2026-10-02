# Export a Unix-like provider API and retire in-repository host instances

kind: spec
date: 2026-09-24
scope: unixlike
status: approved
review-by: 2026-12-24

The maintainer chose on 2026-09-24 to make `configs` a provider consumed by
one private host repository. A separate public template demonstrates the
contract. Physical grouping under `docs/work/unixlike/module-layout/`
precedes implementation here; the completed host evidence remains historical.

## Problem

`unixlike/modules/flake/inventory.nix` holds real host names, accounts,
state versions, Git identity and profile choices. The same flake both owns
the machine-kind composition policy and creates final Home Manager, NixOS
and Darwin outputs. Feature files and checks read these values, and local
recipes and installation helpers assume the final outputs live here. This
couples portable environment changes to individual host instances and
leaves no supported API for an external host flake.

The existing inventory is explicitly non-secret; moving it is an ownership
change, not a claim that it currently contains credentials. The private
consumer will own SOPS + age recipients and encrypted host data. Plaintext
secrets must not enter flake evaluation or build outputs.

## Decisions

### Provider owns the policy, consumer owns the instance

Export typed constructors for NixOS, nix-darwin and standalone Home Manager
configurations. The interface accepts host identity and the machine kind,
validates offered profiles, and returns a complete configuration. It accepts
an explicit extension point for host-owned hardware facts and SOPS + age
delivery without making the consumer select internal deferred-module classes.
The machine-kind table and its required/optional class mapping remain in one
provider-owned composition implementation. Do not pass identity through an
untyped `specialArgs` channel.

The exact public attribute names and argument schema are fixed and exercised
by a consumer fixture before the API is declared stable. The initial
candidate is `lib.mkNixos`, `lib.mkDarwin` and `lib.mkHome`; naming does not
substitute for validation. Provider code may keep its existing typed option
schema internally. Real values, output names and profile selections move to
the consumers. A `host` option within an assembled NixOS configuration is a
typed recipient of consumer values, not a provider inventory.

### Establish coverage before removing the current outputs

First introduce the constructors while the seven present outputs still
exist. Compose those outputs through the same constructors and compare their
evaluated properties and derivation paths with the baseline. The public
template then consumes the API with a synthetic, non-secret host and runs
its own checks. Migrate real hosts one by one, starting with the disposable
OrbStack instance. A consumer pins the provider revision in its own lock and
owns its final output, build and runtime evidence.

The declared physical desktop is not installed. Its consumer can own the
provisional values and evaluated output, but it cannot supply native runtime
or activation evidence until the deferred desktop work resumes. Do not make
the provider transition depend on pretending that placeholder is running.

Only after every current instance has a verified consumer owner, remove the
real inventory and final host outputs from `configs`. Replace their test
coverage with synthetic hosts for every supported machine kind and with
positive and negative profile fixtures. The provider's checks must fail if
they reach no configurations. Existing evidence for past hosts is retained
as dated historical evidence, not presented as current provider runtime.

### Keep repository scopes and deployment decisions separate

The public template and private host repository have their own history and
checks. The repository-owned roadmap, architecture, release/tag meaning and
procedures are changed in repository-scope increments; Unix-like modules,
tests and status change in Unix-like increments. The provider release can
certify its API and fixtures only; a host consumer certifies its own final
build and runtime. No evaluation, build, template publication, merge or tag
authorizes host activation.

## Increments

1. Publish and test the typed constructor API while existing outputs remain,
   then compare all present host outputs against the pre-refactor baseline.
2. In the public template repository, exercise the API with a synthetic
   host and document SOPS + age setup without a real recipient or secret.
3. In the private consumer repository, migrate one host at a time and record
   evaluation, native build and runtime separately. Activation stays behind
   an explicit request for each host.
4. In a Unix-like increment, remove real host values and outputs only after
   consumer ownership is verified; make synthetic machine and profile
   fixtures the provider's coverage.
5. In separate repository-scope increments, revise the architecture,
   release evidence, local command ownership, the hygiene scanner's current
   dependency on `unixlike/modules/flake/inventory.nix`, and remaining roadmap
   items to match the observed transition. Do not remove that inventory until
   its repository-scope name check has a new declared source and fixtures.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | An external flake can call typed NixOS, Darwin and standalone Home constructors without importing provider-internal files or selecting deferred-module classes. | evaluation, review |
| AC2 | Invalid machine combinations, missing identity or profile-choice fields, duplicate profiles and unavailable profiles fail with named errors; valid required classes and optional profiles are composed only by the provider. | evaluation |
| AC3 | During the transition the seven current outputs remain available through the new constructors, and any derivation-path or generated-setting difference from the baseline is explained before adoption. | evaluation, review |
| AC4 | A public, non-secret template consumes a pinned provider API and its synthetic example evaluates in the template repository; setup instructions identify the host-owned SOPS + age boundary. | evaluation, review |
| AC5 | Every installed host has a private consumer owner and independently recorded final evaluation, native build and runtime evidence before its provider-side instance is removed; activation is reported separately. The uninstalled desktop has a consumer-owned provisional output and evaluation only, with its physical evidence still pending in the desktop report. | evaluation, build, native runtime, review |
| AC6 | After adoption, `configs` contains no real host inventory, identity or final host output, and provider fixtures cover every supported machine kind, optional-profile choice and the no-host failure case. | evaluation, review |
| AC7 | Provider checks, installation/deployment helpers, current-state documents and release evidence describe provider coverage without claiming it certifies a consuming host; repository hygiene no longer requires the removed real inventory and still refuses undeclared desired-state names. | evaluation, review |
| AC8 | The remaining desktop, installation and VM roadmap items are re-owned and their existing pending reports are amended without erasing previously verified evidence. | review |

## Excluded

No physical module move, secret plaintext, implicit flake-input refresh,
Windows desired-state change, automatic deployment or host activation belongs
to this provider work. The public template and private consumer are separate
repositories; their own changes are not claimed as commits in this one.

Amended 2026-09-24: The maintainer fixed the private repository boundary before
the first migration. All seven current outputs move to one private consumer
repository, `configs-hosts`; each host keeps its own `flake.nix` and lock so it
can choose its provider revision independently. The public
`configs-host-template` remains a separate, one-time starting point. No
acceptance criterion changes.
