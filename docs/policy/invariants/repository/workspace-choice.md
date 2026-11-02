id: repository/workspace-choice
statement: Source authoring uses master or a named topic in the user-selected current or linked workspace, with isolated workspaces for parallel authors.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool tool/version-control/authoring
enforced-by: tool tool/version-control/workflow
enforced-by: fixture tool/version-control/test-local-workflow
enforced-by: manual The reviewer confirms the user answered the workspace question and parallel authors were isolated
owner: repository maintainer
decision: docs/policy/decisions/repository/master-topic-workflow.md § Decision

Workspace location is selected with the user and retained when continuing the
same task. Ask when the choice is missing or must change. A clean start takes
an explicit choice and records it; the argument does not attest human consent.
