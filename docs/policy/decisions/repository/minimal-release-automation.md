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

## One-time reconstruction

The maintainer authorized fixed a886934 pickup and one multi-scope assembly
branch, with scope-owned commits, instead of merging overengineered history
into the new dev. Preserve old shared refs, existing release tags, consumer
pins and unfinished work. Validate the exact assembled source before the
separate cutover review. The intended one-time adoption sets both dev/master
to that source with explicit expected-old-ref checks and protection restoration.
Afterward normal dev-to-master PR/merge promotion applies again.

The assembly CI entry is temporary and registered. This exception does not
allow general hook bypass, routine direct master edits or protection bypass
for the automated writer. Domain release never adopts or applies host state.
