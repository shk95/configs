id: repository/local-development-integration
statement: Work starts from local dev without remote admission; helpers never publish or prune implicitly, and sequential integration advances clean dev to the exact verified combined candidate with failure on unexpected base change.
rationale: AGENTS.md § Governance design
enforced-by: tool tool/worktree.sh
enforced-by: tool tool/version-control/commit
enforced-by: tool .githooks/pre-push
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test-local-workflow
enforced-by: manual The integrator confirms candidate/base SHA, combined-result verification, clean worktrees and sequential ff-only integration
owner: repository maintainer
decision: docs/policy/decisions/repository/local-development-workflow.md § Decision
