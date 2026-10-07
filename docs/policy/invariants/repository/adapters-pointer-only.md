id: repository/adapters-pointer-only
statement: A model-specific context, command or skill file points to authoritative project guidance or an explicitly adopted skill source and states no policy of its own.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: manual the reviewer confirms that a model-specific adapter points to authoritative project guidance or an explicitly adopted skill source without adding independent policy
owner: repository maintainer
decision: docs/policy/decisions/repository/external-work-role-orchestration.md § Decision

`CLAUDE.md` imports `AGENTS.md`. Tracked local workflow skill adapters and
command aliases are removed. Remaining model-specific instructions discover
project guidance; optional external skills read the target procedure. No
installed plugin or source-relative replacement adapter is required.
