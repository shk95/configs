# Program declarations and host selection
kind: spec
date: 2026-11-14
scope: unixlike
status: approved
review-by: 2026-11-21

Give each selectable program a stable ID and a source module containing its
settings and supplier choices. Keep the existing class composition and use
the program's directory as the host selection group. Profiles preserve
environment defaults. A host can override a group or a program, within the
platform and native class the program supports.

Nix supplies the shared environment and owns its managed settings. Homebrew
supplies selected macOS programs, and Nix-managed mise supplies Claude Code
and Codex on supported Linux homes. The host owns its App Store choices,
`mas`, and Homebrew lifecycle. Integrating the consumer extraction requires
adopting a provider release that supplies the extracted programs.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Relocate existing modules by responsibility and program purpose while preserving ordered packages, payload content and configuration placement. | evaluation, review |
| AC2 | Verify the program declaration, group and individual selection, supplier eligibility and dependencies, effective settings and inventory, duplicate ownership refusals, and the published host contract. | evaluation |
| AC3 | Verify the managed mise fragment, installation of missing requests, failure propagation, local configuration and old version preservation, and shell precedence. | evaluation, build |
| AC4 | Run the provider suite and evaluate every paired host with a candidate override. Preserve the pre-extraction Darwin formulae, casks, App Store selections and lifecycle policy. | evaluation, build |
