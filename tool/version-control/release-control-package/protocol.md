# Inert controller protocol 2

This package implements the repository's preview boundary. Its launcher accepts
only `preview --fixture-inputs` and local inputs; no live transport exists.
Approval/protection/check observations are supplied synthetic assertions. They
are never production authentication. The retained loader validates package
identity and approved merge shape, not the truth of an approval-file author.

The stable loader supports explicit approved protocols 1 and 2 only. This
current package accepts protocol 2; protocol 1 executes its exact retained
historical eight blobs, serializer, reducer and main. Old records are never
rewritten and a mismatched or unknown semantic protocol refuses. TSV format 1
and the eight manifest paths stay unchanged; semantic protocol is separate.

An approved assertion is strict TSV1 with public-repository, master, control,
manifest, approval and protocol singletons. The literal public repository is
shk95/configs; control and master are full SHA-1 commits, manifest and approval
are SHA-256 identities, current protocol is 2. Control must be a two-parent merge reachable
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

This reader handles one supplied synthetic outstanding-batch envelope. Completion
is terminal; a second batch-start or any later event refuses. Global repeated
history slicing and cross-batch retained configuration/package selection are not
implemented, and remain parent source/live obligations.

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

Synthetic promotion candidates support exactly patch, minor or major
classification. No-op/source-only completion is outside candidate promotion.
Migrations is one nonempty literal TSV narrative summary, with the original-byte
control rules above, or the exact `-` sentinel for none; no execution or inferred
schema follows from its text. Major or any migration requires exact approval,
even when the supplied approval-required flag is 0.

Candidate replacement requires every earlier effect to be reconciled. Confirmed
absent candidate-bound intents become derived `superseded` state: they remain
in the projection/history but are neither pending proposals nor eligible for
later intent/observation under the replacement. PR/merge/tag intents record the
exact candidate digest; their observations must retain that binding. Observed
success is absorbing: absent/unknown/conflicting later reads or a different
applied remote identity refuse rather than erasing success or restoring retries.
Idempotent same-identity success does not rewind publication phase.
Record observation reloads the operating head only along its complete known commit
chain: the current head must equal the target or appear among its commits. The
first applied observation may start at its exact intent parent. A stale later
history cannot lower the current head or erase either recorded success.

A tag-ref requires the exact selected tag-object operation's observed success.
Its fixed operation ID is SHA-256 of canonical JSON with kind=`tag-ref`,
object-operation=the release tuple operation ID, tag=domain plus `-v` plus version,
source=the release source and object=the release object. Owner generation/time
does not change that identity. The release tuple arity remains unchanged. Cancel
intents match the recorded owner's exact run, attempt, workflow and sole writer
job, and use the fixed public repository; supplied unrelated targets refuse.

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

## Bounded refresh data and effects

`refresh-result` has one literal JSON payload. Noop, failed and
terminated-timeout have exactly a status and no consumable identities. Changed
has status and a candidate with exactly batch, source, base, parent, head, tree,
before-lock, lock, utility-source, utility-manifest, source-fingerprint, previous
and branch. Commit/tree IDs are full SHA-1; data identities/batch are SHA-256.
Source equals parent, head differs from parent, lock differs from before-lock,
and initial parent equals base. Previous is `-` or the prior observed owned head.
Branch is always `feature/unixlike-refresh-` plus the supplied batch identity.
No time, owner generation or mutable PR body derives that branch.

Refresh transcript has exactly revisions and current. Each DTO has prepared,
proof, current-dev, branch, checks and integration. Historical DTOs match a
candidate exactly and uniquely for replay. Proof requires one dependency-commit
parent, only unixlike/flake.lock in the diff, matching before/after data identity
and unchanged integer permission mode. An update requires the exact normal-merge
parents [previous, base]; initial merge-parents is empty. These assertions bind
fixture observations, not production source provenance. Current DTO schema,
proof, branch head and dev are always rechecked; pending PR and new integration
also require exact head/base/tree/lock Required checks, app15368 and success.
Absent checks are allowed before branch publication; failed/pending/unknown
checks cannot authorize a next PR. Old completed effects stay absorbing.

Refresh-branch and refresh-pr payloads add literal public repository to the
candidate. Their immutable operation ID is SHA-256 of canonical JSON
{kind, payload}. Creation proposes POST git/refs; updates propose PATCH on that
same owned branch with force=false. The observed previous head is a precheck,
not API CAS/fencing. PR creation proposes feature-to-dev with a fixed readable
title and canonical operation marker. Recovery requires a unique observed PR
number and exact candidate/check identities, never its mutable body. An already
observed unique PR joins the new head revision without proposing another create.
The original `pr` operation remains dev-to-master.

Unknown/conflicting effects fence revision advance; completed effects retain
their historical remote IDs. Confirmed-absent old intents become superseded,
history-only and proposed=0; old intent/observation cannot consume a new revision.
Observed old success cannot advance the new refresh stage. A known dev advance
uses the same promotion invalidation as verified refresh integration: unresolved
promotion effects first reconcile, confirmed absence becomes superseded, and
unfrozen candidate/evidence/approval clears. The last promotion generation stays
monotonic; reselection needs the next generation and exact new evidence/approval.
Verified promotion stays frozen; later refresh integration is next-opportunity.
Late nonconsumable results refuse rather than erase an existing changed candidate.
Identical changed results join without executing another preparation.

Actual CLI/Git preparation exists only in the native-Nix integration fixture.
Preview does not execute it. The fixture extracts the two trusted utility blobs
at their reviewed source, runs controlled local upstreams with an explicit
credential-free environment, and independently compares all bytes/modes. A
required base update preflights merge-tree in a disposable repository without a
commit; only a changed result performs a normal merge and isolated dependency
commit. Noop/failure/confirmed timeout preserve owned refs/source/commit counts.
Only synthetic lock data and exact identities reach this pure reducer.

`refresh_window` consumes supplied Asia/Seoul calendar observations: one 05:00
start per day, manual duplicates join, 06:00 waits only for an in-flight refresh,
and fixed 07:00 cutoff reconciles without canceling refresh or extending wait.
Late/missed events are reported as such. It reads no clock, schedules nothing,
and creates no notification or cross-batch storage.
