# Preparation runtime and declaration staging study
kind: study
date: 2026-10-04
scope: repository
status: open

# Preparation runtime review
Observed: 2026-10-04. Read-only official upstream data/download inspection only.

## Fixed Nix recommendation

Use official x86_64-linux Nix 2.34.8 tarball:
https://releases.nixos.org/nix/nix-2.34.8/nix-2.34.8-x86_64-linux.tar.xz
SHA256 2c2e146b80834fe0ca201b51deeb939405b4f18e8d2071bf80b10f8123c50464
Downloaded 25349172 bytes into /tmp/configs-preparation-runtime and independently
hashed; matches official adjacent .sha256 contents:
https://releases.nixos.org/nix/nix-2.34.8/nix-2.34.8-x86_64-linux.tar.xz.sha256

Official bootstrap URL https://releases.nixos.org/nix/nix-2.34.8/install downloaded
4267 bytes, SHA256 96c10e102c88809dd9ec0bee89200c4a51eae4c9f6d8698c26b16788d131e078.
Choose verified tarball directly to avoid bootstrap transitive-download ambiguity;
review bounded archive members and installation logic before future installation.
No installer was executed. Tarball contains 2234 entries and 63 store-path prefixes.
Selected executable /nix/store/v2s32a5zyxbq681gvdab224xmln4hzg4-nix-2.34.8/bin/nix
is 3875576 bytes, SHA256 f6b457269b635c7744426ca5eb8f2b63f5de919012217bb593357fca0b1763c9.
Original .reginfo SHA256 944af3cbc5eaa3178c6d1006eef0092f87cb0852b786742d60733402d8744ffd
records original reference closure including glibc/gcc libraries. Archive digest binds
all included bytes, but ELF/library resolution and functioning hosted runtime remain
unverified; existence of .reginfo is not realized closure or build proof. Host Nix
installation, daemon settings and credential-free execution are not established.

## Fixed Python recommendation

Repository CI currently requests Python 3.13, not an exact patch/build. Recommend
regular GIL-enabled x64 CPython 3.13.16 on Ubuntu 24.04 (not freethreaded). Official
GitHub-maintained actions/python-versions immutable manifest snapshot:
https://raw.githubusercontent.com/actions/python-versions/52ee1aa09f9f41a759b7a7010eda15fb0e2b190e/versions-manifest.json
Manifest SHA256 bb93b51c286c083e2cd7fdeafdd23a022da4ef72576b7e2a3f8dc9beebd48592

Official release build 3.13.16-36805956071:
https://github.com/actions/python-versions/releases/tag/3.13.16-36805956071
Asset https://github.com/actions/python-versions/releases/download/3.13.16-36805956071/python-3.13.16-linux-24.04-x64.tar.gz
Official GitHub release API asset size 102730838, digest
sha256:d6f5f504043400592e9dcf368ba262c64d998608646cc22281b5a75beecbc872.
Asset digest was first observed from the primary API. Later on 2026-10-04 the
102730838-byte archive was independently downloaded and SHA256 matched that digest.
Its 9338-member inventory was read without extraction/installation/execution;
bin/python3.13 SHA256 is
329d378575992732511d75b3bd675cb91b3c65f3082783cd97ccb14f0ecd5a74.

Fixed setup-python source ece7cb06caefa5fff74198d8649806c4678c61a1 supports manifest
resolution of exact 3.13.16. Set python-version 3.13.16, architecture x64, check-latest
false, freethreaded false; verify actual executable/profile before utility invocation.
Source: https://github.com/actions/setup-python/blob/ece7cb06caefa5fff74198d8649806c4678c61a1/src/find-python.ts
An exact patch does not bind rebuild ID: setup-python manifest/toolcache can select
a different same-version build. Strict build custody therefore requires independently
verified fixed asset acquisition or wrapper verification against admitted asset/build;
setup-python alone cannot be claimed to pin this release asset. Future native source
fixtures must prove selected interpreter/runtime and Python -I import isolation.

## Credential and verification limits

