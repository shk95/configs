# Bounded raw refresh merge computation library
kind: spec
date: 2026-10-04
scope: repository
issue: #508
status: approved
review-by: 2026-10-18

## Assignment and outcome

Root owns review and continuation under #479. This planning preparation is pinned
to dev 7bb23181a179f13a78bb9874af4466a1443ec142. The library is a separately
reviewable source-only outcome at tool/version-control/release-merge-proof.py,
with dedicated standalone fixture source/harness. It computes from literal original
public Git object data; it performs no acquisition or public/private effect.
No source pickup is assigned until root reviews this concrete plan.

Implement independently of unmerged #504/#505: do not import their source. Current
semantic package closure remains eight files and neither imports nor executes this
library. A future original5 package copies/adopts explicit source and manifest membership;
that adoption, loader/config9/runtime qualification and transport/operating authority
remain separate gated work under refresh-merge-proof/spec.md. This library cannot
complete that parent's pending acceptance merely by computing a tree.

## Exact data and backend interface

verify_merge(manifest_bytes, chunks, trusted_backend) returns bounded computational
data only: roots, independently computed merge-base, result tree SHA, full result
path/mode/OID inventory and complete novel tree/blob objects in dependency order.
No approved/qualified/operating flag, source custody claim, commit/declaration,
public-object receipt, preparation consumption or future completion timestamp.
trusted_backend is programmer/provisioner-owned fixed runtime capability, never
selected by a carrier path/name/version/environment or imported data. Manifest
runtime-profile digest may only match an already supplied backend identity.
Fixture backends instantiate measured native capabilities for tests; their identity
is not admission of a production executable/helper/library closure.

The data grammar is identical to the proposed #507 raw-carrier appendix at
5d423fa3b3e9afcef3fc11dfbccf2e0ec39d5b06; this standalone plan does not adopt
original5 or its profile admission. Manifest exact keys
{format,kind,roots,runtime-profile,objects,chunks,raw-bytes}; format integer1,
kind required-refresh-merge; roots exact previous/base/merge-base40hex;
runtime-profile64hex matching the programmer-supplied backend identity. Canonical
UTF8 JSON sort_keys/no-whitespace/ensure_ascii=False; reject duplicate keys,
nonfinite values and bool integers. Object rows OID-sorted and unique by OID,
exact {oid,type,size,chunk,offset}; type commit/tree/blob, strict nonnegative
size/offset, chunk integer1..N. Chunk rows ordered1..N exact
{number,size,sha256,git-blob}; names chunks/%06d.bin, manifest.json and all carrier
paths regular100644. No caller paths or extra entries. Outer manifest digest/Git
blob identities are computed, never embedded selfdigest/path/introduction commit.

Each frame is ASCII `type SP canonical-decimal-size SP full40hex-oid LF`, followed
immediately by exactly size literal raw bytes. Offset points to FRAME HEADER start;
descriptor size counts only payload. Frames wholly fit one chunk and concatenate
exactly from offset0 through chunk size without gaps/overlap/padding/trailing bytes.
Verify header type/size/OID against descriptor and SHA1(ASCII(type + space +
canonical size) + NUL + literal raw) against OID. Verify literal chunk SHA256 and
Git blob identities; raw-bytes is the sum of payload sizes. Canonical packing
traverses OID-sorted frames, appending when total frame fits <=1MiB, otherwise
starts the next chunk. Arbitrary rechunking refuses. Actual raw maximum is
min(type limit,1MiB-header-length); a nominal1MiB blob that cannot fit its frame
refuses without splitting or widening. This library grants no retained custody.

## Complete original graph and snapshots

Parse complete commit DAG from previous/base through every original zero-parent
root, with strict original header framing and ordered full parent identities.
Preserve well-formed signed multiline headers as raw bytes; do not certify signatures.
Reject missing parents, cycles, unrelated/unused objects, incomplete/cutoff graphs,
ambiguous headers or unknown formats. Compute all best common ancestors independently;
exactly one must equal declared merge-base. Zero/multiple bases refuse.

Supply complete recursive tree/blob snapshots for previous/base/unique base only.
Historical commits outside these snapshots need no historical tree/blob contents.
Trees use canonical Git sorting, raw directory 40000 and regular 100644/100755 leaves.
Reject gitlinks/symlinks, duplicates, unsafe names/paths/modes and missing closures.
Materialize no checkout; original leaves are data only. Every supplied tree/blob must
belong to selected snapshots. Reject unsupported encoding and incomplete empty trees.

