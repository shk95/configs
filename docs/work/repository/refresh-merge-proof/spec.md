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
