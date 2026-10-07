---
name: integrate-work
description: Verify a local candidate and fast-forward dev sequentially.
---

# integrate work

Read CONTRIBUTING.md "Local integration and completion". Confirm integration
authorization and ownership of one integration operation at a time.

1. Read the candidate's exact SHA, recorded dev base, diff and evidence. Review
   that its first-parent path continues the development lane and any master
   synchronization uses a dev-based --no-ff merge.
2. Confirm primary is on dev, clean and has no operation in progress. Confirm
   dev still equals the reviewed base and is an ancestor of the candidate.
3. If not, stop. Reflect current dev in the candidate worktree, resolve there
   and verify again. Do not refresh all parallel workers on each dev change.
4. Confirm the final candidate worktree is clean and the checks apply to its
   exact combined result. Fast-forward dev to that SHA with --ff-only.
5. Confirm actual dev SHA and report local completion/push status separately.

No local queue, persistent lock service, evidence cache or GitHub admission is
required. A failed integration leaves dev unchanged and preserves useful work.
Master PR admission remains a separate run-version-control-workflow operation.
