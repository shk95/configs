# Retire the repository legacy Darwin capture caller
kind: spec
date: 2026-10-01
scope: repository
status: approved
issue: #469
review-by: 2026-10-15

## Outcome and assignment

Plan a coherent repository retirement of the legacy capture-to-provider-publication
route after the versioned host-document Darwin CLI is delivered. Obsolete calls
refuse explicitly without reading host settings, projecting originals, editing
provider payloads or changing Git state. The new preview/review/save workflow uses
explicit host-owned documents; retirement never redirects a publication invocation
to Save, adoption, activation or another command.

Root reviewed the read-only proposal and assigned B this planning delivery only.
Planning workspace is `../configs-wt/legacy-capture-retirement-plan`, branch
`feature/repository-legacy-capture-retirement-plan`, pinned from fresh origin/dev
21532ddf5b6f98cd7ade1163ffa43a44b16dd339. Source implementation is unassigned.
A later worker pins its actual dev and reviewed plan revision separately after
all prerequisites and explicit assignment. Root alone integrates planning/source
PRs; no auto-merge, deployment or operational permission follows from this plan.

## Dependencies and source pickup gates

1. Actual repaired U2 PR #458 integration and its final-head/post-merge proof.
   `docs/work/unixlike/provider-consumer-contract/spec.md` assigns host-document
   capture and explicitly separates this repository retirement. Its current
   repaired source, not old successful checks, is the prerequisite. Preserve the
   native installed-tool evidence's synthetic rendering, originals-unchanged and
   no activation/deployment limits; source changes need their own qualified proof.
2. A separately assigned Unix-like prerequisite plan/source delivery, after U2
   integration. The Unix-like owner owns Justfile recipe retirement, its invariant
   locator reconciliation and dated decision/current-state updates. This repository
   planning PR edits no Unix-like document or executable. Root assigns that owner
   separately; the recommendation is not an assignment.
3. Actual D refresh-candidate source delivery and integration. D owns root
   `tool/version-control/test`, README and CONTRIBUTING during that source lane.
   Repository retirement cannot edit these concurrently. Re-query actual final
   files/interfaces and open ownership before assigning source; merge conflict is
   not a substitute for agreed ownership.

A roadmap entry is not needed. This standalone pair is the repository plan; a
separate Unix-like spec/report should bind its prerequisite and proof without
copying repository acceptance. One repository source branch/PR carries the whole
retirement once all dependencies are delivered. Changed scope returns to root.

## Unix-like prerequisite and registry detach order

The separate Unix-like owner changes only its owning scope:

- Justfile `karabiner-capture` is removed or becomes permanent explicit nonzero
  retirement guidance. No implicit new CLI, Save or commit/publish call is allowed.
- `docs/policy/invariants/unixlike/host-written-payload-projected.md` retains actual
  U2 schema/tool and positive/refusal fixtures. Detach its root
  `enforced-by: fixture tool/version-control/test` locator before repository
  retirement removes that legacy fixture's invariant tag/block. A declared locator
  without its tag fails the registry. The old registered tag may remain until the
  repository caller is retired; no replacement enforcement gap is allowed.
- The Unix-like projection decision receives dated reconciliation and
  `docs/status/unixlike.md` updates current usage while preserving historical
  #177/#178/#183, source SHAs, activation and projection evidence as historical.

The domain legacy tool, its `project` flags/markers, legacy check/apply behavior
and `karabiner-test` remain outside retirement. Existing `just karabiner-check`
uses that tool. Do not delete it or reinterpret the historical payload contract.
The Unix-like prerequisite proves its own narrowed entry behavior, invariant
registry and independent host-document projection/capture/consumer positive and
negative checks. No installed app execution, real Save or activation is required
by the repository retirement itself.

## Repository owned files and behavior

Change `tool/version-control/commit` to remove legacy capture source-read,
projection, candidate-payload replacement, branch/commit/publication engine and
its constants, capture-only host options/help/topic/classification/dispatch paths.
Recognize obsolete invocations sufficiently to give explicit retired guidance
before readers, projection, any payload write or Git mutation. Legacy host flags,
dry-run, affirmative input and publish cannot bypass retirement. Unknown groups
or options keep their normal refusal. A permanent retired invocation refusal is
final behavior, not a disposable compatibility adapter. Do not introduce a PROV
shim or redirect to the host-document command.

