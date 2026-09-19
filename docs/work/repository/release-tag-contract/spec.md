# State each host's evidence in a release tag annotation

kind: spec
date: 2026-09-19
scope: repository
status: approved
review-by: 2026-10-17

Agreed with the maintainer in the session of 2026-09-19. It is the unnumbered
item `docs/work/roadmap.md` places before order 4.

## Problem

1. **One line per lane cannot say which host it speaks for.** The annotation
   `tool/version-control/plan-release` templates has one `Evaluation`, one
   `Build` and one `Native runtime` line for the whole domain. The Unix-like
   domain already configures three hosts and the roadmap adds four.
   `unixlike-v2026.08.31` fits three hosts into those lines as prose
   ("built natively on the WSL host … darwin build is foreign-target only"),
   and its `Native runtime: passed` is true of two hosts and silent about
   the third. A reader cannot tell a host that passed from one nobody ran.
2. **The audit checks that the fields exist, not what they say.**
   `tool/version-control/audit` accepts any annotation containing the four
   field names, so `Native runtime: probably` is a valid release record.
3. **A tag is immutable and public.** Whatever an annotation says about a
   machine cannot be withdrawn, and the hygiene scan reads the index, never
   a tag.

## Decisions

### A host block per host

After `Domain: <domain>` the annotation carries one block per host the
release speaks for, and ends with `Deployment: not performed by release`:

```text
Domain: unixlike

Host: darwin
  Evaluation: passed; <reference>
  Build: passed; <reference>
  Native runtime: passed; <reference>

Host: wsl-nixos
  Evaluation: passed; <reference>
  Build: passed; <reference>
  Native runtime: unavailable; <why>

Deployment: not performed by release
```

- A block opens with `Host: <label>` and holds exactly the three lanes, each
  once, in any order, indented or not. It ends at the next `Host:` line, at
  `Deployment:`, or at the end of the annotation.
- A lane's value starts with `passed`, `unavailable` or `not applicable`,
  followed by the end of the line or by `;` and a free-form reference. No
  other value is a release state: a host whose check failed is not released
  around, because the tag certifies the domain.
- `unixlike` and `windows` tags carry at least one host block and no lane
  outside a block. A `common` tag deploys nowhere and keeps the three lanes
  at the domain level with the same value rule and no host block.
- Labels are unique within an annotation.

Rejected: the three lanes kept at the top with a line per host under each,
because one host's state is then read in three places and a host missing
from one lane is not visibly missing.

### A label names a kind of host, never a machine

A label matches `[a-z0-9][a-z0-9-]*` and names the kind of host — the lane
names the roadmap uses (`darwin`, `wsl-standalone`, `wsl-nixos`), `windows`
for the Windows host. The annotation carries no machine name, account name
or machine-unique identifier. An operating-system version or build number
describes a kind of host and may appear in a reference. The grammar is
checked; the absence of machine identity is a reviewer's evidence item,
because a machine name is not lexically decidable.

### The annotation declares its own hosts

The contract enforces the form, not the list: which hosts a release speaks
for is the releaser's statement. `plan-release` is a POSIX shell tool of the
`repository` scope and must not evaluate a domain to learn its hosts, and a
host list file written now would duplicate the typed host inventory of
roadmap order 4. Comparing an annotation with a domain's declared hosts is a
later, separate change, once that inventory exists.

Rejected: a per-domain host list file read by `plan-release` and the audit
(duplicate of order 4); deferring the contract until after order 4 (the
first tag after the inventory lands would still be in the old form).

### The two existing tags are excepted by name

`unixlike-v2026.08.31` and `windows-v2026.08.31` are immutable and predate
the form. The audit lists those two names and holds them to the check they
were created under (the four field names present). The list is closed: the
fixtures prove that any other tag name in the old form is refused.

Rejected: a cutoff date read from the tag name, because a tag created today
with an earlier date in its name would pass as legacy.

## Increments

1. This spec and its report.
2. The contract and its enforcement in one change, so that no commit states
   a rule the tools do not hold: the decision record; `INV
   repository/release-tag-contract` restated; `docs/policy/architecture.md`
   (Version control and releases), `CONTRIBUTING.md` (domain releases) and
   the release evidence items of
   `docs/policy/definition-of-done/repository.md`; the `plan-release`
   template; the audit's annotation check with the legacy list; fixtures in
   both directions in `tool/version-control/test`; the skill's Release
   operation if its wording depends on the old form.
3. `docs/work/roadmap.md` marks the item done and the report ends.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | A decision record, the restated invariant, `docs/policy/architecture.md`, `CONTRIBUTING.md` and the release evidence items of the repository Definition of Done state the host-block form, the three values, the label rule with its reviewer evidence item, the `common` form and the closed legacy list, and no document still describes domain-level lanes as the form of a `unixlike` or `windows` tag. | review |
| AC2 | `tool/version-control/plan-release` prints the host-block template for `unixlike` and `windows` and the domain-level template for `common`, and still never creates a tag. | fixtures |
| AC3 | `tool/version-control/audit` accepts a tag whose annotation follows the form and refuses, naming the tag and the defect: a `unixlike` or `windows` tag with no host block; a block missing a lane or repeating one; a lane outside a block in those domains; a value outside the three; a label outside the grammar; a repeated label; a `common` tag carrying a host block. | fixtures |
| AC4 | The audit accepts `unixlike-v2026.08.31` and `windows-v2026.08.31` in the old form and refuses any other tag name in the old form. | fixtures |
| AC5 | Each fixture added names `INV repository/release-tag-contract`, and a mutation that switches off each refusal of AC3 and AC4 fails the unit. | fixtures |
| AC6 | `tool/version-control/audit` run on this repository with its two real tags reports no failure, and `invariants`, `design-citations` and `work` pass on the change. | policy checks |
| AC7 | `Required checks` passes on the head of every pull request of this work before it merges. | affected dispatch |