Read-only cachix/install-nix-action source 8aa03977d8d733052d78f4e008a241fd1dbf36b3
exports github.token and installer falls back to writing it to Nix access-tokens:
https://github.com/cachix/install-nix-action/blob/8aa03977d8d733052d78f4e008a241fd1dbf36b3/action.yml
https://github.com/cachix/install-nix-action/blob/8aa03977d8d733052d78f4e008a241fd1dbf36b3/install-nix.sh
Empty github_access_token does not prevent fallback. Do not use this action in
credential-isolated producer without separately reviewed correction. Proposed direct
checksum-bound installer execution must filter credentials and audit system/user/
daemon config; these hosted properties are pending actual evidence. Outer artifact
uploader legitimately uses platform credentials; writer/private credentials must stay
in a distinct run/Environment. This investigation proves no hosted isolation,
permission, native runtime, private custody or operation. No installer/process execution,
API writes, dispatch, Git mutation or host installation occurred.


# Data-only declaration staging review
Observed 2026-10-04; root proposal, not adopted policy.

## Conclusion

Possible without a new protocol4 reducer event or index format, but requires an
explicit current transport/loader auxiliary-record contract. Original semantic state
and exact current/index.tsv bytes remain unchanged; no declaration-staged event.
Actual private write authority remains separately gated.

## Concrete current blockers

Journal.publish currently permits only history/current/control paths, so
review/declarations/<sha256>.json is refused. Snapshot.validate_changes accepts only
an exact existing pending event projection. Snapshot.validate_prospective assumes
current/transcript.json exists and takes its last source row. Thus merely widening
Journal path regex is unsafe and insufficient. Add a distinct strict data-only
projector and proposal validation/acceptance path, not a pretend semantic event.

Loader verify_append_only_snapshot protects history/ and current/batches.tsv only;
it does not protect declaration paths. Add dedicated read-only whole original
private-history path integrity checking, without changing original package replay.
Existing global_preview can replay unchanged semantic history/index, but must check
that an auxiliary commit leaves every existing leaf and all semantic inputs unchanged.
A real private commit is not proof of numeric source/run/job custody: packet/source
schema must retain independently reobservable staging bindings. Fixed commit author/
date and operations ref ancestry alone do not identify actual staging job.

## Recommended strict source interface

propose_declaration_data(snapshot, canonical_packet, staging_binding) returns exactly
{review/declarations/<sha256>.json:raw,current/index.tsv:original_index_bytes} plus
in-memory exact source/batch/owner/generation/run/attempt/job/head/stop/preparation
binding and proposal digest. No transcript/context/history/config/stop mutation.
Reject missing live original4 batch, pending proposal, unknown operation fences,
stale preparation, unavailable custody, preexisting path or altered packet bytes.
Validate complete parent original replay; construct prospective private tree locally
and replay it independently, requiring byte-identical projection and state result.
Before every object/ref effect and before journal acceptance freshly recheck the
same source/runtime/head/stop/preparation guards. Existing Journal per-effect guards
must be strengthened explicitly for this projector rather than assumed complete.

The immutable packet must carry source-bound staging metadata (numeric run/attempt/
job/actor, batch/generation/parent-head and preparation identities) or an exactly
specified same-path canonical envelope containing declaration plus staging custody.
Choose that schema before pickup; current seven-field declaration packet alone is
insufficient for later independent introduction-custody observation. No own child
commit SHA is embedded. Review digest covers entire retained canonical record.

observe_declaration_data(acquired_original_private_history,digest) derives the unique
single-parent introducing commit where parent lacks path and child has exact regular
100644 blob/raw packet. Verify all other leaves preserved (index exactly same blob),
parent original semantic replay, independent original source/runtime custody and
fresh review/preparation bindings. Traverse complete authenticated private history,
including side-parent changes; reject delete/reintroduce/change/mode changes or
ambiguous introduction. Derive anchor internally; never accept caller anchor input.
Old semantic packages remain unchanged; new current loader knows auxiliary path
integrity but never reinterprets old protocol transcripts.

Quota recommendation: packet64 KiB, maximum256 packets/16 MiB total original packet
bytes across complete acquired history; retain existing128 MiB total acquisition
budget. Count introductions including inaccessible/deleted attempts for integrity;
quota exhaustion refuses, no pruning/reclamation. Apply bounded commit traversal and
output limits separately. Numeric sets/exact schema remain root review decisions.

Unknown object/ref acknowledgement fences this instance. Read-only observer may
classify exact original introduction, absent or conflict; absent does not authorize
retry. Exact history reconciliation plus explicitly authorized continued owner is
required before another proposal. Partial unreachable blobs carry no review authority.
No new semantic sequence/index transition means existing auxiliary-publication receipt
and fencing must be explicit transport state, not silently inferred reducer recovery.