## Isolated native computation

Create a fresh owned bare SHA1 ODB from independently verified literal objects via
bounded fixed Git hash-object writes. No caller packs/deltas, checkout/index, network/
fetch/remotes, lazy objects, alternates, grafts/replacements, templates/hooks, proxies,
credentials or inherited config/import path. Use explicit fresh HOME/TMP and
allowlisted environment, fixed executable/helper capability and process-group bounds.
Run merge-base --all as independent cross-check, then modern merge-tree --write-tree
--no-messages --merge-base=<unique-base> previous base. Require exit 0 and exactly
one full result-tree line. Conflict/abort/nonzero/extra output/timeouts refuse.

Admit only identical original .gitattributes path/mode/blob inventories across the
three snapshots. Parse bounded built-in text/-text/text=auto/eol=lf/eol=crlf/binary;
reject user macros/custom merge/filter/diff drivers/encoding/unsupported declarations.
Set GIT_ATTR_SOURCE to verified previous commit and merge.renormalize=false; disable
info/global/system attributes. Attribute evolution or unavailable backend behavior
refuses; do not disable original attributes and claim ordinary merge equivalence.
Proposed native test profiles are Linux/macOS Git 2.55.0 and Windows 2.55.0.windows.5.
Exact version availability alone is insufficient; backend identity/behavior fixtures
and production runtime provisioning are separate evidence.

Enumerate full computed result closure and independently hash every novel tree/blob.
Report literal novel objects absent from supplied original object set in topological
order; original object absence is not public absence. No generated commit M/H here.
Enumerate the whole novel closure first; reject a complete result exceeding eight
objects/512 KiB; never discard novel objects to fit. Future M/H share this bound.

## Finite bounds

4096 commits, 32 parents/commit, 64 KiB/commit,depth 4096,4096 trees, 4096 input blobs,
1 MiB/blob, 16 MiB original raw, 256 KiB manifest, 24 chunks<=1 MiB,24MiB carrier,
256 MiB owned scratch, 120 seconds entire proof and 1 MiB command output. The complete computed novel closure must fit the parent initial publisher bound
of eight generated objects and 512 KiB combined raw bytes; excess finitely refuses
without trimming. The later adopter counts any generated M/H commits against this
same bound and may therefore refuse a library result that leaves insufficient room. Backend
must terminate whole owned process group and clean owned temporary state on refusal;
no host/global cleanup. Boundary excess refuses, no truncation. Aggregate original5
history/materialization quotas remain future adoption gates, not implicit widening.

## Delivery and verification

One repository-only source PR after reviewed plan; dedicated linked worktree pinned
fresh dev and reviewed plan independently. Proposed fixture files are tool/version-control/test-release-merge-proof and its
Python harness. Wire the shell entry into tool/version-control/test beside the
release suites and the Windows repository test list in .github/workflows/ci.yml;
update the existing classifier/affected-path fixtures for these repository-owned
paths. Root coordinates those shared-file edits in the eventual source assignment.
Do not modify either release-control-package/manifest.tsv or release-transport.manifest.tsv.
Use the existing INV repository/fixture-git-isolation boundary for disposable Git
fixtures and name it in positive/negative isolation fixtures. Computational acceptance
fixtures answer this work spec; no new durable invariant is proposed by this plan.
Any later durable rule must separately satisfy the existing invariant format and
positive/negative enforcement convention. No new operator command is required. Report all evidence separately:
local computational fixtures, exact-head native Linux/Windows affected CI, policy/
review, and unperformed actual runtime qualification/acquisition/transport/operation.

Fixtures must use real disposable Git: clean divergent merge, content merge/rename/
mode/emptytree preservation, binary conflicts with explicit attrs, text/eol profile,
multiple/unrelated/missing/cyclic DAG, signed raw headers, hash/frame corruption,
unsupported attrs/modes/symlink/gitlink, complete novel closure, every bound/excess,
fixed-backend spoofing and ambient config/hook/driver/credential/network canaries.
No current semantic package/loader receives imports or membership as a test shortcut.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Strict bounded raw carrier and complete original DAG/three-snapshot verification independently find exactly one best base and refuse malformed, incomplete or unsupported data. | fixtures, policy checks, review |
| AC2 | Programmer-owned isolated native backend computes exact supported Git merge tree and complete novel object closure, with admitted original attributes and bounded failures. | fixtures, affected dispatch, review |
| AC3 | Standalone source/fixtures and normal exact-head Linux/Windows delivery preserve current semantic closure and report computational proof separately from original5/runtime/transport/operating admission. | fixtures, policy checks, affected dispatch, review |

