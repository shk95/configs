id: repository/pr-integration-authority
statement: Remote pull requests preserve integration candidates independently of local workspaces, workers deliver without admitting merges, and only an authorized integration role admits changes through the protected canonical branch.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: manual the reviewer confirms remote recovery, worker and integration authority separation, and the protected branch settings at the delivery revision
owner: repository maintainer
decision: docs/policy/decisions/repository/github-agent-workflow.md § GitHub-centered agent workflow

A local checkpoint holds execution progress only. Candidate enumeration uses
remote state. Native Draft, Ready, check and merge states have no parallel
state registry or labels. Cleanup is independent from admission and requires
data-preservation review. Agent role compliance is a reviewed procedure;
branch protection supplies the server-side PR and check gate.