## Required evidence

Fixtures: unchanged original4 projection; forbidden adjacent changes; stale source/
owner/job/head/stop; corrupt canonical packet/custody; introduction on side parent;
delete/recreate; quotas; lost blob/tree/commit/ref response; replay historical original
packages unchanged. Native delivery remains independent. Actual private endpoint
permissions/protection/write receipts, custody and Environment hold are separate
operating gates; source fixtures/commit history cannot certify them.


## Two-digest staging alternative, root review pending

# Two-digest declaration envelope review
Observed 2026-10-04; proposed contract only, no source/operating adoption.

## Feasibility

D0(body) before dispatch and D1(envelope) after runtime observation avoids the
run-ID/digest self-reference. Same finite writer, one sole job and existing writer
concurrency is compatible with the intended ownership model. Domain review of D1
covers both exact declaration and staging custody; no declaration artifact required.
Numeric job metadata alone does not bind body: fixed original run-name displaying
D0 plus independently verified workflow/source binds the preexisting canonical body.

Current release-control-writer.yml is disabled preflight-only, permissions empty,
job writer-preflight, no run-name, Environment or body input. Entry checks exact
source/ref/event/workflow/actor/run/latest attempt/sole job but not display_title;
runtime keyset is exact and includes no declaration digest. Journal rejects new
review paths and current projector requires semantic event/transcript. This proposal
requires explicit new current source adoption; existing CLI implements none of it.

## Exact grammar to settle

Recommend input declaration-body-digest optional string, empty for ordinary modes;
require nonzero lowercase 64hex whenever staging is requested. Run-name expression
must produce fixed literal `release-control:<mode>:declaration:<D0>` for staging,
and a fixed distinct ordinary title for empty digest. Validate mode enum and entire
API display_title, never substring/prefix/derived job output. Verify original workflow
blob binds this exact expression, single input and sole job. No unsupported control
characters/interpolation or display truncation accepted. Input metadata is not read
from run API: only exact fixed display_title is the observation contract.

Envelope strict keys format/body/body-digest/staging; format integer 1. Body follows
exact reviewed schema and canonical hash D0. Staging strict keys controller-source,
workflow,actor,run,attempt,job,batch,generation,operating-parent; numeric identities
strict positive integers, attempt exactly 1, generation original reducer integer,
public source/parent exact 40hex and batch 64hex. Specify workflow numeric ID versus
path explicitly (recommend numeric ID with original source-bound workflow path/blob
in role policy). No child introduction commit is embedded. Hash complete canonical
envelope as D1 and retain at review/declarations/<D1>.json. Reject extra keys,
canonical encoding drift, changed D0/display_title or stale parent/generation.

Parent must be current acquired private head immediately before atomic Journal
stage, with unchanged original index/projection and full fresh owner/source/job/
stop/preparation bindings. If head moves, rebuild only after explicit fresh revalidation;
a changed envelope creates new D1 requiring new domain review, never migrate approval.
Body hosted private transfer must provide exact canonical D0 verification inside
trusted wrapper before stage; provision source contract and actual custody separately.
No current local packet/CLI fixture establishes that transfer.

## Observation and recovery blockers

Read-only observer verifies unique original introducing commit, absent parent path,
exact child envelope/index projection and no unrelated leaf change; every later
transition preserves packet bytes/mode/path. Replay original parent state and compare
its batch/generation/owner to staging custody. Independently verify original numeric
run/attempt/job/actor/source/workflow and exact D0 title against retained envelope.
Live staging requires running sole job; historical observer must separately permit
terminal original job with expected timestamps, not construct current writer Entry
from a completed run. Deleted/missing/moved run evidence refuses; no invented custody.

The future source plan must define partial object/ref write fencing and durable
observer result binding. Unknown acknowledgement: same instance cannot retry;
reconcile exact original introduction first. Absent receipt or terminal earlier run
alone grants no retry/takeover authority. Domain review D1 must independently bind
exact successful reviewer run/job/Environment/approving numeric reviewer/comment;
actual pre-job hold/protection remains separate operating evidence.

No second writer workflow/job is introduced. Missing canonical body, invalid digest,
unsupported original runtime/review API, stale owner/parent, quota excess or absent
actual custody refuses finitely. D0/D1 contract does not authorize private writes,
bootstrap, dispatch, credential provisioning or source implementation by itself.
