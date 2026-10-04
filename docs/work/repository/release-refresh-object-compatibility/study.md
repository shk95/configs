# Observed refresh and object publication contract gaps
kind: study
date: 2026-10-04
scope: repository
status: open

## Original source observations

At dev 978f999c827ea78e3d33462bec928b53f1c4b046, adapter.PAYLOADS contains
refresh-branch and refresh-pr, with exact REFRESH_FIELDS and deterministic refresh
operation IDs. Executor.request(refresh-branch) first reads the proposed public
commit and validates lock-only closure. Its effect is ref creation or non-force ref
update. Existing branch observations classify the head as previous/new; they do not
observe object creation or partial object publication. No hidden public Git-object
POST belongs to this original operation.

The original engine binds refresh intents to an existing refresh candidate, owner
generation and original context; unresolved unknown/conflict blocks later intent.
A new effect needs explicit compatible schema/reducer/transcript/operation support.
Historical packages must continue to validate their own original contracts.

The local current lock is 4094 bytes, but current small size is not a durable data
transport bound. A caller-provided lock envelope is assertion data until actual run,
source/tool, before/after bytes/modes and terminal status are independently observed.
Preparation must run apart from the writer's credential-bearing OS job. Fixed trusted
utility source is copied explicitly; no destination candidate utility is executed.

## Official endpoint evidence and unresolved download authority