## Stop and replan

Replan for schema/bounds/scope changes, native unsupported behavior, new executing
closure, original5 import/adoption request or competing shared ownership. No remote
acquisition, credential provision, workflow dispatch/enablement, private packet,
API publication, initializer, promotion, release, host activation/Apply or cleanup.

## Dated review repair, 2026-10-04

This proposed standalone revision follows #507 head
5d423fa3b3e9afcef3fc11dfbccf2e0ec39d5b06 exact raw frames and limits. It does not
adopt unmerged source or original5 admission. Root approval remains pending.
No independent larger generated-object limit is proposed; bounded complete output
refuses rather than silently extending the parent's initial publication subset.

## Approval and pickup, 2026-10-04

Root approved this source-only plan after the editorial closure-bound repair. Pickup
owner: status_plan. Execution base: 7bb23181a179f13a78bb9874af4466a1443ec142
(fresh origin/dev). Reviewed plan is approved and provisionally uncommitted; its
revision will be published together with source, before any worker handoff.

## Dated implementation prerequisite amendment, 2026-10-04

Root approved INV repository/raw-merge-computation-read-only with fixture enforcement
at tool/version-control/test-release-merge-proof. Its rationale is AGENTS.md Rules
that are expensive to break; it binds bounded raw verification and read-only
computation, without native qualification or original5 adoption. Computational
positive/negative fixtures name this invariant; suite isolation cases separately
name INV repository/fixture-git-isolation. This supersedes the earlier no-new-invariant
planning statement. Execution issue: #508. Owner: status_plan.

## Dated traversal and bounded-execution amendment, 2026-10-04

Root approved standalone expanded traversal limits: depth256, UTF8 path bytes4096,
8192 expanded entries per original snapshot and computed result. Count rows before
enqueueing/materialization; shared subtrees can expand far beyond unique-object
quotas. No original carrier grammar change; future original5 adoption explicitly
admits this subset or refuses wider data. Never truncate or normalize paths.

Exact unsafe-name refusal: empty names, . or .., case-insensitive .git, slash or
backslash, Unicode control codepoints below32 or127, any :*?"<>| character, trailing
space/dot, and case-insensitive Windows device stem con/prn/aux/nul/com1–9/lpt1–9
including extensions. Names must decode as UTF8. Tree modes remain literal40000/
100644/100755. No checkout or OS path normalization is performed. JSON structure
depth8 is a parser guard; the exact admitted manifest schema is shallower.

Native execution monitors scratch size before, during and after each subprocess.
This is an observational refusal cap, not a hard filesystem quota or qualified
production resource-isolation claim. Pre-materialization reservation is original
raw bytes +32 times expanded three-snapshot raw bytes +8192*4096 per-object overhead;
it deliberately refuses oversized duplicate-path inputs before writes. This
conservative reservation is an admitted computation subset and does not certify
a worst-case arbitrary executable. Native backend remains provisioner-owned.

On unsuccessful group termination or unverified group absence, refuse and retain
owned scratch with a structured recovery path; never claim parent-only termination
as successful cleanup. Unix verifies group absence after reaping; Windows requires
a successful bounded taskkill /T /F receipt. Live-child canaries run in both fixture
profiles. Mandatory author/committer headers admit nonempty identity/email, canonical
nonnegative timestamp of at most12 digits and explicit numeric timezone; unsupported
header formats refuse while signed multiline raw bytes remain unmodified.

## Dated expanded-input reservation correction, 2026-10-04

Remove the earlier32x scratch reservation: it had no native allocation proof and
would refuse the measured actual graph. Enforce expanded-input work<=16MiB before
materialization instead: sum literal tree/blob payload bytes at every full path
occurrence in all three snapshots, including roots/repeated subtrees. This is in
addition to original16MiB raw-object and expanded-entry limits. Concurrent256MiB
scratch observation remains an explicit refusal monitor, not a hard filesystem
quota. Independent hard resource isolation is future runtime qualification/adoption
work, not this computational provider's proven authority. No carrier grammar or
original5 admission change.
