id: repository/workspace-preservation
statement: Workspace removal refuses an unreviewed head, unpreserved unique source history, dirty state, ignored data and unfinished operations, and never removes the primary checkout.
rationale: AGENTS.md § Governance design
enforced-by: tool tool/version-control/workspaces
enforced-by: fixture tool/version-control/test-mechanics.py
enforced-by: schema tool/version-control/recovery.py
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Mechanical operation

A named topic ref retained in the same clone at the exact reviewed head is
valid preservation when removing only its worktree. Unique commits remain
visible in the review. Ref mismatch, data loss or an unfinished operation
still refuses. External bundles are optional additional preservation, not a
prerequisite to retaining an already preserved local branch.
