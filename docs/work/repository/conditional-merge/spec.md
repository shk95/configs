# Conditional asynchronous protected merges
kind: spec
date: 2026-10-06
scope: repository
status: approved
review-by: 2026-10-20
issue: #533

## Problem and outcome

An authorized integrator currently waits until CI and protected merging finish.
Move that wait to GitHub without delegating review, accepting later source, or
bypassing protection. Support both topic-to-dev integration and explicit
dev-to-master promotion. This plan does not enable remote writes or change the
current operating policy before its implementation is adopted.

Keep the existing integration and promotion skills. They perform their own
review and authorization, then submit one common bounded merge request. Policy
belongs in the adopted decision and invariant, human procedure in CONTRIBUTING,
and deterministic execution in repository tools and Actions. No new CI skill,
state database, status labels, or local queue is needed.

## Request and execution

One explicit workflow dispatch carries four values: PR number, target branch,
approved head SHA, and observed target SHA. Full SHAs are required. The Actions
run, authenticated actor, inputs and result are the request record. Dispatch
authorization is distinct from worker delivery. A worker cannot submit a merge
merely because its PR is Ready. Successful submission means requested, not merged.

Expose one operator command through tool/configs; Actions invokes its underlying
implementation directly. Submission reports a confirmed run URL or an ambiguous
submission requiring inspection, never retries a possibly accepted write blindly.
The operator can leave after confirmed submission.

The workflow runs accepted tooling rather than executable source from the PR.
Wait at most 60 minutes for the existing Required checks and all protection
conditions. Reuse the current ci-source evidence format to bind the approved
base, head and computed merge tree to the actual CI run. Verify current evidence,
including superseding reruns; old success does not override a newer failure or
pending run. Keep writer credentials outside candidate execution and obtain them
only where needed. Credentials have no branch-protection bypass.

Immediately before merging, requery Ready state, same-repository source,
supported independent PR shape, head and target identities, outstanding
auto-merge requests, required checks, reviews, resolved conversations and explicit
blockers. Unknown state is not success. This path does not arm native auto-merge.
Explicitly blocked or high-risk candidates require their admission-specific
review; no blanket human approval count is introduced.

Call the protected merge API with the approved head SHA and merge method merge.
Confirm the PR's actual merge commit, parents and tree. Distinguish requested,
merged, and merged-with-audit-failure in Actions output. A completed merge does
not create a release tag, GitHub Release, deployment, activation or Apply.

## Target-specific admission

Dev accepts reviewed same-repository independent topic PRs under the existing
scope and integration rules. Master accepts only an explicitly approved
same-repository dev promotion. Retain the one-open-master-PR rule and the existing
promotion validator, including accepted input-patch ancestry. The input patch
workflow keeps its own source validator, credentials and tagging contract.

CI runs independently. Serialize writer execution per target; master's writer
group is shared with the existing input patch writer. Do not cancel an active
writer when another request arrives. Use explicit pending-run retention rather
than silently replacing earlier pending requests. A pending run does not renew
approval. Multiple admitted requests may enter, but after one moves the target,
the others stop as stale. No merge ordering decisions are delegated to workers.

## Refusal and recovery

| Observation | Result |
| --- | --- |
| Both identities unchanged and exact-source required CI/protection satisfied | Protected merge, result verification and audit |
| Head or target changed | Stop; fresh inspection and explicit admission required |
| CI failed or cancelled, unsupported candidate, or invalid request | Stop and preserve PR |
| CI/protection evidence pending or temporarily unknown | Bounded wait; timeout stops visibly |
| Same approved source already merged | Verify remote identity; report completion without another merge |
| Merge API result ambiguous | Read remote PR and merge identity before any retry |
| Audit fails after confirmed merge | Report audit failure separately; no automatic rollback |

No automatic branch update, rebase, source repair, or reapproval is introduced.
Cancellation is confirmed before worker repair. If the request merged while
cancellation was attempted, inspect the result rather than claiming revocation.
Actions cancellation is not an atomic rollback of an API request. Recovery uses
GitHub records; loss of a local worktree does not lose the request.

## Concurrency guarantee and limit

The merge API provides an atomic expected-head condition, not an expected-target
condition. Rechecking the target and then calling the API is not a compare-and-swap
on the target. Concurrency serializes participating writers only. Strict branch
protection remains the final gate for protected merges outside that group.

All supported unattended writers must share the appropriate group. The existing
human commit --publish interface and direct protected manual merging must be
accounted for explicitly: they cannot be represented as serialized merely
because the new workflow is. Do not silently remove those interfaces.

Before enabling writes, qualify a target move between the last check and merge.
If strict protection does not safely refuse stale-source admission, restrict
concurrent admission to the supported writer path or return to planning. Do not
claim absolute target-SHA atomicity or rely on post-merge detection to prevent a
merge that already occurred.

## Pickup lane

Lane: conditional-merge. Owner: the assigned repository worker; assignment occurs
in the execution issue before pickup. Scope: repository. One coherent branch/PR
contains the common submission/tool/workflow, fixtures, adopted policy and
invariant, existing skill updates, procedure and current-state changes. The
planning pair may be reviewed first; it is not a runtime rollout.

Inputs and dependencies: this reviewed plan; current origin/dev pinned at pickup;
the GitHub-centered agent workflow and master input patch decisions; existing
promotion validation and exact-source CI record. There is no prerequisite domain
change or roadmap reprioritization. Record the reviewed plan revision separately
from the execution base.

Resolve before executable pickup: accepted workflow/tooling ref, authorized
dispatch identities and writer credential/environment choice. Inspect current
remote settings rather than inferring permission from local authentication.
Use the existing master writer group. General dev automation needs its own
permission boundary; do not implicitly extend release credentials to dev.

Evidence: positive and negative fixtures for every enforced property, policy
checks, and explicit remote dispatch qualification of dev and master. Local
fixtures do not certify remote behavior. Actual qualification merges require
separate explicit merge authorization; implementation/PR authorization is not
merge authorization. Candidate test source must never receive writer credentials.

Stop/replan for required protection bypass, unproven target race, automatic source
repair, native stack support, a new state registry, broadened release authority,
acceptance changes, or unexpected effects on another scope. A failed remote
qualification leaves its report criteria pending or unmet, never verified by
local fixtures alone.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Existing integration and promotion skills retain their separate review/authorization boundaries and submit the same bounded request without a new skill or duplicated CI policy. | policy checks, review |
| AC2 | An authorized unchanged dev PR or dev-to-master promotion merges only after current exact-source required CI and all protected conditions pass. | fixtures, affected dispatch |
| AC3 | Changed head/target, failed or superseded evidence, Draft/fork/stack input, unresolved blockers, unsupported master source and timeout cannot cause a merge. | fixtures, affected dispatch |
| AC4 | Competing requests serialize with existing master input patch writers; stale requests stop and later arrivals do not cancel active writers or silently replace pending requests. | fixtures, affected dispatch |
| AC5 | Submission confirmation, cancellation, ambiguous writes and reruns recover from GitHub and distinguish requested, merged and post-merge audit outcomes without duplicate writes. | fixtures, affected dispatch |
| AC6 | Accepted tooling and bounded credentials preserve branch protection; remote qualification accounts for external writers and proves safe handling of the target-move race without claiming atomic target matching. | fixtures, affected dispatch, review |
