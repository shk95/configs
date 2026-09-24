# Make the WSL command-line boundary explicit

kind: spec
date: 2026-09-24
scope: unixlike
status: approved
review-by: 2026-09-25

## Problem

Unix-like status, decisions and comments still describe WSLg as deferred.
The current WSL outputs already omit graphical classes and disable NixOS-WSL
GUI options, but the fixture does not check those options. The maintainer has
decided that WSL GUI is outside the intended outputs.

## Decisions

- Amend the existing WSL invariant and decisions. A future request begins by
  revising the architecture and invariant before implementation planning.
- Keep both WSL outputs command-line only and retain the explicit `false`
  values for the Windows graphics driver and Start Menu launchers.
- Extend the existing evaluation fixture to cover those values. Keep the
  existing checks that graphical class markers are absent from both WSL homes.
- Keep Linux fontconfig support for tools that render files; remove its
  former WSLg rationale without changing the package or configuration.
- Reject removing the font package as part of this policy change: it also
  serves noninteractive Linux rendering, and removing it changes host output.

## Increments

| Increment | Scope | Evidence lane |
| --- | --- | --- |
| U1 | unixlike | evaluation and review of the invariant, fixture, status and comments |

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The Unix-like invariant, decision and current status say that WSL GUI is outside the intended outputs and requires policy revision before any future implementation. | review |
| AC2 | Evaluation confirms that both WSL homes omit graphical class markers and NixOS-WSL keeps its graphics driver and Start Menu launcher options disabled. | evaluation |
| AC3 | Relevant Unix-like comments no longer present WSLg as planned, while configuration values stay unchanged. | review, evaluation |

## Excluded

Host activation, Windows native state, and removing command-line fontconfig
support.
