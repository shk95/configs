# Typed receipt and content-addressed review custody contract
kind: study
date: 2026-10-04
scope: repository
status: open

## Adoptable source design, not operating acceptance

Root and independent reviewers resolved the transport representation against the
original protocol-3 evidence/transcript reader and original operating Git loader.
Use transport-only validation and projection; no new semantic custody field or
historical reinterpretation. Durable source adoption must add the typed custody
decision/invariant, review-only role, fixed public read contracts and exact transport
closure with positive/negative fixtures. Source implementation follows a child
spec; operator provisioning and genuine records remain separate.

All JSON is strict UTF-8 canonical bytes: sorted keys, compact separators,
ensure_ascii=False; reject duplicate/unknown keys and nonfinite values. Packet is
at most 4 MiB, index 256 KiB, arrays 64 entries; positive integer IDs reject bool.
Identities are full lowercase SHA1/SHA256. No caller input selects a URL, owner,
workflow, Environment or template repository.

## Independently trusted review authority

The trusted deployment contract is separate from packet assertions. Exact keys are
format, source, public-repository-id, review-workflow-id, review-workflow-path,
review-workflow-blob, review-job, review-environment-id, review-environment, reviewer.
Format is 1; source/blob are original SHA1; numeric IDs are actual positive IDs.
Fix public provider shk95/configs, reviewer 101378576, workflow path
.github/workflows/release-production-review.yml, job review-production-receipt and
Environment release-production-review. Actual deployment IDs are independently
observed and reviewed setup inputs; packet authors cannot choose them. Future
owners or review scopes reopen this single-maintainer contract.

The manual-only review workflow accepts only a packet digest. Its initial source
job gate is statically disabled; a separately reviewed accepted-source change
is required before actual invocation can proceed. Dispatch inputs cannot enable
the gate. Its fixed run-name is review:<digest>.
It has one Environment job, empty permissions, no checkout, secret, private
locator, packet contents, artifact or operating write. Platform-created deployment
metadata is explicit. The job validates digest grammar; source never approves it.

Validate original accepted review source/workflow blob, actual repository/workflow,
manual master ref/event, actor, latest attempt=1 and sole successful job. Observe
complete approvals: exactly one unambiguous approved record from the authorized
numeric reviewer for the exact Environment with comment review:<packet-sha256>.
Fixed title must also match, but title or unobserved dispatch input is not authority.
Reject mixed/rejected/duplicate histories, rerun, deletion, unavailable metadata
and source/packet movement. Repeat observations before proposal/publication.
Claim no approval timestamp or attempt/job field absent from the approval API.
Actual initial hold ordering and reviewer policy are operator evidence. The receipt
attests authorized human approval of assertions, not GitHub-certified native truth.

## Packet grammar

Read review/packets/<sha256>.json as a 100644 original regular Git blob from the
independently acquired complete operating bare Git. Verify original blob identity,
canonical bytes, bounds and SHA256. Exact top-level keys are format, scope,
authority, claims, raw-records and template-pair. Format is 1.

Scope exact keys: dev/master/tree/control SHA1; manifest/rules/baselines-digest and
requirements-digest SHA256; baselines canonical base64 of original baseline TSV;
selected sorted unique check IDs. Match the actual original qualifier diagnostic,
package, baseline and trusted Actions requirements. Authority exact keys are
source, workflow-blob, workflow-path, job, environment, public-repository-id,
workflow-id, environment-id and reviewer, all equal to independent trusted scope.
Do not include post-dispatch run IDs, a packet's own digest or active references
inside its hashed bytes: that would create a hash/run self-reference.

Claims are sorted by id and exactly cover selected non-Actions requirements.
The independently reviewed producer contract fixes each selected ID as Actions
or review/native/template; packet authors cannot change that classification.
Every raw-record reference resolves exactly once; unused raw records refuse.
Exact claim keys: id, kind, domain, lane, tool, source, records and statement.
Kind is review/native/template; domain repository/unixlike/windows; source is dev;
lane and tool equal original diagnostic values including source-blob suffixes.
Records are sorted unique raw-record IDs; statement is at most 8192 UTF-8 bytes.
Classify producer type from the independently reviewed requirement contract, not
job naming. Existing Actions receipts retain their original strict requirement
schema and independently observed execution metadata.
Actions metadata and workflow/tool blob identities do not independently report
actual interpreter/Git/runtime versions. Current CI selects Python 3.13 and only
asserts a minimum functional version; it is not automatically the exact production
tool descriptor. An Actions producer must have an explicitly reviewed source
contract establishing the required tool/profile, or those facts require approved
raw execution records. Never upgrade a matching job name to exact runtime proof.

