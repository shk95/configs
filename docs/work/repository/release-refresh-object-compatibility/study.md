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
