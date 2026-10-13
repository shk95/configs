# Align verification with the provider boundary
kind: spec
date: 2026-10-13
scope: repository
status: approved
review-by: 2026-11-12

## Implementation

Use current public API ownership rather than historical machine delivery as
the verification boundary. Keep finite contract and composition witnesses,
payload validity and owned scripts. Remove automatic host closure and VM
qualification. The repository connection and Unix-like implementation are
separate source changes and must be reviewed together before integration.
Windows behavior and private consumer source are outside this work.

Local base was dev 12abd979e9aaa710c61bde0146f8769e4e437a78; selected master
bbdd265591788de1a2de4b5d8affccad00672eda was reflected by an authorized merge
before authoring. No source commit, local integration or remote operation is
authorized by this work item.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | CI and the local check invoke one provider suite and retain classification and the stable gate. | fixtures, affected dispatch |
| AC2 | Automatic annotations describe focused provider artifact build evidence and claim no consumer native runtime. | fixtures, review |
| AC3 | Workflow and architecture describe provider and consumer verification ownership accurately. | policy checks, review |
| AC4 | Existing prior-writer annotations support publication retry without writes while newly generated writes require current evidence; artifact build wording remains accurate. | fixtures, review |

## Independent review correction

Amended 2026-10-13: AC4 adds recovery compatibility, semantic toplevel coverage
and focused generated-file parsing as applicable to this scope, following the
maintainer's request after Sol 6.1 medium and Astra medium reviews. Original
AC1–AC3 remain unchanged.
