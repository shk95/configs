id: repository/release-control-preview-only
statement: Release controller preview verifies exact retained control dependencies, treats supplied records and API transcripts as data, and produces only bounded decisions or refusals without credentials, external effects or candidate execution.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: tool tool/version-control/release-control
enforced-by: fixture tool/version-control/test-release-control.py
owner: repository maintainer
decision: docs/policy/decisions/repository/release-controller-preview-boundary.md § Decision

Strict records, approved-package assertions and fake endpoint observations prove
the isolated preview contract, not production approval or actual permissions.
The inert workflow has no schedule or operating connection. Linux and native
Git-for-Windows fixtures remain separate evidence; unavailable runtimes refuse
or report unverified instead of passing. Later operating transport is separate.
