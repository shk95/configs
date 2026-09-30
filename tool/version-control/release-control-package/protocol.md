# Inert controller protocol 1

This package implements the repository's preview boundary. Its launcher accepts
only `preview --fixture-inputs` and local inputs; no live transport exists.
Approval/protection/check observations are supplied synthetic assertions. They
are never production authentication. The retained loader validates package
identity and approved merge shape, not the truth of an approval-file author.

An approved assertion is strict TSV1 with public-repository, master, control,
manifest, approval and protocol singletons. The literal public repository is
shk95/configs; control and master are full SHA-1 commits, manifest and approval
are SHA-256 identities, protocol is 1. Control must be a two-parent merge reachable
from the asserted master. The exact approved control is selected explicitly;
mere ancestor reachability does not select a different commit. Manifest rows are
`file<TAB>constant-path<TAB>sha256`, sorted with exactly the loader's executing
closure. Blob modes must be regular files, never links. All semantic Python
modules plus retained release-preview, its AWK engine/rules and classifier are
included. The manifest itself is bound by the assertion's digest. The current
stable loader is the fixed verification boundary, not retained decision logic.

Child processes receive only an explicit runtime environment allowlist; ambient
credential variables and Python/Git execution overrides are not forwarded. This
source fixture boundary does not establish actual CI Environment isolation.
Python isolated/no-site mode admits only standard-library and manifest-verified
adjacent modules, rather than ambient installed packages.

Operating inputs have config/operating.tsv, control/stop.tsv, a contiguous
history/NNNNNNNNNNNN.tsv sequence and current/index.tsv. Original bytes are
strict UTF-8 ending in LF, without blank/comment rows, empty values or controls
except tabs/newlines separating fields. Literal narrative Unicode/backslash/quote
data is JSON-escaped only on output. Unknown keys/kinds, duplicates, unexpected
tuples or field counts refuse. Config actor/check lists are sorted unique comma
lists (`-` empty), decimal IDs have no leading zeros; full SHA-1 IDs have 40
lowercase hex digits and SHA-256 identities have 64. Event filename counter is
the only padded counter. Exhaustion refuses. Pinned config blob identity is bound
in batch-start; the caller supplies those pinned bytes, while stop is read anew.
There is no private storage transport in this lane.

Each event has sequence, kind, prior-event digest and batch identity plus exactly
the kind-specific fields declared in records.py. Evidence, release and operation
tuples retain the parent's exact arities. JSON operation payload is a literal TSV
singleton and must match the tuple's canonical SHA-256 payload identity; it is
never evaluated. Endpoint schema/path/body/status construction lives in adapter.py.
The current index stores sequence/prior/batch/generation/stage and a SHA-256 digest
of the complete canonical reducer state. Full state is reconstructible from the
events; a digest is not a substitute for history. Any projection mismatch refuses.

The reducer invalidates approval/evidence on candidate replacement and freezes
publication after verified promotion. Intent comes before observation. Supplied
complete target observations distinguish applied/confirmed absent/unknown/conflict;
unknown/conflicting operations prevent new intent, and completed effects cannot
be replayed. Stop can race an accepted intent: its observation is retained but no
next intent is allowed. Clearing a stop input does not resume recorded stop;
authenticated synthetic resume and reconciled effects are required. Takeover
requires exact terminal owner/attempt/writer-job observations, not cancel acceptance
or timeout. Neither generations nor these prechecks are atomic API fencing.

Transcript JSON has exactly source, checks, owner, observations and protection.
Source is a list of exact repository/workflow/actor/run/attempt/ref/event/mode/candidate
objects, allowing historical approval and current preview observations together.
Checks is a list of full evidence tuples, each exact selected tuple observed once.
Owner carries exact latest-attempt and complete writer-job termination, when
takeover is requested. Observations are keyed by operation ID, with a list of
historical status/target/complete objects selected by each event's observation
digest. This retains both unknown and later reconciled responses for replay.
Protection is the explicit asserted expected settings.
These are fake API observations; production provenance and endpoint receipts are
outside this package's delivered proof.

The writer bound is 15 minutes, API deadline 30 seconds, cancel observation 30
seconds up to five minutes. Accepted transient retry waits are 5/15/30 minutes
with prospective credential-free job bounds 6/16/31. Fixtures simulate these
contracts; the inert workflow performs no wait, API or cancellation. Its independent
inspector is outside the constant cancel-in-progress=false writer job group.
Actions pending-job replacement/FIFO, actual notifications and real credential
isolation require separate operating proof. No schedule trigger is installed.

Public output is a bounded outcome/stage/proposal count, never private connection
IDs, payload digests, record prose, paths or raw exceptions.
Disabled config produces no output; enabled invalid inputs refuse. This protocol
does not adopt production semantic releases or replace calendar tags.
