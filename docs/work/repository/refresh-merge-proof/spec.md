# Verify original required-base refresh merge provenance
kind: spec
date: 2026-10-04
scope: repository
status: approved
review-by: 2026-10-18

## Assignment and dependencies

Root owns this non-deferred follow-up after initial-only refresh-object-protocol.
This is not ready for implementation until exact original merge evidence and bounds
are reviewed. Pin current dev and reviewed plan separately at pickup. Deliver one
repository semantic/loader outcome followed by separate transport custody adoption;
root retains serialized rules/manifest ownership. No old protocol batch migration.

## Required proof contract

Bind original previous/base commits, complete ancestry to independently determined
merge bases, all trees and blobs required by actual Git merge computation, exact
ordered merge parents [previous,base], resulting tree and final lock-only head.
Unknown/shallow/missing graph, multiple ambiguous bases, conflicts or unsupported
merge behavior refuse. Direct root/unixlike trees alone are not complete merge proof.

The reviewed original package must independently realize a bounded bare object
database from hashed literal original data and run credential-free Git merge-tree.
No checkout, remote/fetch, lazy objects, replacements/grafts, hooks, external attribute files,
external merge drivers, user/global config, private connection or token may reach
this subprocess. Pin supported Git behavior/runtime and explicit environment;
validate the resulting full tree hash and preserve every original non-lock change
produced by the required base merge. Then independently verify the final commit
changes only the lock relative to that computed merge parent. Transport-generated
merge labels or asserted success do not prove original computation.

Exact raw-object carrier, full graph completeness algorithm, executable closure,
supported merge-base cases and byte/runtime bounds require a dated reviewed design
before source pickup. If proof exceeds initial construction/transcript bounds,
return to planning instead of trimming ancestry or silently widening limits.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Reviewed complete original merge carrier, graph/merge-base algorithm, runtime closure and bounds independently compute exact required-base merge without privileged or ambient execution. | review, policy checks |
| AC2 | New original semantics verify ordered parents, computed merge tree and final lock-only construction while preserving original protocol1/2/3 and initial-only protocol4 behavior. | fixtures, policy checks |
| AC3 | Actual disposable Git and exact-head native evidence cover clean merges, conflicts, missing graphs, wrong trees, contaminated locks and isolated runtime; transport custody/API/operating proof remains separate. | fixtures, policy checks, affected dispatch, review |

## Stop conditions

Replan for incomplete original objects, unsupported Git merge behavior, new closure,
changed bounds/schema, competing source ownership or real API/credential requirements.
No dispatch, publication, initializer, promotion, release, schedule or host changes.

## Design amendment, 2026-10-04

Amended 2026-10-04: AC1 requires the complete-DAG, three-snapshot carrier and
original introduction contract below. AC2 requires complete bounded novel merge
object closure before refs. AC3 includes attribute/runtime, immutable-history and
staging/recovery fixtures. Original criteria remain; source pickup is NOT ready.

Protocol 5 selects its original package and carrier format. Each generation binds
manifest SHA256/Git blob, previous/base, independently derived unique merge-base
and runtime profile. Neither event nor manifest embeds a caller anchor commit.
Derive the unique authenticated event-introducing commit from original private
journal transitions. Carrier/event/index can then share one atomic journal commit
without a self-hash cycle. Protocols 1-4 keep original semantics and replay layout.

Store carriers/<manifest-sha256>/manifest.json and numbered chunks beneath its
chunks/ directory. Strict manifest binds roots, object types/OIDs/sizes/offsets,
chunk sizes/SHA256/Git blobs. Frames contain literal raw objects, no packs/deltas.
Verify each Git type/length hash. Supply complete commit DAG to literal zero-parent
roots, compute best common ancestors and refuse zero/multiple bases. Supply full
recursive tree/blob closures for previous, base and unique merge-base only.
Reject incomplete/cyclic/unrelated graphs, duplicates, symlinks/gitlinks and unsafe
names/modes. Canonical raw directory mode is 40000.

Proposed limits: 4096 commits, 32 parents/commit, 64 KiB/commit, depth 4096,
4096 trees, 4096 blobs, 1 MiB/blob, 16 MiB raw objects, 24 MiB retained carrier,
256 KiB manifest, 24 chunks maximum of 1 MiB each, 256 MiB scratch disk,
120 seconds whole proof and 1 MiB command output. Define aggregate history quotas
before pickup; exhaustion refuses. Keep existing 4 MiB API/transcript framing.

At original introducing tree verify exact regular carrier paths/modes/hashes,
manifest digest and complete chunks. New carrier is absent in parent, complete in
child; initial design refuses reuse. Check every later transition for immutable
paths/blobs: deletion/recreation refuses. Materialize original bytes only into owned
batch; original package repeats content validation. Loader provenance is not merge
correctness. Unknown publication acknowledgement fences continuation, not retry.

Construct isolated fresh bare SHA1 ODB through bounded hash-object writes of
verified literals. No checkout/index, fetch/remotes, lazy objects, packs, alternates,
grafts/replacements, templates/hooks, credentials/proxies or ambient config.
Cross-check independently derived base with merge-base --all; run merge-tree
--write-tree --no-messages --merge-base=<unique-base> previous base. Require exit 0
and one exact tree line. Proposed exact profiles: Linux/macOS Git 2.55.0 and
Windows Git 2.55.0.windows.5; supported behavior/executable closure remain pending
positive/negative native fixtures. Installed version alone certifies nothing.

Supply/parse every operand .gitattributes blob. Preserve strictly bounded built-in
text, -text, text=auto, eol=lf/crlf and binary values. Refuse macros, custom
merge/filter/diff drivers, encoding and unsupported declarations. No info/global/
system attributes. Unsupported originals cause finite refusal; disabling attributes
must never be mislabeled preservation of ordinary Git merge semantics.

Required-base merge has parents [previous,base] and computed full tree. Final
single-parent dependency commit changes only unixlike/flake.lock with unchanged
mode. Initial protocol 5 retains 8 generated objects/512 KiB generated bytes.
Derive/publish/independently observe complete novel computed merge object closure
before refs; verifier-generated trees are not presumed public. Initial support
requires all non-lock leaves/modes/empty trees equal new base; outside this support
or object bounds refuse/replan, never discard computed changes to fit.

Carrier staging/publication, authenticated transition selection, loader interface/
aggregate quotas and unknown-response recovery remain unresolved prerequisites.
Source/native, transport custody/API and actual private/manual/scheduled proof are
separate. No source assignment follows this design amendment alone.

