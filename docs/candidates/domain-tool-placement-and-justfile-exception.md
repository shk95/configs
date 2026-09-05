# A domain's executable entry point lives under the domain's path; the Justfile is an unannotated exception

kind: addition
scope: repository
first-observed: 2026-09-05
target: docs/architecture.md § Change and dependency rules (one sentence); a comment on the Justfile arm of tool/version-control/classify
promote-when: a second domain tool is placed, or the classifier or the Justfile is edited anyway
drop-when: no new occurrence by 2027-03-05

## Observation

The maintainer asked why the Windows entry point could not sit at the root like the Justfile. The answer is recorded for that case in `docs/decisions/windows-entry-point-in-domain.md`; no general sentence exists. The Justfile's root placement is carried by a bare classifier arm with no comment, next to a `common/` non-arm that carries three lines of justification, and the Justfile holds 13 recipes in the `repository` group, so an edit to one classifies `unixlike` and selects the full Unix-like lanes.

## Evidence

- `tool/version-control/classify`, the `unixlike` arm; `grep -c "group('repository')" Justfile` is 13.

## Occurrences

- 2026-09-05: one question, answered in the decision record.
