# Unix-like tool comment cleanup

kind: spec
date: 2026-09-25
scope: unixlike
status: approved
review-by: 2026-10-25
issue: #397

The Unix-like module reorganization left source comments that point to files
which have moved. Correct current references so nearby tooling and module
relationships can be followed from the tree as it exists.

## Decisions

Update only current explanatory comments and script help references. Keep
runtime code, intentional negative fixture paths, and historical decision
records unchanged. Map each old module path to the concern that now owns it
and use the public Windows entry point in the one cross-domain comment.

## Increment

One Unix-like PR carries the source-comment corrections and their review and
evaluation evidence. No host activation is part of the change.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Current Unix-like source comments name existing modules and check paths, apart from explicit historical or negative fixture examples. | review |
| AC2 | The Windows suite reference names its public entry point; source changes are comments only, with no executable code or Nix option value changed. | review, evaluation |
| AC3 | Unix-like checks and scope classification pass for the comment-only change. | evaluation |