In `tool/version-control/test`, remove only obsolete capture-specific payload copy,
host setup/helpers and capture-to-Git banner unit after registry detach. Replace
it with finite retirement refusal/no-write proof under appropriate adopted
repository invariant tags. Do not leave an untagged fixture unit. Shared
`uname_stub` must remain: it also proves Windows publish refusal. Retain generic
multi-path helpers when other operations need them; remove misleading legacy
comments without opportunistic unrelated cleanup.

README stops advertising capture-to-provider commit. CONTRIBUTING adds the actual
pinned Darwin preview → explicit content/destination review → Save workflow,
mode-600 proposal, guarded explicit host documents, stale/partial retry, separately
owned consumer connection and activation boundaries. The current Windows capture
workflow is independent and unchanged. Usage references the actually delivered
CLI rather than an unavailable proposal or an inferred private consumer adoption.
No root operator entry routes publication into Save.

Update this child report with actual per-criterion source proof. Necessary durable
repository decision/invariant changes require owning review; work documents alone
create no policy. This source outcome contains no Unix-like edits.

## Verification and stop conditions

Use disposable synthetic repositories and readers, official fixture Git isolation
and explicit functional controller Python runtime. For obsolete invocations test
matching/drift/missing/unreadable inputs and projection/reader/Git-write spies.
Check payload and synthetic original bytes/modes, index, HEAD, branches and
remote refs before/after; affirmative input, dry-run and publish still refuse.
No fixture reads or writes real app/original paths. Positive new CLI preview/save
proof stays in explicit disposable targets and is inherited from delivered U2,
not performed implicitly by a retired invocation.

Run narrow refusal fixtures and then the normal repository suite, including
brew/cask/mas/flake, hook/branch/check/publication behavior and Windows publish guard.
Preserve existing conservative affected dispatch and source-bound Linux/native
Git-for-Windows evidence when selected. Run normal work/registry/hygiene/domain-read/
records/design-citation/provisional/secret checks and final-head Required checks.
Document-only planning CI proves form, not source criteria or native operation.

A missing U2/Unix-like/D delivery, registry gap, a needed domain tool retirement,
changed capture/ownership semantics or shared source claim returns to root before
implementation. No app restart/install, host originals Save, private adoption,
activation/Apply, release/promotion/tag, credential/Environment operation, schedule
or source cleanup is authorized here. Controller global-history/manual/scheduled
and release-parent completion remain independent.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Actual repaired U2, Unix-like prerequisite and D refresh source are delivered/reviewed before separately assigned repository source pickup; no parallel ownership or domain edits occur. | review, policy checks |
| AC2 | Every supported obsolete capture invocation, including host options/dry-run/affirmative/publish forms, gives early explicit retirement refusal before host read/projection/payload write/Git mutation and never redirects to Save or another publication route. | review, fixtures, policy checks, affected dispatch |
| AC3 | Matching/drift/missing/unreadable synthetic originals and provider payloads retain exact bytes/modes, with index/HEAD/branches/remote refs unchanged; reader/projection/write spies prove no execution despite legacy flags. | review, fixtures, policy checks, affected dispatch |
| AC4 | Capture-only source/fixtures/help are retired after Unix-like registry locator detach while actual U2 enforcement and historical domain tool/project contract remain intact; no orphan locator/tag or untagged fixture exists. | review, fixtures, policy checks, affected dispatch |
| AC5 | Normal operator regression remains valid for brew/cask/mas/flake/hooks/publication and Windows refusal; shared uname_stub and unrelated helpers/checks survive, with exact-head CI and selected native governance proof. | review, fixtures, policy checks, affected dispatch |
| AC6 | README/CONTRIBUTING describe actual delivered pinned host-document preview/review/save, explicit destinations, stale/partial behavior and separate consumer/activation permissions; no legacy publication usage or Windows workflow regression remains. | review, fixtures, policy checks, affected dispatch |