## Native attribute profile clarification, 2026-10-04

Actual disposable macOS Git 2.55.0 review found that bare merge-tree without an
explicit attribute source ignores repository binary declarations. The initial
supported profile therefore sets GIT_ATTR_SOURCE to the independently verified
previous/ours commit, forces merge.renormalize=false, and admits only byte-identical
.gitattributes path/mode/blob inventories across previous, base and merge-base.
Attribute evolution returns to planning. Preserve supported original built-in
attributes, including the built-in binary spelling; user macros remain unsupported.
Do not normalize operand blobs silently or disable original attributes wholesale.

An exploratory merge.renormalize=true run aborted inside Git on bare text/eol data;
that profile is unsupported. Any abort, nonzero result or extra output refuses.
The default-false isolated profile with explicit original attribute source passed
tiny clean/novel-object and attribute fixtures. Source/native Windows/Linux,
executable closure, bounded stress and actual private/public receipts remain pending.

## Preparation identity clarification, 2026-10-04

Required-base preparation runs on the independently computed complete merge tree T,
not a future merge commit whose timestamp depends on that job's completion. A
separate versioned required5 receipt binds input-kind=computed-merge-tree, T,
previous/base/unique merge-base, original carrier/runtime profile and independently
approved utility/producer source identities. Original1–4 receipt/candidate semantics
remain unchanged. Exact receipt grammar and path-Nix source-metadata support still
require review; this clarification does not assign implementation.

Observe actual successful producer completion and its timestamp after the job ends;
a producer cannot author its own future completed-at into its artifact. Then form
canonical merge commit M with tree T and ordered parents previous/base, and final
head H with parent M. Candidate source=parent=M; before-lock is the literal merged
lock from T, not the base operand lock. Compare H's complete tree to T with only
the lock replacement. Preparation consumption excludes M/H, batch, transient writer
identity, construction digest and operation IDs, preventing hash/time cycles.
Controller source, utility source, producer source and candidate source remain
separate explicit identities. Missing or changed bindings refuse.

## Proposed contract amendment, 2026-10-04

Amended 2026-10-04: AC1 requires the explicit carrier/runtime/producer/declaration
and original replay interfaces below; AC2 includes the original5 initial/required
union and protocol-specific exact executable closure; AC3 includes both-direction
original-history, runtime/attribute, quota and recovery fixtures. Original criteria
remain. This is a review draft prepared on actual dev c69fbc8; source pickup is
NOT ready and no implementation is assigned. Root must accept the remaining typed
runtime trust predicate and contract choices before source pickup.

This amendment supersedes the original blanket attributes exclusion only to admit
independently parsed identical original built-in .gitattributes; all external
attribute sources/drivers remain excluded. Source structural/native fixture proof
and independently provisioned runtime/domain trust are separate gates. No profile
hash, approval digest or synthetic receipt establishes actual operating admission.

### Protocol and unchanged envelopes

Original protocols1–4 remain literal source/manifests/reducers/layouts. Only original5
records admits approved/config/batch-start protocol='5'. TSV format remains1.
EVENT_FIELDS, BASE fields, tuple arities and kinds are copied explicitly from4 without
optional extra fields. refresh-result payload is exactly {status,candidate} for changed
and exactly {status} for noop/failed/terminated-timeout; nonchanged cannot replace an
existing candidate. refresh-integrated payload stays exact
{base,head,commit,parents,tree}. Global context remains12columns,
CONTEXT_FIELDS=(start,batch,master,control,manifest,approval,protocol,config-commit,config,transcript-commit,transcript);
no carrier introduction anchor column. Approved/control/manifest always refer to
executing source package, not carrier.

Candidate is exact13 STRING keys
{batch,source,base,parent,head,tree,before-lock,lock,utility-source,utility-manifest,source-fingerprint,previous,branch}.
IDs/digests/branch grammar unchanged. Context exact7
{prepared,proof,current-dev,branch,checks,integration,construction}; proof exact7
{head-parents,merge-parents,changed,before-lock,lock,before-mode,mode}; branch exact3
{batch,branch,head}. Current-dev=B at preparation (or actual integration commit in
existing integration checks), not M. Required update: previous=P, source=parent=M, M
tree=T/ordered parents[P,B], H tree=U/parentM; before-lock is literal T-lock, not
B-lock; final changed list exactly unixlike/flake.lock and unchanged lock mode.

An original5 batch MUST first create/observe its own initial candidate, then require
changedbase/observed oldhead as previous exactly as4 owner-state transitions. No
migration or borrowing an outstanding4 batch. To make this reachable without invented
ownership, original5 explicitly retains the exact initial-only format1 construction
grammar copied from4 for previous='-', source=parent=base; no merge carrier/runtime
proof involved. Its initial producer uses the separately adopted original4 data receipt
contract. Required update alone uses construction5 below. This is an explicit NEW5 union
selected by previous/format, not a modification of original4 or relabeling old source.
Initial format1 is forbidden for previous!='-'; construction5 forbidden for
previous='-'. All accepted5 preparations, including initial, count toward new5 bound4.

### Exact construction5 and nested data

Construction5 exact keys
{format,inputs,carrier,receipt,completion,declaration,objects,digest}; format integer5.
Inputs exact
{batch,source,base,previous,before-lock,lock,utility-source,utility-manifest,source-fingerprint,preparation},
all existing candidate equality bindings plus preparation64hex. Compact carrier exact
{format,manifest-sha256,manifest-blob}, format integer1/64hex/40hex. Receipt is the full
canonical public receipt5 DTO below; no path/opaque digest substitution. Completion is
full bounded observed DTO below; declaration includes exact approved content/custody
reference below. Objects exact ordered list rows {type,sha,raw,dependencies}, canonical
base64 raw; dependencies exact type/sha rows derived from object bytes, not caller
authoritative. Existing generated payload exact8keys and topological operation-ID
derivation remain; object plan/payload differs by original5 construction semantics only.
Digest SHA256 canonical exact construction excluding own digest; includes every other
field, excludes operation IDs/introduction commit. All object raw hashes/type/length
validated; <=8generatedobjects/512KiB decoded aggregate, no duplicate/unused rows, no
omitted novel merge closure.

