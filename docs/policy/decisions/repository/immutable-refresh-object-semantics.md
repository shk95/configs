# Immutable refresh object semantics
date: 2026-10-04
scope: repository
status: accepted
reopen-when: Required-base merge construction, wider raw-object bounds or new publication authority is proposed.

## Decision

Protocol 4 names each bounded immutable public refresh blob/tree/commit as a
separate original effect. A construction binds complete literal original base
commit/path trees/before-lock, exactly the lock-only generated closure, preparation
identity and deterministic object dependencies. Its digest excludes itself and
operation IDs; IDs are derived afterwards in publication order. Intent must match
the next exact original construction object and observed prerequisites before
any branch or PR effect. Uncertain/conflicting effects fence later intent.

Initial support requires previous='-' and parent=base. Existing original protocol
1/2/3 packages, transcripts, IDs and required-base update behavior are unchanged.
Required-base protocol-4 update needs independently verified complete original Git
merge provenance; supplied trees/parent labels are not computed merge proof.

Signed original base headers are hashed literally and parsed for an unambiguous
graph. Newly generated commits have only canonical unsigned tree/parent/author/
committer headers, fixed Release controller identity, UTC epoch and a fixed subject
with seven ordered release declarations. Structural validity is not domain review,
actual producer completion or semantic release certification. Later authenticated
transport must independently verify declaration/producer custody and exact public
object bytes. Returned API acknowledgement never substitutes for independent read.

Original protocol-4 replay reports preparation digests only from accepted events.
The global loader checks those original outputs across completed/outstanding batches
and refuses one preparation consumed by different batches. Same-batch joins are
allowed; unused transcript revisions and original protocols 1/2/3 are not silently
reinterpreted. Preparation metadata stays asserted offline until actual observation.

Construction is bounded to 1 MiB canonical data, eight originals and eight generated
objects, 512 KiB combined decoded bytes and 256 KiB per object. Direct entries and
dependencies are bounded to 4096, names to 255 bytes, message to 16 KiB. Initial
lock path has only root/unixlike trees. Replay permits at most 16 distinct accepted
preparations and refuses serialized output beyond the existing 4096-byte limit;
global loader refuses malformed or unbound original output. Larger data returns to
review; historical bytes are never trimmed to fit.

Observation-only recovery can reconcile exact old-owner intent before takeover,
using terminal-owner proof and the existing old generation. It cannot implicitly
retry POST. Refusal source fixtures and original package replay are separate from
actual API publication, permissions, writer deployment and operating receipts.
