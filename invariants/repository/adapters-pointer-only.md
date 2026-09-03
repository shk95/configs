id: repository/adapters-pointer-only
statement: A model-specific context, command or skill file discovers the canonical Agent Skills workflow and states no policy of its own.
rationale: docs/architecture.md § Repository governance plane
enforced-by: manual the reviewer confirms that a changed file under .claude/ or a model-specific adapter only points at the canonical source
owner: repository maintainer

`CLAUDE.md` imports `AGENTS.md`; `.claude/skills/*/SKILL.md` and
`.claude/commands/*.md` point at `.agents/skills/`. A test that asserts this
mechanically is welcome and would move this entry to `fixture`.