Receipt5 exact
{format,kind,repository-id,run,attempt,job,workflow-path,workflow-blob,producer-source,utility-source,utility-manifest,source-fingerprint,input-kind,input-tree,previous,base,merge-base,carrier-manifest,git-runtime-profile,preparation-runtime-profile,base-lock,before-lock,after-lock,lock-mode,status,input-inventory}.
format5, kind refresh-data, input-kind computed-merge-tree; numeric IDs positive strict
integers, attempt1; status changed for consumable construction5 (noop observed
separately, no construction/consumption). Input-inventory exact
{independent,follows,excluded,selected}; sorted unique named lists, follows
name->nonempty named path list; original utility exact selection rules preserved. All
commit/tree/workflow blob40hex; lock/runtime/manifest/fingerprint64hex. carrier-manifest
is exact compact object equal construction.carrier. Producer-source is actual completed
manual producer workflow source, utility-source selects independently reviewed actual
executable blobs, controller-source is context.master/approved master and NOT
candidate.source=M.

Fingerprint SHA256 canonical ordered list of rows {path,sha256,mode} for every regular
file in literal T:unixlike/ subtree BEFORE lock replacement, sorted UTF8 pathbytes,
domain-relative paths, mode permission bits. No .git/temp paths exist in this original
immutable map. Realization ignores only owned `.refresh-inputs-running` and exact
created `.refresh-inputs-*` transient folders per utility; immutable files cannot hide
behind those names (refuse preexisting reservednames). FullGit treeT binds
outside-domain entries independently. Utility-source admitted bytes must equal
corresponding T tool bytes; mismatch finitely refuses in first contract, no unreviewed
copy substitution. Path/mode/mtime realization and exact path-Nix behavior remain native
custody gates; sourcefixtures cannot certify them.

Completion exact {run,attempt,job,completed-at,observation-digest}; run/attempt/job
equal receipt, attempt1, canonical UTC `YYYY-MM-DDTHH:MM:SSZ`, strict valid date>=1970;
observation-digest64hex. Consumer independently observes actual successful sole
job/latest attempt and reobserves it after artifact read; producer never predicts its
own future job completion or includes M/H. Original semantic fixtures validate exact
equality/epoch structure only. Completion digest itself is not authenticity. Canonical
generated metadata timestamp is integer epoch of completion.completed-at; approved
runtime profile defines identical conversion, no ambient clock.

Declaration exact {format,envelope,digest}; format1. envelope is the FULL original D1
object, exact {format,body,body-digest,staging}, format1. Body exact
{format,preparation,source,base,before-lock,after-lock,utility-source,utility-manifest,source-fingerprint,rules-source,rules-digest,semantic-protocol,semantic-manifest,declarations}.
Body format1; source=M, base=B, before-lock=T-lock, after-lock=candidate.lock (SHA256 of
final lock bytes); preparation equals accepted preparation digest; utility/fingerprint
equal candidate/receipt, rules-source=original approved executing source40hex,
rules-digest=original classifier rules64hex, semantic-protocol='5',
semantic-manifest=original executing package manifest64hex. declarations exact seven
STRING keys
Release-Format,Release-Domain,Release-Impact,Release-Contracts,Release-Compatibility,Release-Rationale,Release-Migration;
values exact reviewed parser grammar (1/unixlike/none|patch|minor|major/sorted unique
comma contracts/compatible|breaking/nonempty bounded singleline/none or canonical docs
path), no default or opaque digest substitution. Staging exact
{controller-source,workflow,actor,run,attempt,job,batch,generation,operating-parent};
numeric workflow/actor/run/job positive, attempt1, batch64hex, generation original
canonicaldecimal, controller-source and operating-parent40hex. Staging
source/runtime/owner/generation/parent are HISTORICAL at unique original introduction,
not forced equal to current owner/generation/head.

Hash canonical FULL body bytes to body-digest=D0; hash canonical FULL envelope to
declaration.digest=D1. Original5 validates exact nested sets/canonical bytes/D0/D1, all
body/candidate/receipt/source/package equality and generated7trailers equality. Loader
independently materializes byte-identical retained D1 from original
review/declarations/<D1>.json and validates actual unique introduction/immutability.
construction.declaration.envelope must byte-equal that materialized original, not a
locally manufactured envelope with matching asserted digest. The later declaration
observer supplies actual original stage success+domain review
exactD1/title/comment/reviewer provenance; hashes are not actual approval. No opaque D1
or review-digest alone proves seven fields. Full envelope <=64KiB/each
string<=4096UTF8bytes. Future current generations revalidate eligibility/data and
current effects; never migrate domain approval to a changed envelope. This preserves two
independent predicates H(original staging/review) and C(current effect authority).

Proposed-M causality: after actual producer completion is already observed, compute a
PURE OFFLINE proposed M hash from T, orderedparents[P,B], completion epoch and PROPOSED
sevenfields. This is data-only calculation with no private/public object write,
refresh-result or permission claim. It permits body.source=M and D0 before D1
staging/domain review. Domain review binds full D1. ONLY AFTER actual accepted review,
rederive M from exact original D1 sevenfields/completion/roots and require equality to
body.source; derive H/authorized construction, then permit durable refresh-result
subject to current owner/source/head/stop gates. Changed fields/date/roots change
M/body/D0/D1 and require fresh review, never reuse approval. Receipt/preparation/carrier
still never contain future M/H. Proposed hash availability is not construction/effect
authorization.

Merge M exact unsigned headers tree,parentP,parentB,author,committer (two unique
orderedparents); finalH exact tree,parentM,author,committer. Actor/committer `Release
controller <release-controller@example.invalid> <completion epoch> +0000`. M prefix
`chore(unixlike-deps): merge required base`; H prefix `chore(unixlike-deps): refresh
reviewed inputs`. Blank line then fixed seven trailers in order
Release-Format,Release-Domain,Release-Impact,Release-Contracts,Release-Compatibility,Release-Rationale,Release-Migration,
exact reviewed declaration values, canonical LF/finalLF. No signature/extra generated
header/default. Originals preserve well-formed signed headers/raw bytes unchanged. M/H
formed AFTER completion+declaration observation; receipt/carrier/preparation contain no
future M/H.

