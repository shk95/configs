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
