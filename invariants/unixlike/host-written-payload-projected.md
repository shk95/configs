id: unixlike/host-written-payload-projected
statement: A payload the host application rewrites in place is compared, applied and captured by one projection onto the members the payload declares; what else the host keeps in that file is runtime and is neither reported as drift nor captured.
rationale: docs/architecture.md § Unix-like domain
enforced-by: tool tool/darwin/karabiner
enforced-by: fixture tool/checks/karabiner-test
decision: docs/decisions/karabiner-desired-state-by-projection.md § Karabiner desired state is compared and applied by projection

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
the payload decorative.

The first payload under this rule is Karabiner's, and the same rule covers the
symbolic hotkey entries the input-source toggle depends on: there the declared
members are entry numbers in a dictionary the host holds dozens of entries in.
The Windows domain reached the same rule from the other side and registered it
separately as `INV windows/subset-owns-declared-keys`; the two are copies of one
idea, each enforced by its own domain's tooling.