Preparation5 digest SHA256 canonical exact object
{format:5,public-repository,run,attempt,job,artifact-id,archive-sha256,receipt-sha256,producer-source,utility-source,utility-manifest,roots,input-tree,carrier-manifest,git-runtime-profile,preparation-runtime-profile,source-fingerprint,before-lock,after-lock,lock-mode};
roots exact previous/base/merge-base, public-repository fixed shk95/configs.
Artifact/archive/receipt literal provenance supplied separately by authenticated public
producer bridge, not guessed from data receipt. Exclude
batch/M/H/completion/declaration/opIDs. Version5 prevents digest grammar ambiguity, not
automatic evidence authenticity. Missing custody freezes source-only assertions.

### Canonical manifest/chunk frames

Manifest exact {format,kind,roots,runtime-profile,objects,chunks,raw-bytes}; format1,
kind required-refresh-merge; roots exact previous/base/merge-base40hex;
runtime-profile64hex accepted original profile identity. Canonical UTF8 JSON
sort_keys/no-whitespace/ensure_ascii=False/no nonfinite/duplicatekeys. Objects sorted
unique by OID (not type), exact {oid,type,size,chunk,offset}; type commit/tree/blob,
strict nonnegative integer size/offset, numberedchunk1..N. Chunk rows ordered1..N exact
{number,size,sha256,git-blob}; filename chunks/%06d.bin. All paths regular100644, no
callerpaths/extraentries. Outer manifest.json canonical digest/ Gitblob exactly compact
reference; no embedded selfdigest/path/introcommit.

Each raw frame is ASCII `type SP canonical-decimal-size SP full40hex-oid LF`,
immediately followed by exactly size rawbytes. Object offset points to FRAME HEADER
start; manifest size refers only raw payload bytes. Each frame wholly inside onechunk;
exact concatenation covers chunk0..size with no gaps/overlap/padding/trailingbytes.
Verify frame type/size/OID equal descriptor and SHA1(ASCII(type + space + canonical
size) + NUL + literalraw) equalOID. Chunks' literal SHA256/Git blob identities exact.
raw-bytes equals sum payload sizes. Canonical packing: traverse OIDsorted frames, append
to currentchunk if totalframe fits<=1MiB; otherwise begin nextchunk. No arbitrary
rechunking permitted. A1MiB blob does not fit1MiB chunk includingheader: actual accepted
raw max=min(type limit,1MiB-headerlen); excess finitely refuses, never splitframe or
widenchunk. This resolves the prior size/frame boundary ambiguity.

Complete commit DAG zero-parent roots, unique independentlyderived bestbase, full
recursive previous/base/base-of-merge snapshot closures and original attr inventories
required. Reject unused/duplicate/missing/cyclic/unrelated/shallow data,
symlinks/gitlinks/unsafe modes/names. Tree directory rawmode40000. Identical attr
inventories across all3 snapshots; admit only builtin
text/-text/text=auto/eol=lf/eol=crlf/binary spellings and compatible exact combinations,
no user-definedmacro/driver/encoding. Unknown/conflict/multiplebase refuses. Compute via
fresh bare ODB, explicit GIT_ATTR_SOURCE=P and merge.renormalize=false; enumerate all
novel blob/tree literals, construct M and only-lockH independently. All non-lock
leaves/modes/emptytrees must equalB for initial supportedsubset. Runtime ODB objects
neverpublicreceipts.

### Finite runtime admission/data flow

PROPOSED first operating profile: independently provisioned Linux native Git2.55.0 exact
executable/dependency closure, qualified separately before operation. macOS
sourcefeasibility and fixture provisioning establish no operating admission. Do NOT
hardcode unknown hashes as if accepted or require current source delivery to invent
them. Original5 NEW config exact10 keys = original4 exact9
{enabled,public-repository,repository,operating-repository,operating-ref,workflow,actors,checks,protocol}
plus git-runtime-profile. This additional key is original5 only; original1–4 config
grammars remain literal and refuse it. git-runtime-profile is64hex and binds the
canonical FULL immutable admission envelope below through config
blob/context.config/config-commit and independently reviewed source/approval custody.
Missing/unknown/mismatched admission finitely refuses required merge; carrier's
self-asserted profile can never select authority.

Admission envelope exact {format,profile,authorization}; format1. profile exact
{format,platform,version,executable-sha256,closure-digest,options,attributes-policy,limits};
profile format1/platform='linux'/version='2.55.0'/actual executable and
completeclosure64hex. authorization exact {controller-source,approval-digest};
controller-source40hex must equal original approved.master/context.master;
approval-digest64hex must equal original approved.approval selected by that
package/context. These equality checks bind the admission to the original
source-approval contract, not carrier or producer assertions. Independently provisioned
runtime trust must additionally certify that this source/approval contract admits the
exact configured profile; offline source-approval assertions alone remain unqualified.
Store exact canonical envelope regular100644 at
review/runtime-profiles/<git-runtime-profile>.json; config digest hashes full envelope,
not profile body alone. Manifest/receipt git-runtime-profile digest equals this full
envelope identity. Loader derives unique original introduction, verifies immutable
everylatertransition and independently source/approval-bound config-profile custody;
unresolved/unknown review authority means unqualified, not an invented default.

Smallest source interface: global loader reads exact original5 config profileSHA,
materializes original immutable envelope bytes at owned batch runtime/profile.json AFTER
structural/provenance verification; original5 merge_proof.py validates exact
config/envelope/carrier/receipt equality and finite profile grammar. Credential-free
replay accepts a provisioned location descriptor exact
{format,profile,executable,closure-root}, format1/profile=configSHA, fixed owned
read-only locations selected by INDEPENDENT trusted runtime provisioner (not any
carrier/receipt/caller). Original helper rehashes executable/fullclosure against
anchored envelope before any Git call; mismatch refuses. No new event/context column or
source hardcoded realhash needed. Sourcefixtures may explicitly supply a trusted
disposable fixture admission/config/envelope/provisioning boundary; they prove
binding/refusal only, never actual accepted Linux runtime qualification. Actual
operating config/provenance/review role/provisioner remains an independently authorized
gate.

No private repository path/token/network reaches verifier. FreshHOME/TMP/bareODB, fixed
command/env allowlist, no
remote/fetch/checkout/index/packs/alternates/replace/graft/hooks/externalattrs/merge/filter/proxy.
Effective Gitconfig generated exclusively by anchored original profile; ignore ambient
global/system/source repo config. sourcefixtures cannot certify hosted OS/native closure
or supply missing operating authorization.

