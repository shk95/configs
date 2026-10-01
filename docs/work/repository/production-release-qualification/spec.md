# Production release qualification before operating rollout
kind: spec
date: 2026-10-01
scope: repository
status: approved
review-by: 2026-10-15

## Outcome and ownership

Prepare complete reviewed production qualification inputs for the existing offline
release-preview and later controller, without publishing releases. Repository owns
classification/impact/evidence mapping and qualification data. Configuration-domain
API or desired-state changes remain separate domain-owned work. Root is sequential
planning/continuation owner; source pickup requires a recorded execution issue,
current dev and reviewed plan revision after prior lanes are integrated.

## Dependencies and decisions

Use provider-release-contract/spec.md and its initial independent unixlike-v1.0.0
and windows-v1.0.0 direction, delivered provider/Windows contracts, release-preview,
global-history and refresh outcomes. Calendar tags remain immutable. Do not infer
semantic readiness from an existing calendar tag, fixture or source integration.

Inventory actual public configuration inputs, constructor/module defaults and
constraints, inspection/generation/capture/consumer behavior, compatibility surfaces
and operator entry points. Map every production-relevant classified path to explicit
checks and justified coverage. Keep repository-only source distinct. Unknown ownership,
unmapped contract paths, unavailable required evidence or declared defects refuse.
Do not add common material to hide incomplete domain mappings.

Pin mapping rules and exact tool identities. Select justified representative Unix-like
evaluation/build and native Windows generation/runtime cases that cover the public
promise rather than private fleet outputs. Private final-host evidence remains
consumer-owned. If a public promise is untestable, narrow it through owning review
instead of waiving verification. Domain test implementation belongs to that domain.

Prepare a source-bound bootstrap proposal for the selected candidate and accepted
contract baseline in separately reviewed history, avoiding self-referential SHA.
Legacy-history cutover is explicit; optional Release-* declaration requirements do
not silently become global commit policy. After cutover, exact structured impact,
compatibility/rationale/migration and inverse-revert behavior must drive qualification.
No production bootstrap source is chosen without its actual maintainer review.
Template adaptation and exact provider/template pairing must be verified where an
affected public API release requires them. Provider integration is not release proof.

## PR and verification boundary

One repository implementation PR carries reviewed mappings, qualification fixture
positive/refusal cases, necessary operator documentation and this report. Separately
scope any missing Unix-like/Windows contract checks. Exercise real classifier paths,
missing coverage, mismatch, defects, unavailable evidence, bootstrap identity and
legacy cutover refusal. Preserve Linux/native Git-for-Windows evidence separately.
Authenticity of actual CI receipts is the transport child's obligation; synthetic
inputs cannot qualify a real production release.

Replan on unsupported public contracts, cross-domain source ownership, uncertain
bootstrap selection or weaker acceptance. No operating credentials, live workflow,
promotion, tag creation/push, host activation or Windows Apply is assigned.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Reviewed actual public contracts and all production-relevant paths have explicit domain/check mappings; unknown/unmapped paths and defects refuse. | review, fixtures, policy checks, affected dispatch |
| AC2 | Required representative evidence covers the public promise with pinned tools and separate domain lanes; unavailable evidence cannot qualify release. | review, fixtures, policy checks, affected dispatch |
| AC3 | Source-bound bootstrap/legacy cutover proposal preserves calendar tags, fixes baseline identities and refuses implicit semantic conversion. | review, fixtures, policy checks, affected dispatch |
| AC4 | Structured cumulative impact, compatibility/migration and inverse-revert qualification retain exact comparison and template-pair obligations. | review, fixtures, policy checks, affected dispatch |
| AC5 | Official offline qualification and Linux/native Windows positive/refusal proof stay read-only; synthetic receipts never become production certification. | review, fixtures, policy checks, affected dispatch |

Amended 2026-10-01 (AC1, AC5): actual Git-tree inventory found the retained Nix
editor settings unclassified and historical Unix-like root paths still on master.
The repository prerequisite in legacy-unixlike-classification/spec.md must integrate,
then a separate Unix-like editor-settings relocation must integrate before this
suspended lane resumes. Root preserves and continues the existing #471 worktree.
No unknown path is waived and no source proof becomes operating certification.
