# A JsonSubset payload is captured by projection

date: 2026-08-31
scope: windows
status: accepted
issue: #93
source: 9f1e8ce:docs/status.md § A JsonSubset payload is captured by projection

`JsonSubset` was refused outright, on the grounds that the payload is a subset
of the host file by design and cannot be derived from it. Eleven of the eighteen
PowerToys managed files declare that mode, including the root `settings.json`
that owns the per-module enable map, so the maintainer could change a setting in
the PowerToys UI, watch `capture.ps1` report the drift, and have no way to move
it into desired state (#93).

The premise was wrong in one direction only. A `JsonSubset` payload declares
which keys it owns and tolerates every other key the application keeps in the
same file. The host holds a value for each declared key, so the payload that
makes this host clean is the host's values arranged in the payload's declared
shape, and that *is* derivable. What is not derivable — the keys the payload
deliberately does not declare — is exactly what must never reach desired state,
so the projection drops it.

This is one mechanism rather than a per-file ignore list, and the choice is the
decision worth recording. An ignore list is a second declaration of what a
payload owns, kept beside the payload and free to drift from it; every new
module would need an entry, and a missing entry fails open by writing runtime
state into desired state. A projection has only the payload, so a key is
captured if and only if the payload declares it, it fails closed on an object
member nobody thought about, and widening coverage is an edit to the payload
itself. AGENTS.md's rule that runtime state stays out of desired state is then
enforced by the payload rather than by a list of names someone has to maintain.

That guarantee is about object members, and review found the sentence had been
overstated into one about payloads (#100). A declared list is exact rather than
a subset, so it fails *open*: declaring an empty list is a claim to own the
whole list, and the projection then captures whatever the host holds there. The
mechanism is right — a declared list has to be exact, because the read side
matches it by position and requires equal length, so no member subset a payload
declared could outlive a length change. What was wrong was the payloads. The
PowerToys inventory declared twenty-eight empty lists, and the worst of them
would have captured CmdPal's monitor topology, its installed-extension ranking,
and Advanced Paste's free-text AI prompts. The rule the audit settled on is that
a list is declared only when there is content to declare: a key left undeclared
owns nothing, which is exactly what an empty declared list cannot express, and a
fixture now holds the whole inventory to it.

Each JSON kind is projected the way the read side compares it, so the two
directions cannot disagree about what a payload owns. A declared object
contributes exactly the members it declares. A declared list contributes the
host's list element by element, with element *i* projected onto declared element
*i* where the payload has one and taken whole where it does not, because the
read side compares a list by position and requires equal length: a payload
cannot declare a member subset that outlives a length change, so taking the
elements it never declared as they are is the only reading the payload's own
shape supports. A declared scalar contributes the host's scalar, `null`
included, because the read side treats a declared `null` as a leaf.

Convergence is by construction rather than by test: every member of a projected
document is a member `Test-WinEnvJsonSubset` looks for, holding the value it
found there, and every projected list has the host's own length. There is no
host this can capture from and leave drifted, and the fixture asserts it through
the comparison itself rather than restating it.

Two host shapes are still refused, and both are shapes the read side already
calls drift while the payload's declared shape cannot express the fix: a
declared member the host object no longer holds, and a host value whose kind is
not the declared value's kind. Whether a vanished key should be dropped from
desired state or restored in the application is not a question this direction
can answer, and writing a migrated shape in would discard a declared subtree
without saying so. Both name the key path.

The projection is ordered before the content refusals. An absolute account path
in a key the payload never declared is therefore gone by the time they read the
content, while this host's account name in a key the payload *does* declare is
still refused. Reversed, every capture from a real PowerToys host would be
refused for a path in a key desired state does not manage.

**No `SchemaVersion` bump, and this is a departure from the three earlier schema
bumps (`docs/decisions/wslconfig-selected-by-windows-build.md`,
`docs/decisions/terminal-generated-profiles-tolerated.md`,
`docs/decisions/feature-selection-closed.md`) that needs its reason stated.**
Those bumps each declared something no earlier loader could honour — a
`Features` array, a `Sources` variant list, a new `Compare` mode — so the schema
number is what makes an old module say the schema is unsupported instead of
failing later with a mangled message. Nothing here is such a declaration:
`JsonSubset`'s read semantics are untouched, no manifest key or `Compare` value
is added, and every earlier loader honours every declaration in this manifest.
The refused direction was unimplemented, not undeclarable, and an older
`capture.ps1` paired with this manifest still refuses conservatively rather than
doing something wrong. Inventing a second mode with identical read semantics
purely to carry a schema number would put two spellings of one comparison in the
manifest, which is the thing the one-mode-per-entry decision exists to prevent.

`ProjectVersion` does move, 0.5.0 to 0.6.0. That field is what an applied host
compares against its recorded `state.json`, and both halves of this change are
things an applied host should redeploy for: the payloads widen to cover settings
surfaces they did not declare before, and the domain's reconciliation behaviour
changes. No `state.json` schema changes.