Profile options exact
{merge-renormalize:false,attribute-source:'previous',autocrlf:false,safecrlf:false};
attributes-policy exact
{format:1,inventory-equality:'previous-base-merge-base',allowed:['-text','binary','eol=crlf','eol=lf','text','text=auto']};
limits exact
{commits:4096,parents:32,commit-bytes:65536,depth:4096,trees:4096,blobs:4096,blob-bytes:1048576,raw-bytes:16777216,manifest-bytes:262144,chunk-bytes:1048576,chunks:24,carrier-bytes:25165824,scratch-bytes:268435456,proof-seconds:120,command-output-bytes:1048576}.
Admission-envelope canonical hash covers exact profile values AND independent
source/approval binding; actual executable/closure hashes and authorization require
independently observed native provisioning/review before operating admission. No
invented hash placeholders are valid admission.

### Original closure/replay/carrier interface

Fixed helper `merge_proof.py`; protocol->exactclosure registry: original1–4 exact
existing8; original5 exact9=old8+helper. No optionalunion/discovery/hiddenimports;
metadata/hash/originalcontrol provenance strict. Original5 helper imports only verified
originalmodules. Loader approved/config/context/driver allowlists admit5 explicitly.
Original1/2 offsetzero path and original3/4 main.replay signatures/output unchanged.
Original5 main.replay accepts existing directory/transcript/approved/before/prior plus
runtime descriptor and provenanceview; independently parsed from owned files, no
currentreducer substitution.

Provenanceview exact durable
{format:1,kind:'durable',carriers:[{manifest-sha256,manifest-blob,introduction}]};
introduction is loader-DERIVED actual privatecommit40hex, not any caller
event/manifest/hash. Prospective exact
{format:1,kind:'prospective',parent,carriers:[{manifest-sha256,manifest-blob}]}; parent
actual independentlyobserved privatehead40hex, candidatefiles frozen separately by
verifiedtransport proposal. Original5 helper uses onlycarrierbytes/manifest, not
introduction as mergecorrectness proof. Prospective output must be explicitly tagged
proposal-only at caller interface and cannot manufacture durable
consumption/publiccompletion. Completed5 selects
anchoredoriginaltranscript/carrierbytes; outstanding5 selects only
introducedoriginalreferences underactualhistory. Actual event+completecarrier introduced
atomically, immutable everylatertransition; delete/recreate/partial/ambiguousintro
refuses. Unknownprivate publication fences until exactfreshhistory/ref reconciliation.

Original5 durable replay output exact {projection,stage,proposed,preparations,carriers}.
preparations max4 exact {digest,batch}; carriers max4 exact
{manifest-sha256,manifest-blob,batch,generation}; generation canonicaldecimal of
original accepted owner-generation at refresh-result, bound tosameevent, rows
canonicalordered byfirstaccepted sequence/dedup exactidentity. Output derives ONLY
acceptedchanged events; unusedrevisions/noop do not consume. Loader verifies
exactrowsets/IDs/projectedbatch/materializedidentity and globalcrossbatchpreparation
uniqueness. Prospective internalresult MUST NOT be passed to global acceptedconsumption
aggregator; use distinct proposal API result exact
{kind:'prospective',projection,stage,proposed}, never emit
acceptedcarriers/preparations. All stdout<=4096 measured BEFORE emission,
pending/countstrings finitely bounded by eventquota. Old4<=16preparations/exact4result
unchanged.

PROPOSED exhaustive globalinvocation/retained-journal quota:
max4introduced5carriers,64MiB rawsum,96MiB literalcarrier bytes
includingmanifest/frames,96chunks,16384commit/tree/blob descriptors
EACH,4accepted5preparations perbatch;20000events/256contexts/4096privatecommits scanned
for5admission; scratch256MiB and480seconds includinghistory/materialization/allproofs,
output1MiBpercommand/4096replay. Count completed/outstanding/superseded
introducedcarriers; no reuse/deletefreesquota. Existing acquisition128MiB/20000files
remains separately binding (packedoverhead stillmayrefuse). Streaming
byte/disk/deadline/processgroup termination required; capture_output/posthoc cap
insufficient. Exhaustion finitelyrefuses and returnsplanning, never
trimsancestry/widensbounds/cleanshistory. These profile/quota choices are NEW proposals
requiring adopted rationale/invariant, not existingpolicy.

### Acceptance before pickup

Root must review exact union(initialformat1/requiredupdateformat5),
receipt/decl/custody/runtime/provenance interfaces, canonicalframes/limits and native
provisionedclosure strategy; add dated spec/report amendment and accepted durablepolicy
sources where needed. Prove bothdirections literal1–4+new9closure,
exactfield/mixedprotocol refusal, beforemergedlock vsbaselock,
prospectivecannotclaimdurable, privateatomicintro+recovery,
nativeattrs/graph/conflict/runtime, complete
novelpublicclosure/order/4096output/globalquota. Source/native and runtime/API/operating
admission stay separate. Publictransport5 requires its own originalcustody adoption
after semantic5; no ready/sourceassignment follows this text alone.

### Proposed bounded interface corrections, 2026-10-04

The following interface corrections remain part of this PROPOSED contract.
Final root acceptance and source pickup are pending; this draft records no
implementation or operating qualification.

Source approval preexists and hashes only the selected original package authority,
excluding runtime profile envelope/config/qualification results. Runtime authorization
is an independent trusted predicate over exact full envelope SHA, original source
approval, executable/dependency closure; matching asserted source/approval scalars alone
never grants it. Any later qualification/review receipt remains outside the hashed
admission envelope. Closure inventory covers immutable executable/dependency regular
files only and explicitly excludes
profile/envelope/config/receipt/descriptor/source/carrier/ODB/scratch. Descriptor
remains independent trusted provisioner data, not self-asserted event input.

Every glue config reader and empty/disabled/complete selected preview must select exact
protocol grammar: original1–4 keys9; original5 keys10. Original retained config/profile
custody is authoritative. Empty/initial5 accepts exact no-merge sentinel null plus
tagged empty provenance view; it does not invoke Git or require provisioned runtime, and
retains config profileSHA without pretending its unqualified reference is operating
admission. Required5 requires full original profile bytes/provenance and independent
trusted runtime predicate. No disabled initializer silently provisions profile data.
Explicit original5 range CLI receives owned runtime/view files and before/prior,
while1/2 and3/4 dispatch signatures remain literal. Summary512/replay4096 caps are
independent.