GitHub documents Actions artifact metadata with run identity and a digest, and a
ZIP download endpoint returning an expiring redirect. This requires a reviewed
redirect/token/ZIP boundary; existing fixed API-only transport is not enough.
See [Actions artifacts REST API](https://docs.github.com/en/rest/actions/artifacts).
No download origin allowlist or wildcard authority is inferred from the API hostname.

GitHub's Git database API exposes object creation separately from ref updates. The
source design must bind the resulting exact object identities before publication,
not treat a ref response as proof of all object effects. See
[Git database API guide](https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-your-git-database).
Actual API permissions, Environment isolation and source acceptance remain distinct
operating gates, not conclusions drawn from those endpoint descriptions.

## Independent plan review and unresolved exact schema, 2026-10-04

Independent review found no blocking defect in this pending planning return. Before
source pickup, bind an already completed preparation run to the later claimed writer
batch with exact source/base, unique consumption and stale/duplicate-result refusal.
A run completed before claim is not itself ownership of the eventual writer batch.

Restart also needs an explicit owner/decision procedure after object GET. Exact
verified bytes may become an observed success; unavailable/404 must not silently
become confirmed absence or authority for another POST. A new instance or run creates
no retry permission. These unresolved contracts keep AC1/AC2 pending.

## Data-origin delegation and attempt provenance review, 2026-10-04

Official artifact downloads use an API-returned expiring Location. A future explicit
contract may delegate one credential-free data GET to that exact API-returned public
HTTPS URL, with no caller URL, second redirect, credential forwarding or signed-URL
logging; DNS and actual connection address, TLS, port and byte/ZIP limits need
positive and negative fixtures. That is a new authority to adopt, not a conclusion
from the existing fixed-host/no-redirect decision. No download host is guessed.

Artifact metadata binds a run but does not itself name uploader job/run attempt or
prove utility execution. A proposed first source contract supports only a pinned
sole-job completed attempt=1 and unambiguous artifact identity, with independently
observed run/job/source/tool and an explicitly adopted output contract. Reruns,
missing provenance, replacement or moving metadata refuse. Digest binds archive
bytes, not semantic correctness or operating certification. Exact acceptance remains
pending, including unique later-batch consumption.

## Generated lock declaration gap, 2026-10-04

The actual test-refresh-candidate-nix.py prepare fixture commits only a
chore(unixlike-deps) subject. Production preview requires seven Release-* trailers;
missing trailers or unknown compatibility refuse. The flake.lock exact mapping
selects prod-unixlike-api and its related contract/template/evidence obligations.
Neither fixed author/time nor later promotion approval invents those declarations.

The required order is literal lock result, source-bound Unix-like domain release
review, deterministic message/object construction, then explicit object publication.
Reviewed impact/contracts/compatibility/rationale/migration bind exact lock/base/
utility/rules/package and change invalidates review. Unsupported none/source-only
needs its own compatibility plan. Scheduled dependency refresh has no implicit
patch/compatible authority; absent an accepted narrow automation policy it prepares
and waits for review rather than publishing. This gate is now explicit pending AC4.


## Reviewed immutable object and handoff contract, 2026-10-04

Root and independent reviewers selected protocol 4 with refresh-object as the
single new effect kind. Its blob/tree/commit payloads are data; no hidden writes
enter original protocol-3 refresh-branch. Existing authorize_recovery already
permits authenticated terminal-old-owner observation before takeover, so no new
semantic owner authority is needed. Actual REST canonicalization is an operating
gate, not a reason to omit strict source mismatch refusal.

Protocol 4 refresh current/revision contexts have exact keys prepared, proof,
current-dev, branch, checks, integration, construction. Keep original protocol-3
six-field grammar. Construction exact keys are format=1, inputs, objects, digest.
Inputs exact keys: batch, source, base, previous, before-lock, lock, utility-source,
utility-manifest, source-fingerprint. Digests are SHA256; commits SHA1; previous
may be '-'. Objects are ordered topologically with exact type/sha/raw/dependencies
keys. Raw is canonical base64 of original Git object body, type blob/tree/commit,
sha is SHA1(type + space + decimal byte length + NUL + raw). Dependency descriptors
have exact type/sha keys, sorted uniquely. Reject cycles, forward/self edges and
unknown original dependencies.

Digest is SHA256(canonical(format/inputs/objects)), excluding itself and operation
IDs. After this digest is known, derive each ordered payload's exact keys:
repository, batch, refresh, construction, object-type, object, raw, dependencies.
Repository is shk95/configs; refresh is canonical prepared digest; dependencies
is canonical JSON of type/sha/operation descriptors. An earlier generated object
uses its already derived operation ID; an independently observed original public
dependency uses '-'. Operation ID is SHA256(canonical(kind=refresh-object,payload)).
No runtime owner generation participates in the ID; original row generation does.
This order avoids a construction/operation self-reference.

Validate complete lock-only graph: changed literal lock blob, full direct unixlike
and root trees with all other entries preserved, optional required-base merge
commit parents [previous,base], final commit parent [parent], exact prepared head
and tree. Preserve original base raw objects for complete graph/hash checks.
Transport derives graph from actual original objects; arbitrary caller graph is
not publishing authority. Reducer matches each intent to the next exact payload
derived from original construction, observes dependencies before later objects,
and requires all generated objects observed before branch/ref/PR. Unknown/conflict
fences everything; replacement requires original unresolved-effect reconciliation.

Public fixed API writes are POST git/blobs, git/trees, git/commits; reads are exact
typed SHA endpoints in shk95/configs. Blob POST only canonical base64; tree POST
only complete direct path/mode/type/sha entries, no base_tree/content/deletion;
commit POST only explicit tree/ordered parents/message/author/committer, no signature
or defaults. Status 201 is acknowledgement, not completion. Independent exact GET
reconstructs and rehashes original bytes. No recursive-tree completeness shortcut,
redirect, other repository, guessed prefix or unexpected response proves existence.

Observation envelope retains status/target/complete. Present target exact keys:
object-type, object, raw-digest, dependencies, construction. Mismatching complete
data conflict; unavailable data unknown. Only exact typed authenticated GET 404
can mean absent; 401/403/422/5xx are unknown. Lost POST response fences later writes.
Existing read-only recovery records original old-generation applied/absent first;
only reconciled takeover can explicitly retry identical payload/ID. New instance
is not retry authority. Stop/source/head/job movement still refuses effects.

Commit grammar is bounded unsigned canonical Git data with fixed identities,
UTC +0000 date from actual successful preparation job completed_at, and reviewed
seven Release-* trailers. Actual domain custody binds base/before-after lock,
utility/rules/package/preparation receipt; transport verifies this independently.
Structural trailer grammar or fixed metadata never invent patch/compatibility.
Unexpected server bytes/SHA conflict and cannot reach any ref. Source synthetic
fixtures prove this refusal; actual successful API publication needs later receipts.

Bounds: canonical construction <=1 MiB, generated objects <=8, decoded total
<=512 KiB, individual raw <=256 KiB, direct tree entries/dependencies <=4096,
name <=255 bytes, depth <=8, commit message <=16 KiB. Full transcript remains
within existing 4 MiB transport limit; do not delete old revisions to fit. Pickup
checks actual source fits; larger data returns to planning.

Original protocol 1/2/3 package bytes, IDs, transcripts and reducers remain selected
by original control/manifest. Enumerate protocol 4 in original package/loader and
current transport dispatch without rewriting old contexts or historical closures.
Semantic source comes first, then independently reviewed current transport object
bridge, then refresh preparation/receipt connection and finite writer. Each outcome
has source/native proof; no source step initializes, promotes master, enables a
schedule or performs an actual release.

## Separate preparation and declaration contracts

Choose an exact completed accepted-source manual preparation run, sole successful
job, latest attempt=1 and allowed actor; no automatic preparation dispatch effect.
Outer hosted job has platform artifact upload credentials, but no writer/private
credential/Environment/packet. Owned utility child has fresh HOME/TMP, isolated
Git/Nix config, fixed binaries, allowlisted environment and bounded process-group
termination. Do not call environment filtering OS isolation; actual separate hosted
run/platform credential observations are operating gates.

Artifact refresh-data-v1 contains only regular receipt.json/before.lock/after.lock.
Receipt exact keys: format, repository-id, run, attempt, job, workflow-path,
workflow-blob, source, base, utility-source, utility-manifest, source-fingerprint,
before-lock, after-lock, lock-mode, status, input-inventory. Status changed/noop;
failure/timeout produces no consumable data. Input inventory is the original
utility independent/follows/excluded/selected result. No asserted head, declaration,
approval or check result. Reconstruct original before bytes/mode/source and compare
literal validated after data. Run metadata does not supply dispatch inputs.

Artifact metadata binds run/digest, not uploader job/attempt: accepted original
single-producer workflow plus sole job and attempt1 establishes the narrow producer
contract. Bound pages/counts, exact sole artifact/name/nonexpiry/run/source/id/digest,
then reobserve after download. First contract limits archive4 MiB, decoded2 MiB,
each lock256 KiB (matching object limit), receipt128 KiB, exact3 entries; reject
duplicates/traversal/special/encrypted/unsupported/CRC/size/expansion/trailing data.

A new separate binary reader accepts precisely the fixed artifact API's bounded
302 Location as a transient data capability. Existing JSON transport stays fixed
host/no redirects. Delegated reader uses absolute HTTPS443, no userinfo/fragment,
bounded DNS URL, all resolved addresses public and connection pinned to a validated
address with original-host TLS/SNI. No forwarded auth, cookie, netrc, proxy or
second redirect; one bounded200 GET, <=30-second network phases and <=60-second
total window. Signed URL remains memory-only. Verify archive SHA256; expiry,
redirect, malformed Location, nonpublic address or changed metadata refuse.
Data read permission, if needed, is independent Actions-read and never writer PAT.

Bind exact run/attempt/job/artifact/archive/receipt/base/source/utility identities
to one batch preparation consumption. A completed run is not owner authority and
cannot be reused by a second batch. Durable protocol-4 consumption representation
must be reviewed with the preparation child before writer pickup; object source
may proceed independently of this still separate producer/consumption implementation.
Domain owner supplies exact reviewed Release-* fields through separately approved
custody. Missing declaration is a finite blocker, including scheduled wakeups.
Actual download/OS isolation/permissions/native utility/declaration receipts stay
operating gates, not synthetic fixture conclusions.

## Reviewed original-data and consumption correction, 2026-10-04

This amendment supersedes the optional required-base merge construction described
above for the first protocol 4 source. Initial-only means previous='-' and parent=base;
required-base merge remains non-deferred under refresh-merge-proof/spec.md. A supplied
merge tree plus parent labels cannot establish computed Git merge provenance.

Construction exact keys are format, inputs, originals, objects, digest. Inputs add
preparation to batch/source/base/previous/before-lock/lock/utility-source/
utility-manifest/source-fingerprint. Preparation digest is SHA256(canonical public
repository/run/attempt/job/artifact-id/archive-sha256/receipt-sha256/base/source/
utility-source/utility-manifest)); exclude batch and all transient writer identities.
Originals are ordered type/sha/raw objects: base commit, root tree, each direct path
ancestor tree, before-lock blob. Hash all original raw bytes, verify tree links and
complete entry lists, replace only lock/ancestor SHAs, and compare every untouched
entry literally. Unaffected blob contents are not required because exact entries
retain their original SHAs. Reject duplicate or unused originals and extra generated
objects. Initial generated parent must equal base. Only generated commits require
unsigned fixed canonical headers; signed/extra generated headers refuse. Original
base commits accept bounded well-formed original headers, including multiline
gpgsig. Hash whole literal original bytes, preserve signatures/extra headers and
parse one unique tree plus ordered parent headers without rewriting the object.
Malformed/orphan continuation lines, duplicate tree, invalid parent identity or
ambiguous header/message framing refuse. This does not assert signature validity.

Source feasibility observation on 2026-10-04: observed origin/dev 1e635ffd has a
1240-byte original commit, tree 09b80c5c2334d8b296d69b0af0dc4a403706cfb6,
two ordered parents and a multiline gpgsig header. It fits the proposed individual
raw bound; no operating or signature-certification evidence follows. Add signed
original-base positive and malformed continuation/header negative fixtures.

Construction digest covers canonical format/inputs/originals/objects only. Derive
operation IDs topologically afterwards; no own digest or operation ID enters this
digest. Originals <=8 and generated objects <=8; decoded combined bytes <=512 KiB,
individual raw <=256 KiB, complete canonical construction <=1 MiB. Existing name,
entry, dependency, message, depth and complete-transcript bounds remain unchanged.

Original protocol 4 replay returns preparations[] digest/batch pairs derived only
from accepted refresh-result events, not unused transcript revisions. Global loader
aggregates validated original replay output after each batch, checking exact output
schema/batch identity and bounded cardinality, permitting same-batch reuse and
refusing same digest consumed by different batches. It never substitutes a current
reducer or inspects old protocol 1/2/3 with new semantics. Metadata remains asserted
offline until independently observed transport custody supplies its real provenance.