Raw-record exact keys: id, kind, source, platform, tool, command, lane, result,
content and sha256. IDs match [a-z0-9][a-z0-9-]* with length at most 128. Kind is
review/native, source is dev, tool/lane match claim, result is verified. Content
is canonical base64 with exact SHA256, at most 512 KiB decoded per record and
3 MiB total. Native command is 1..64 strings, each at most 4096 UTF-8 bytes without
NUL; review command is empty and platform null. Native platforms are x86_64-linux,
aarch64-linux, aarch64-darwin, windows-x64, windows-ltsc-19044-x64 and
windows-inbox-powershell-5.1-x64. Required Darwin/LTSC/bootstrap profiles must match
their actual requirement; generic Windows CI cannot stand for an LTSC record.
Bytes/source/tool/coverage are checked automatically. Genuine execution, actual
command use and semantic result are the authorized reviewer's assertions.

Template-pair is null unless its requirement is selected. Otherwise exact keys
are repository, provider, revision, tree, delivery-ref, observed-ref-head, delivery,
pair and record. Fix repository shk95/configs-host-template and main ref; provider
equals dev, revision/tree/head are original SHA1, delivery=delivered, pair=verified
and record references approved original pair evidence. Independently verify the
actual public main ref and complete original bare template graph/tree/ancestry.
This needs an explicit anonymous fixed-repository GET/Git data contract; it does
not expand the writer's private credential boundary. Identity/ancestry do not
prove compatibility: authorized owner review binds the actual tested pair.

Context Bridge/live source inspection observed main at
2cbf41be904448354f413e6156e8e83c0e4c445a, repository ID 1385102654. The root
flake/lock currently pin provider c76752dc1ec285dce721ae02a2f139c9f32dcb76;
tool/check-hosts supports CONFIGS_PROVIDER_OVERRIDE for an exact candidate pair.
Do not require the template's current provider pin to equal candidate dev when
actual approved pair evidence uses that override. These observed revisions are
not frozen future delivery inputs or new build/runtime evidence.

## Index, projection and restart

review/production-index.json exact keys: format=1, scope-digest and entries.
Scope-digest is SHA256 of canonical packet scope bytes; the index is at most
256 KiB. Each entry packet is lowercase SHA256, and IDs match selected check IDs.
Entry exact keys are id, packet, run, attempt, job. Attempt is 1; all numeric IDs
are positive. Entries sorted by check ID cover every non-Actions selected ID once.
First implementation uses one packet/one review run/job for the exact candidate
scope. The index is a lookup hint, not approval. Journal never writes review paths.
Actual operator maintenance must serialize packet/index publication, preserve
original initializer completion/history and retain immutable content-addressed
packets. No automatic packet publisher is authorized.

Project validated review claims into original eleven-field rows:
id/dev/master/tree/rules/manifest/verified/review-run/1/review-job/expected-tool.
Review run/job identify custody of the assertion, not native execution. Merge
with real Actions receipts for exact selected coverage. Use original nine-field
offline evidence TSV and seven-field template-pair rows; original transcript keys
remain source/checks/owner/observations/protection plus optional refresh.

Historical recovery starts from original row run/attempt/job, independently
observes its original review source and approved comment digest, then reads that
same content-addressed packet and checks original candidate/baseline/tool scope.
It never uses a new active index to reinterpret old evidence. New candidate packets
follow original generation advancement and evidence/approval invalidation after
unresolved-effect reconciliation. Missing/deleted/rerun/revoked receipts refuse
new effects without rewriting old semantic history.

## Source adoption and verification

Add a dedicated typed-production-receipt-custody decision/invariant and explicit
authenticated transport amendment for the new read role. Add review-only workflow,
bounded anonymous review/template readers, original private packet/index reader,
typed collector and exact current transport inventory/dispatch. Preserve original
five/six-file inventories and semantic packages. Stop for unrepresentable historical
bindings; custody authority becoming a reducer event would require a new protocol.

Fixtures cover strict schema/bounds, wrong scope/hash/comment/actor/Environment,
mixed review history, original source drift, rerun/deletion, false profile/tool,
missing/duplicate/foreign coverage, template ref/graph/pair mismatch, no private
credential forwarding or approval writes, proposal/publication movement, immutable
packet retention, replacement invalidation and old-row restart through approved
hash independently of active index. Source fixtures supply no real native proof.

Actual gates remain accepted master review/writer source, numeric provisioning,
genuine raw native/template/review records, operator packet publication/retention,
human approval, first Environment hold, semantic baseline adoption and declaration
judgement. Source neither creates them nor substitutes initializer certificates.