Union discriminator is accepted candidate.previous: '-' requires copied
initialformat1/source=parent=base and may replace an unobserved initial under existing
samebatch rules; non'-' requires format5 and independently observed original samebatch
oldbranch head==previous, changed base, reconciled effects. No borrowing outstanding4
ownership. Initial+required consumptions share max4 accepted5 preparations (at most
three required after one initial); only format5 accepted changed events emit carriers.
Nonchanged consumes neither. New5 config/closure/CLI/output adaptations are an explicit
versioned contract and must preserve original1–4 fixtures.

Actual domain approval requires a
separately accepted typed subject predicate over FULL original D1 and original
package/source under independently provisioned numeric domain reviewer role plus exact
approving service comment declaration:<D1>. Neither caller bool nor canonicalhash
substitutes for this predicate. Runtime acceptance likewise uses separately accepted
typed subject predicate over profile body/closure and full envelope identity; later
approval receipt is outside that envelope.

Original D1 introducing-parent projection must independently select protocol5 and the
same original package/source bound by the required5 body; old4 staged records cannot be
migrated/reinterpreted. Historical D1 staging.generation, accepted refresh-result
carrier generation and current effect-row generation are three distinct bindings: check
each against its original event/current authority respectively, never force equality.
Required5 source=M/T-lock/fullD1 equalities apply ONLY constructionformat5 with non'-'
previous. Copied initialformat1 grammar is exact and receives no new fields/equality
rules or silently injected D1 content; preparation/declaration child must adopt actual
initial custody separately while preserving the initial payload grammar.


Every config branch validates original approval/config/context agreement before
field use. Future transport5 StartPlan/initializer/config adoption remains a
separate explicit source outcome; original semantic replay cannot certify that
a new real batch can start. Empty/initial5 durable replay returns carriers=[]
and no accepted preparation until an initial changed event is accepted.
Original4 max16/preparation digest/result schema stays unchanged.

The exact trusted runtime admission predicate remains a SOURCE pickup blocker:
its independently provisioned public/source-approval/profile/closure tuple and
verification interface must be accepted before implementation. This plan invents
no runtime workflow/role or numeric trust identity. Later actual Linux/native
closure, domain reviewer/Environment and API grants are separate operating gates.

## Computational replay and operating runtime admission clarification, 2026-10-04

Amended 2026-10-04: AC1/AC2 distinguish computational replay from actual operating
runtime admission. Root accepts this boundary for the source contract; it does not
assign original5 implementation or certify an actual runtime. Exact complete-closure
verification and trusted-host/loader wiring, fixed runtime-role adoption and the
remaining original5 interfaces require concrete pickup review. No new event/context
column, wire boolean or topology is introduced.

A pure ProfileAnchor validates canonical original config10/envelope/source approval,
full digest equality and unique immutable original provenance. It carries data only.
An independent programmer/provisioner authenticates the owned descriptor origin and
rehashes the actual executable and complete accepted dependency closure before
constructing the computational Backend. A matching manifest profile scalar or a
caller-selected descriptor does not supply this ingress. Missing or mismatched
required5 ingress refuses; old1–4 and initial5 no-merge sentinel behavior remain literal.

The anchored helper computes the complete bounded merge and novel object result.
Its internal ComputationalMergeProof may bind profile/carrier/tree/object identities;
it grants no qualified, approved, accepted operating or publication flag. Keep the
selected original5 replay stdout grammar and 4096-byte limit unchanged. Offline and
prospective replay verify computational original facts without fabricating live
Environment/reviewer state. Source fixtures may use explicitly synthetic anchors
and programmer-owned native backends; they do not certify the anchor's claimed
operating platform or production closure.

Trusted transport separately observes the uniquely introduced original runtime
packet, exact subject/source approval and fixed source-policy runtime role through
the explicitly adopted typed custody observer. It combines that observation with
current independently verified realization into an in-process RuntimeAdmission.
No public constructor/deserializer from view JSON, approved:true, packet kind or
source approval alone grants this capability. Opaque Python state only marks a
trusted programmer boundary; it is not OS attestation or protection from hostile
code in the same interpreter. Candidate/retained computation remains credential-free.

Before proposing an accepted operating refresh result or effect, trusted transport
requires matching runtime admission, independently observed preparation and full
DOMAIN D1, then refreshes current source/job/owner/generation/head/stop guards.
Historical computational replay does not pretend to reauthorize current operation.
A serialized audit receipt remains data and must be independently observed at
operating admission. Public/default required5 CLI refuses without independent
computational ingress; runtime/view files convey location/provenance data and never
create operating approval. No production fixture/trusted=true bypass is added.

Proposed exact runtime-native coverage is five sorted scenario IDs:
attributes-lock-preservation, clean-required-merge, finite-refusal,
isolated-configuration, runtime-identity. A successful refusal harness may report
exit0 only when its raw records retain the expected command failures. These IDs and
runtime-role packet specialization still require explicit source adoption. Actual
Linux2.55.0 realization, complete closure, scenario execution, review/Environment,
original private custody and hard resource isolation remain separate operating gates.
The standalone raw computation library's observed scratch refusal is not a filesystem
quota qualification. No accepted operating event, API write or source5 pickup follows
from this clarification alone.


## Complete computational closure and host ingress, 2026-10-04

Amended 2026-10-04: root accepts the following computational source contract for AC1/AC2. It supersedes prior computational SOURCE-blocker wording about complete-closure serialization, consistency and host wiring. RuntimeAdmission and fixed-role/native scenario source adoption remain wholly later transport5; they are unavailable to this semantic outcome. Actual hashes, Linux realization, dependency completeness, independently immutable provisioning and hard resource/service isolation remain unqualified operating gates. Source pickup still requires actually delivered prerequisites and a fresh reviewed revision.

### Canonical inventory and digest

Runtime closure inventory exact object {format,kind,entries}; format integer1 (bool refused), kind exactly git-runtime-closure. Canonical bytes are ASCII UTF-8 JSON with recursively sorted keys, separators comma/colon without spaces, ensure_ascii=True, allow_nan=False, no BOM or final newline. Duplicate keys, noncanonical original bytes, unknown keys or trailing bytes refuse. SHA256 of these entire bytes is envelope.profile.closure-digest. The inventory does not contain its own digest, envelope/profile/config/approval/qualification or descriptor, avoiding a cycle.

