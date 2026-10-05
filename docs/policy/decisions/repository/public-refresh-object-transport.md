# Public immutable object transport and local delivery
date: 2026-10-05
status: accepted
scope: repository
reopen-when: A different public origin, credential class, object schema or retry authority is needed.

## Decision

Amended 2026-10-05 for the reviewed public-refresh-object-transport work. Current
initialization and new batches adopt actual original protocol 4 records, approval,
contexts and replay. Existing protocol 1/2/3 packages and histories remain exact.
Current transport membership adds release-public-objects.py as the eleventh file;
original five/six/seven/eight/ten-file inventories remain literal inspection inputs.
This adopts INV repository/public-refresh-object-transport.

The selected manifest-verified original adapter supplies the exact blob, direct
complete tree and unsigned deterministic commit POST bodies. Fixed public object
POSTs use the existing Contents write class; no new credential class, repository,
ref, tag, scheduler or operating enablement is introduced. Generated dependencies
must already be observed; original dependencies need bounded raw custody and
independent public availability. Unsupported custody finitely refuses.

Independent anonymous GETs target only shk95/configs Git objects on api.github.com,
without redirects, proxies, credentials or writer fallback. Direct tree GET omits
recursive entirely. Complete typed comparison binds blob bytes, directory-aware
mode/name/type/identity/order and commit tree/ordered parents/message/actor/date.
Signed original commit bytes are retained and structurally compared, without a
signature authenticity claim. Generated commits remain canonical and unsigned.
A 404 establishes absence only between matching public numeric repository identity
and same-type known-original proofs; incomplete, conflicting or failed proof fences.
The reader bounds requests, response bytes and elapsed time and never retries.

Before private API effects, a prospective child is replayed in an owned isolated
object database and its bounded exact new raw objects are retained. Private tree,
commit and observed ref must match that child. The owned LOCAL original database
then imports only those hash-verified raw objects and completes graph/history/global
replay before logical acceptance or clearing pending state. API acknowledgement
alone is insufficient. Failed local delivery retains pending and the original logical
head even when REMOTE advanced. Recovery requires fresh retained history and
reconciliation; this amendment grants no rollback, duplicate write or retry authority.

This is disabled source capability. Actual API, permissions, bootstrap, native
operation, release and host deployment remain independent gates. The work report
records source and fixture proof without certifying those operating gates.

## Source

Reviewed work: docs/work/repository/public-refresh-object-transport/spec.md.
