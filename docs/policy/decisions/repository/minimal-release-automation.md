# Bounded releases and one-time reconstruction

date: 2026-10-05
scope: repository
status: accepted
issue: #515
source: docs/work/repository/minimal-reconstruction/spec.md § Implementation
reopen-when: A supported normal release cannot complete under the bounded path.

## Release boundary

Use ordinary GitHub PRs, Required checks, Environment review when needed and
immutable domain tags. Source declarations fix previous release basis, exact
version and change/compatibility text. Execution results stay in PRs/Actions;
they are not source-owned run or approval state.

Keep permitted automatic change scope, current candidate/check/approval agreement,
credential separation, tag immutability and remote result confirmation after
ambiguous writes. Recover one unfinished promotion before the next. If the
original source is lost, stop and require an explicit SHA. Past AC12 is not
inherited in full; private journals, retained object transport, approval
receipts, global fencing and complete notification deduplication are excluded.

## Manual operation

2026-10-06: provide one dispatch-only manual release using the same bounded
release operations. An explicit manual request omits clock and daily-cycle
scheduling choices only. One workflow refreshes permitted inputs, waits a
bounded time for current checks, integrates and prepares the exact promotion,
then performs separately reviewed publication. Approval holds no writer
credential or writer concurrency. Active manual runs make scheduled release
inspection wait; candidates are still rechecked immediately before writes.
Current GitHub PRs/checks/tags and job outputs suffice: no persistent cycle
record, label, comment command or new service is adopted. Manual execution
proves release operation separately from the scheduler's trigger delivery.

## One-time reconstruction

The maintainer authorized fixed a886934 pickup and one multi-scope assembly
branch, with scope-owned commits, instead of merging overengineered history
into the new dev. Preserve old shared refs, existing release tags, consumer
pins and unfinished work. Validate the exact assembled source before the
separate cutover review. The intended one-time adoption sets both dev/master
to that source with explicit expected-old-ref checks and protection restoration.
Afterward normal dev-to-master PR/merge promotion applies again.

The assembly CI entry was temporary and registered for the one-time adoption.
This exception does not
allow general hook bypass, routine direct master edits or protection bypass
for the automated writer. Domain release never adopts or applies host state.

## Verification cost

Keep local/fixture proof with source and remote CI proof in Actions/PR checks.
No follow-up report-only push is needed to copy a successful CI result.
Keep dev push CI for coordinator reentry. master uses its fully checked PR and
actual merge identity instead of another full push CI. Publication resumes
from ordinary schedule/manual/related CI events if its writer is interrupted. Remove
retired suites and the confirmed ninefold independent-suite repetition before
considering any more precise check selector. Fixture failure coverage and actual
normal-path operating evidence are distinct; no live failure-experiment project.

Future tags use domain SemVer fixed by source declarations. Preserve the exact
two historical tag objects and their old target across the one-time cutover;
this is a closed historical exception, not a calendar-tag allocation policy.

2026-10-06: the maintainer authorized chronological source-history refinement
and one replacement of the unconsumed Unix-like/Windows 1.0.0 tags. Preserve
the original shared refs and tag bytes before replacement. Pause automatic
writes, validate the candidate locally, replace both refs with expected-old
checks, restore protections and require exact-source dev CI before recreating
the two annotations. A failed qualification restores the preserved refs/tags.
Historical calendar tags remain exact. This one-time bounded migration exception does
not allow routine tag mutation or change the normal writer's refusal behavior.

The prior minimal dev/master and unconsumed tag objects are temporary rollback
material, not a second permanent source archive. Delete their backups after
successful qualification and replacement. Preserve the earlier overengineered
archive separately; original PR/Actions records retain historical proof.