entries is a list sorted strictly by ASCII path bytes, with unique exact paths. Root entry is exactly {type:"directory",path:"",mode:<mode>}; it is mandatory and first. Each nonroot directory entry exact {type:"directory",path:<path>,mode:<mode>}. Each regular file entry exact {type:"file",path:<path>,mode:<mode>,size:<integer>,sha256:<64lowerhex>}. File size includes zero, is not bool and equals original actual bytes; file hash is SHA256 of all bytes including an empty file. No size/hash keys on directories. No symlink/special/object-discovery entries.

Nonempty paths are portable ASCII relative POSIX paths: components match [A-Za-z0-9._+-]{1,255}, except exact '.'/'..' components forbidden; one slash between components, no leading/trailing slash, backslash, empty component, colon, whitespace, NUL or encoding aliases. Case is preserved and compared exactly; this source contract is for the proposed Linux realization and does not silently admit case-folding filesystems. Every parent directory through root must be explicitly present. Directory entries may be empty. No two directory/file entries share a path. Paths are lexical inventory identities relative to independently supplied closure-root, never URLs or operating paths selected by candidate data.

mode is canonical four-digit octal 0[0-7]{3}, equals actual POSIX permission bits, and excludes setuid/setgid/sticky or non-POSIX realization. Files require owner-read bit; directories require owner-read+owner-search. Other write/execute bits are identity data, not immutability proof. Independently selected executable must lie lexically below closure-root, have no symlink component, match exactly one file entry and have owner-execute bit. Its SHA256 equals profile.executable-sha256. Executable path remains host-local descriptor data; public profile binds bytes/closure, not arbitrary path authority.

Inventory must enumerate ALL root descendants and root itself. Exact full directory/file membership is checked without following links; unexpected files/directories, missing entries, type/mode/size/hash differences refuse. Hard-linked regular files are permitted only as independently immutable realized files; each path is independently inventoried and charged its full size. A provisioner must ensure outside aliases cannot mutate admitted content. No deduplication waives byte quotas. Inventory belongs outside closure-root; envelope/config/receipt/descriptor/source/carrier/ODB/scratch paths cannot be members or nested into that root. Declared dependency completeness means every executable/helper/loader/library/data dependency of the admitted Git commands is included; enumeration proves equality to this independent declaration, not automatic dependency discovery. Native provisioning must prove the declared set is complete and runtime cannot substitute an outside dependency. Do not run ldd, loader discovery or PATH-selected tools to grant that trust.

## Finite bounds and rationale

Accepted fixed structural bounds (not observed qualification): entries24576 including root; regular files16384; directories8192 including root; path1024 ASCII bytes; component255 bytes; depth64 nonempty components; individual file134217728 bytes (128MiB); aggregate summed file sizes1073741824 bytes (1GiB); canonical inventory8388608 bytes (8MiB). All limits are inclusive, independent and enforced before consuming/allocating beyond them. Counts include every hard-link path and empty directory. Maximum counts do not promise that maximum-length entries fit the inventory byte budget: the intersection must fit or refuse. No compressed/deduplicated representation expands these bounds.

Root reported hash-only observations of a downloaded Python archive with9338 members and Git/Nix material with63 store paths/2234 members. These observations are archive inventory data only: no installation, accepted complete-runtime membership, fit, native or operating qualification follows. Accepted24576 entries/16384 files/8192 directories provide finite headroom above those observed archive member counts, without adopting their topology or asserting category counts. 128MiB/file supports substantial native executables/shared libraries while refusing unbounded payloads; 1GiB aggregate bounds three complete rehash passes to3GiB of content reads. 8MiB inventory bounds parser memory independently of disk content and limits long-path accumulation. depth64/path1024 accommodate deeply nested immutable native material while bounding ancestor validation. These are conservative finite source choices, not assertions that an actual Git closure fits. The reported archive counts do not measure the actual admitted complete closure, expanded aggregate bytes, canonical inventory or120-second performance. Actual independently provisioned realization must measure counts/bytes/time and either fit or replan; unknown hashes and oversized profiles are never replaced by placeholders or relaxed automatically.

Use the already proposed profile proof-seconds120 as ONE monotonic end-to-end computational deadline covering host preverification, owned materialization, child preverification, isolated merge and child postverification. Host owns the start/deadline; child receives only remaining time through trusted invocation bookkeeping, never candidate/receipt/profile overrides. Reuse existing command-output-bytes1048576, finite subprocess termination and raw/carrier/scratch quotas independently. A slow hash walk or merge finitely refuses without computed proof; no resetting deadline between phases. A host parent enforces remaining timeout even if child fails to cooperate. This does not qualify hard filesystem quotas or actual runtime performance.

## Verifier algorithm and consistency

verify_realized_closure(inventory_bytes, anchor, descriptor, deadline) returns immutable DATA {inventory_sha256,executable_sha256,entries,files,directories,bytes}, only on exact equality. Validate original canonical inventory/bounds and anchored digest before traversal. Authenticate descriptor origin independently in host before any helper invocation. Inspect each directory/file via non-following descriptors rooted at supplied closure-root; reject symlink root/components and special files, enumerate complete membership, stream regular bytes under declared/aggregate limits, compare mode/size/hash. Do not use stat().st_size alone as read quota: refuse one-byte excess while streaming. Refuse observable identity/type/mode/size/membership changes during each scan. Stat/device/inode/mtime comparisons are only mutation diagnostics, never an immutability certificate. No snapshot claim follows from matching metadata.

Three exact passes are mandatory within the shared deadline:
1. PREHOST: trusted provider authenticates independent original anchor/provisioner input and verifies complete current realization before returning provisioned input.
2. PRECHILD: selected original9 helper rereads canonical inventory/profile and rehashes complete current realization immediately before any Git execution. It compares exact anchored hashes, membership and descriptor identity to host materialized data, not a host success boolean.
3. POSTCOMPUTE: helper rechecks the complete realization after the final Git command and before returning ANY consumable computed result. Any mismatch/error/deadline discards the computation and returns finite refusal; no event/effect/accepted proof is emitted. A failed postcheck cannot be recovered by rehashing and blessing the earlier result; recomputation under a new provisioned stable realization is required.

These checks detect observable changes, but cannot exclude change-and-restore or concurrent dependency substitution during execution. Independently immutable provisioned executable/dependencies throughout all three phases is an explicit prerequisite supplied by the trusted programmer/provisioner at the structural source boundary, never a serialized flag. It must have independently established that property; a JSON flag, permission mode, chmod, matching stat snapshots, inventory itself or opaque Python constructor cannot establish it. Fixtures may exercise diagnostics on mutable disposable roots, but must not report operating immutability. Runtime/profile/provisioner refresh during a computation refuses; it cannot replace original anchor authority.

