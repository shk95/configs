# External work-role orchestration with project-owned procedure
date: 2026-10-07
scope: repository
status: accepted
source: docs/work/repository/codex-work-cycle-extraction/spec.md

## Decision

The maintainer selected Agent Rack as the repository for reusable agent plugins.
Its existing Work Cycle package owns the six work-role instructions and their
Codex packaging. Remove configs' tracked local role skills and Claude workflow
discovery adapter/command aliases. Claude plugin development is deferred.
Preserve local excluded Context Bridge connection files and discovery data.

Configs retains its policy, contributor procedure, scope classification,
verification, hooks, CI, native checkpoints, promotion/releases and host
operations. CONTRIBUTING.md and tool/configs remain sufficient entry points
without an installed plugin. An external role reads target policy and never
supplies permissions, project tools or a new remote admission gate.

Source separation installs no replacement, tracks no external source-path
adapter and creates no marketplace or activation configuration here. The
maintainer chooses external distribution and later Codex installation and
consumer adoption explicitly. Structural checks do not certify installed-host
discovery or model use. Repository policy and its enforcement remain local.

This replaces the project-local role-location portion of
github-agent-workflow.md and local-development-workflow.md; their adopted
local completion, authorization, preservation and protected promotion rules
remain in force. Historical results and source imports remain evidence.

The maintainer owns future connection and provider-migration decisions.

## Amendment 2026-10-07: independent review and minimal context

The independent source review found the extracted core methods sufficient.
Retain project operator and checkpoint tools; further tool extraction and
actual-model behavior verification are not required for this preparation.

Model-specific discovery may point to authoritative project guidance or an
explicitly adopted skill source without adding policy. It does not require
an external workflow adapter. Classify first and read relevant current
contracts; cited history is consulted for a needed rule or ambiguity rather
than loaded as a default session obligation. Current invariant decision
pointers name the adopted local-development contract; earlier decisions and
their measurements remain historical records.
