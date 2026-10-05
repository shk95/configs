id: unixlike/host-written-payload-projected
statement: Managed settings that a host application rewrites in place have one finite ownership declaration used by comparison, application, capture and consumption, with whole declared members replaced and undeclared runtime siblings excluded from drift and capture.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: tool unixlike/modules/programs/karabiner/tool
enforced-by: fixture unixlike/tool/checks/karabiner-test
enforced-by: fixture unixlike/tool/checks/karabiner-entry-test
enforced-by: schema unixlike/tool/darwin-capture/engine.py
enforced-by: schema unixlike/modules/programs/karabiner/module.nix
enforced-by: fixture unixlike/tool/checks/darwin-capture-test.py
enforced-by: fixture unixlike/tool/checks/darwin-capture-consumer-test
decision: docs/policy/decisions/unixlike/karabiner-desired-state-by-projection.md § Karabiner desired state is compared and applied by projection

Most Unix-like payloads are delivered as a link into the Nix store, so the
question of what the repository owns in the file never arises: it owns the
whole file. An application that unlinks and rewrites its own configuration
cannot be delivered that way, and desired state then has to say which members
of that file it owns. Saying it once, in the payload, is what keeps the three
directions honest: the same declaration decides what counts as drift, what is
written over the host's own members, and what may be read back into the
payload. A second declaration — a list of keys to ignore — would be free to
drift from the payload and would fail open on a member nobody thought about.

The projection is onto the members the payload declares, not onto every member
it happens to contain: a declared member is taken whole, with everything
beneath it, and an undeclared member of the same document is left where it is.
The fixture holds both directions, because either half alone is useless. A
projection that reported the host's own runtime members would make every
application save a drift; one that missed a changed declared member would make
the payload decorative. The capture direction has a fixture of its own in
`tool/version-control/test`, because the command that reads a projection back
into the payloads is the commit helper rather than the projection tool.

The first payload under this rule is Karabiner's, and the same rule covers the
symbolic hotkey entries the input-source toggle depends on: there the declared
members are entry numbers in a dictionary the host holds dozens of entries in.
The Windows domain reached the same rule from the other side and registered it
separately as `INV windows/subset-owns-declared-keys`; the two are copies of one
idea, each enforced by its own domain's tooling.

Reconciled2026-09-30. Version-1 host-document management declares finite units in
`unixlike/modules/programs/karabiner/units.json`, independent of present settings:
Karabiner global/profiles parents and symbolic hotkey entries60/61. The new native
adapter, capture engine and typed module consumption read that declaration.
Active host documents replace whole units; configs source returns provider
defaults while retaining dormant data. Disabled units do not load documents.
Missing required parents/entries and unsupported deletion/reset shapes refuse.

The legacy executable and both historical fixtures remain exact compatibility
enforcement for the existing provider-payload Git caller; they are not claimed as
host-document contract consumers. Their payload-bound protocol and locator/tags
remain until the separately owned caller retirement. Historical observations
retain their original source binding.

Reconciled 2026-10-01. Active host-document schema and capture/consumer fixtures
above enforce the single finite unit declaration independently of the historical
Git caller. The retired Justfile publication entry refuses legacy arguments
without reading observations or inferring a host-document Save destination;
its fixture also proves the retained comparison delegation. The registry detaches
only the root legacy fixture locator before its separately owned tag/block
retirement. That root fixture still exists and may name this registered invariant;
its continued historical coverage does not make it an active host-document
consumer. The domain legacy tool, project protocol and projection fixture remain
unchanged and registered. Earlier payload-bound rationale and observations retain
their original source meaning.