## Host-owned computational API and materialization

Accepted host signature: global_preview(paths,assertion,head,scratch,*,computational_provider=None); replay_package(...,*,computational_provider=None). No provider discovery from paths/event/transcript, dynamic imports, callback deserialization or public --trusted override. Provider is a trusted programmer-owned callable selected by reviewed host source; its minimum API provision(ProfileAnchor,OriginalContext,Deadline) -> ProvisionedComputation. ProfileAnchor and OriginalContext are immutable DATA derived by the host from exact original profile/config/sourceapproval/introduction, not operating approval. ProvisionedComputation is host-local opaque programmer state carrying validated descriptor, canonical inventory bytes and realized identity data; it has no public JSON/deserializer and no operating qualification flag. Creating it manually outside trusted wiring does not prove native truth; the contract is a programmer boundary, not hostile-interpreter defense.

Descriptor remains exact {format,profile,executable,closure-root}: format1, profile full original envelope SHA, executable/closure-root independent absolute owned paths. Origin is established by provider implementation, never by a location or mode alone. Provider receives no credential/API/Environment/runtime reviewer object. It supplies canonical complete inventory bytes from independent provisioner material, compares their digest and realized closure to anchor, and cannot alter anchor/options/bounds to fit a candidate. A caller path/JSON with equal hashes cannot create this ingress. No actual production provider/closure/topology is selected in this amendment.

Host verifies unique original envelope/carrier provenance and writes fixed owned batch runtime files: profile.json (exact original full envelope), closure.json (canonical independent inventory), descriptor.json (exact4key location data), provenance.json (existing original5 durable/prospective/empty view). Files are exclusive regular owned scratch inputs with bounded content, no alias/symlink/discovery; root is outside runtime closure. Passing them to selected original5 child conveys computational DATA, never RuntimeAdmission. Profile hash comparisons and child complete rehash detect file tampering; ownership/mode do not grant approval. Exact original5 callable remains main.replay(directory,transcript,approved,before,prior,runtime,view), with seven positional arguments and no inventory-path argument. For required5, runtime is the absolute host-owned descriptor-file path <directory>/runtime/descriptor.json; view is exactly <directory>/runtime/provenance.json. These are location DATA, not provider authority. The helper derives the mandatory fixed sibling profile.json and closure.json from the validated runtime parent directory, never from a descriptor key. Both argument paths must match the independently materialized batch locations; refuse aliases, alternate directories, symlinks or mismatched view location. No optional probing/discovery is permitted. The original5 main/helper reads EXACT required regular files runtime/profile.json, runtime/closure.json, runtime/descriptor.json and runtime/provenance.json, applying original envelope/closure/descriptor/provenance grammars and bounds; extra entries in runtime directory refuse. Empty/initial5 retains runtime=None as the exact null no-merge sentinel and view=<directory>/runtime/provenance.json with the tagged empty view. Its host-created runtime directory contains provenance.json only; it never reads/materializes required profile/closure/descriptor or invokes provider/Git. Runtime directory filenames are host computational inputs only, not new event/context/source columns. Default required5 CLI runtime/view arguments alone never create a trusted provider; its host gate refuses before required computation unless programmer-provisioned ingress is present. Selected host REPLAY_DRIVER passes the fixed descriptor-file and view paths ONLY after the provider/materializer completed for required5 (and explicit runtime=None plus empty view for empty/initial5), and helper lookup of closure.json is mandatory fixed-path behavior, never a new descriptor key. The existing provenance wire grammar is not expanded: profile introduction/sourceapproval are host-verified from actual history before materialization, and profile/config equality remains explicit in child.

The trusted host dispatch may serialize these data to its isolated verified child; it does not serialize provider authority or claim that an arbitrary direct helper invocation authenticates ingress. Direct library Backend use is programmer-owned unqualified computation. Public/default host required5 CLI fails without this independently injected provider; runtime/view file arguments alone never instantiate it. No serialized accepted/qualified boolean and no new event/context/result column. stdout4096 and summary512 grammars remain unchanged. Old1–4 dispatch/signatures remain literal; empty/initial5 null no-merge skips provider/Git and carries an unqualified profile reference only.

RuntimeAdmission construction, typed runtime packet observer, five native scenario review, domain/producer custody and accepted operating event/effect proposal are wholly future transport5. Semantic5/helper/host computational preview cannot construct/deserialise/admit that capability or publish an operating proof. Actual Linux2.55.0 full closure/native behavior/independent immutability/isolation remain operating qualification, even when synthetic source fixtures pass.

## Finite acceptance fixture obligations

Positive canonical complete root with nested+empty directories, regular/executable files and zero-byte content; exact digest/modes and independent host provider yields unqualified computational result. Negative extra/missing directory/file, symlink root/component/leaf, special file, duplicate/dot/escape/encoding/path/type/mode/size/hash errors and inventory canonical mismatch refuse. Boundary/count/path/depth/file/aggregate/inventory at-limit versus one-over refuses finitely before excess reads/allocations.

Provider absent/JSON/location/mode/approved=true cannot authorize host required5 dispatch; trusted fixture provider succeeds with explicitly synthetic anchor. Tampering original envelope/config/inventory/descriptor/provenance and mismatching original sourceapproval refuse. Prehost/prechild/postcompute mutation and unexpected added directory fixtures refuse without result; no source fixture labels pre/post stat equality as immutable qualification. Shared deadline exhaustion in each phase and noncooperative child termination refuse. Literal1–4 and initial5 no-provider positive, required5 no fallback, original9 closure selection and existing4096/512 replay bounds remain proven. These fixtures do not claim Linux/native production qualification or actual operating custody.

Root-review refinement, 2026-10-04: revised finite inventory limits above and fixed runtime-directory/descriptor-file/view interface are proposed adoption choices; computational source fixtures explicitly use synthetic anchors and programmer-supplied immutability premises. Such fixtures verify source equality/refusal and do not certify actual Linux closure immutability, complete dependency isolation or production qualification.

The fixed runtime directory is ephemeral host input outside the immutable selected nine source members. Its four required files (or initial no-merge provenance-only case) are checked separately and never added to the original source manifest or inherited by old packages. Computational source fixtures use synthetic provisioner premises and do not certify actual immutable runtime deployment.
