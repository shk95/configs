# Separate trusted transport from retained semantics
date: 2026-10-01
scope: repository
status: accepted
reopen-when: A new endpoint, semantic protocol, transport closure or executing credential boundary is required.

## Decision

Keep release-control preview and its historical eight-file semantic packages inert.
A separate trusted transport inventory contains the finite API client, retained
bridge, fixed loader and disabled operator preflight. Pin that complete inventory
at the approved master entry. A credential-free child executes only the exact
manifest-verified retained package. Current transport glue never supplies a newer
reducer, serializer, classifier or qualification engine to an old batch.

The trusted deployment wrapper owns runtime event inputs and the reviewed operating
bootstrap; candidate/request bodies cannot provide them. Independently fetch run,
attempt, actor, workflow, job, source/ref and protection. Required evidence additionally
binds successful check/run/job identity and reviewed exact workflow/tool blobs.
Mutable prose, candidate artifacts and an asserted version string are insufficient.
No provisioned wrapper or selected operating connection is claimed by source proof.

Transport uses one fixed TLS API host, no redirects/proxies, a 30-second request
bound, bounded response sizes and complete bounded pagination. Unknown pages or
responses refuse. An external write follows durable intent and a fresh stop reread.
A lost response is reconciled by target observation; it is never an automatic retry.
Private records use exact current head, one-parent child commits and non-force ref
updates, followed by actual observed-head reconciliation. This is not atomic API CAS.

Promotion requires fresh exact head/base/protection/evidence; actual post-merge parents
and tree gate immutable tag objects/refs. Unexpected merges stop publication without
automatic undo. Complete PR lookup includes closed/merged history; absence cannot be
inferred from a count or one open page. A duplicate successful operation joins once.

GitHub cancellation is run-wide and has no expected-attempt guard. Refuse cancellation
unless a fresh complete job inventory contains precisely the recorded owner job.
Recheck latest attempt before and after the call; 202 is not termination. Mixed-job
runs, changed attempts, timeout-only takeover and unknown termination refuse. Future
manual provisioning must isolate the writer into its own run and serialize rerun
mutations. Separate inspector/wait executions receive no writer credential authority.

Authenticated stop/resume retains original history and old-package obligations;
resume clears stale validation/approval rather than reviving it. Actions failure is
an authenticated notification-source receipt, not proof of user inbox delivery.
Wake acknowledgement never grants ownership or exact-candidate approval.

The public operator interface is read-only preflight only. Workflows remain disabled,
with no connection, secret, Environment, dispatch, schedule or executing write mode.
Source fixtures use only disposable Git and fake endpoints. Actual bootstrap,
connection, permissions/protection, master source promotion, manual authorization
and manual/scheduled receipts remain separate unresolved operating gates.

## Sources and scope

The source work and criterion proof are in
`docs/work/repository/release-operating-transport/`. API limitations were reviewed
against the official GitHub REST documentation for workflow runs, Git refs, Git
objects, check runs and pull-request merge. This decision reconsiders only the future
transport boundary of release-controller-preview-boundary.md; it preserves that
preview contract and authorizes no actual operating effect or host change.

## Read-only credential qualification

Amended 2026-10-02: allow a separate master-only, maintainer-only, single-job
credential qualification workflow to receive the dedicated Environment token and
selected private locator/identity. This is a provisioning probe, not the routine
credential-free inspector/wait execution or a writer. It checks actual run/attempt,
actor, source, workflow/job, private repository and protection using bounded GET
requests. It refuses changed attempts/source, mixed jobs and unexpected access to
secret metadata. Its fixed HTTPS host cannot redirect and has no write primitive.

Check-run accessibility on the public provider is tested without authentication;
no selectable Checks grant is needed for that observation. Successful qualification
proves read accessibility and the observed denial only, not write permissions,
Environment isolation, bootstrap adoption, domain evidence or live enablement.
The public preflight and existing source writer workflows remain inert. Deployment
of the probe still requires normal accepted master source, and actual observations
remain separate from source fixture proof. Source stays pinned to the running SHA;
candidate scripts/artifacts/caches never execute with its token.

## Credential-free public inspection

Amended 2026-10-02: allow a separate master-only single-job public inspector/wait
workflow without an operating Environment, credential, private connection or writer
concurrency. It observes only approved public writer/qualification workflow runs,
exact latest attempts, actual actors/ref/source and complete sole-job metadata.
The source must be in the accepted public master's full original Git history.
The finite wait never cancels, wakes, claims or approves; completion and timeout
remain observations, not retained-owner authority
(`INV repository/release-inspection-without-authority`).

Its network transport is bounded anonymous GET to the public provider only, without
logs/artifacts/cache reads or candidate execution. Old/moving attempts, source,
workflow/job identity, unknown pages and mixed jobs refuse. Trusted writer takeover
must independently reconcile actual authenticated terminal evidence and old-package
history. This change does not enable the writer or adopt operating bootstrap.

## Original private Git acquisition

Amended 2026-10-02: a trusted acquisition helper may pass the dedicated operating
credential only to a fixed GitHub HTTPS Git process and its approved askpass code.
It authenticates the approved entry and selected private repository before fetch,
owns a fresh bare repository and disposable configuration, bounds time/output/disk,
and refuses moving, shallow, alternate, grafted, replaced or incomplete objects.
No checkout, hook, submodule, proxy, redirect, ambient credential/configuration or
candidate program is allowed. It stores no credential in arguments, files or Git
configuration and returns only verified original private objects to the retained
loader. Retained subprocesses continue to receive the credential-free environment.

The current transport inventory explicitly adds
`tool/version-control/release-operating-history.py` as its sixth file. Historical
five-file transport inspection and eight-file semantic packages remain exact;
this acquisition does not substitute a current reducer or rewrite old objects.
A disabled initial-record proposal uses the verified original package's empty
projection, remains source-bound and selects no domain semantic baseline. Actual
seed/ref publication, provisioning workflow, reviewed private proposal and complete
manual/scheduled operating evidence remain separate unfinished deliveries.
