# Manual connection and credential preparation
kind: study
date: 2026-10-02
scope: repository
status: open

At dev 1a0e39c1a36b915c0dc162506603ef37ce726ec2 the finite transport is delivered,
but the workflow remains disabled and there is no start/claim/planning wrapper.
The maintainer subsequently selected a separate private operating repository and
direct user issuance/storage of the fine-grained PAT. Keep actual connection
identity in the private setup inventory and the protected Environment.

## Concrete setup inventory

| Item | Selection or remaining obligation |
| --- | --- |
| Resource owner | Same owner as the public provider and selected operating repository. |
| Selected token repositories | Public provider and selected private operating repository only initially; template access waits for an implemented, reviewed adaptation operation. Never private hosts. |
| Environment | release-control in the public provider; selected deployment policy allows branch master only, no tags. |
| Token secret | CONFIGS_RELEASE_TOKEN, stored directly by the user in that Environment, never a repository-wide secret. |
| Private locator secret | CONFIGS_RELEASE_OPERATING_REPOSITORY; setup writes the selected locator without exposing the token. |
| Operating ref | operations; not initialized until reviewed source/control/bootstrap and original record grammar are bound. |
| Actor allowlist | Authenticated maintainer numeric identity initially; runtime and triggering actor must match. |
| Token expiry | User-selected bounded expiry and manual replacement; no renewal service. |
| Contents | Read/write for immutable Git objects/records, exact refs and source/merge inspection. |
| Pull requests | Read/write for complete candidate lookup, exact creation and protected merge. |
| Actions | Read/write for authenticated run/job observations, explicitly bounded dispatch and sole-owner cancellation. |
| Checks | No token selection prerequisite for public provider check-run reads; the qualification probe explicitly queries them anonymously. Actual evidence binding remains required. |
| Commit statuses | Read-only for exact source-bound required evidence; public accessibility does not certify write authority. |
| Administration | Read-only for actual branch protection; no protection mutation through the operating credential. |
| Metadata | GitHub's required read access. |
| Other permissions | None initially; no Issues, Secrets, Environments or Workflows write. New endpoint requirements return to review. |

One fine-grained token's selected permission set applies to all selected repositories;
the selected repository list is not per-repository privilege separation. Existing gh
credentials are administrative setup authority only, never the operating token.
The permission inventory was checked against GitHub's official REST permission map:
https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens
The public check-run exception is documented at
https://docs.github.com/en/rest/checks/runs#list-check-runs-for-a-git-reference

Environment preparation alone does not prove job isolation. The deployed wrapper
must first establish exact workflow/job/source provenance and rejected foreign-ref
access. Verify all actual allow/deny paths after credential storage and before any
manual publication. Native representative domain coverage and exact provider/template
pairing are independent release inputs; do not substitute hosted fixtures for them.

## Next source delivery

Implement start/claim/planning and finite wait/reconciliation on the existing retained
engine and original serializer, paired with the single-job trusted writer workflow.
Keep inspector and candidate work credential-free and revalidate complete candidate
data before publication. Publish and review that source before normal promotion.
The final deployment pins are determined by the actual accepted source, not by this
planning revision or the earlier unselected bootstrap proposal.

Before that delivery, the finite credential probe runs only from accepted master
source using release-control, the dedicated token and locator, and the private
numeric identity in CONFIGS_RELEASE_OPERATING_REPOSITORY_ID. This is read-only
provisioning evidence, not an operating wrapper or a selected bootstrap.

## Private history and empty-repository boundary, 2026-10-02

At dev 5e5c3bc, Journal requires an existing operations head and Snapshot requires
complete local original Git objects. The published ownership/inspector increment
still supplies neither private transfer nor initial records. REST commit metadata
alone cannot be assumed to reproduce arbitrary original signed commit bytes.
Choose a separate narrowly isolated trusted Git acquisition process, with the
credential boundary reviewed before source implementation and no worktree checkout.

GitHub's Git references documentation explicitly refuses creating a ref in an
empty repository, even when the object exists:
https://docs.github.com/en/rest/git/refs#create-a-reference
The Contents API documents create-file PUT, an optional branch parameter, fixed
file contents and Contents write permission:
https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents
This supports a separate narrow initialization proposal. Actual empty-repository
behavior and lost-ack reconciliation must be observed on accepted deployed source;
the documentation does not establish an actual permission or bootstrap receipt.

Git acquisition must suppress ambient configuration/credentials, templates, hooks,
redirects/proxies, external protocols, alternates, shallow/promisor/lazy fetching
and replacement/graft interpretations. Original Git object identity and verified
complete history remain loader inputs; no REST-based synthetic history conversion
is accepted. The Git documentation supplies the fetch/config mechanisms:
https://git-scm.com/docs/git-fetch
https://git-scm.com/docs/git-config

Root reviewed these source/design constraints against the current loader/Journal
and official API/Git documents. AC1-AC6 remain pending; the private connection,
bootstrap proposal digest, operating source pins and permission receipts remain
private unresolved deployment inputs. No initial seed or record was written.
