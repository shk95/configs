# Plan and verify work in documents, and keep issues for execution state

kind: spec
date: 2026-09-19
scope: repository
status: approved
review-by: 2026-10-24

Agreed with the maintainer in the session of 2026-09-19 and revised the same
day after an independent review whose findings were reproduced before they
were applied. Depends on `docs/work/repository/docs-layout/`, whose tree
this spec writes into.

## Problem

1. **The planning rules cannot express the host roadmap.** "One milestone,
   one scope" and "one milestone, one branch, one pull request" forced the
   seven host lanes into chains of narrow single-scope milestones. This is
   the second occurrence: the Unix-like restructure study recorded the same
   block ("two milestones, neither meaningful alone") and left open whether
   to amend the milestone rule. The decision that a branch lives as long as
   its milestone did not hold on its first case (ten pull requests across
   two milestones), and no milestone-length branch has run since it was
   adopted.
2. **Plans and their verification live where they cannot be held to
   account.** Session specs and plans were kept untracked; issues carry
   acceptance criteria that can be edited after the fact; evidence is spread
   over issue comments.
3. **Issue closure is manual.** GitHub closes a linked issue only on a merge
   into `master`, and every pull request targets `dev`.
4. **The design area binds nothing and is little used.** Four documents,
   all written between 2026-09-08 and 2026-09-12 and none since; the
   argument it holds has no path to an outcome except an inlet elsewhere.

## Decisions

### Documents plan and verify; issues hold execution state

| Artefact | Nature | Holds |
| --- | --- | --- |
| `spec.md` | fixed, tracked | goal, decisions, acceptance criteria with the evidence lanes each requires, `review-by` |
| issue | mutable | the execution plan (increments as a checklist, order), progress, blockers, links to pull requests |
| `report.md` | fixed, tracked | for each acceptance criterion, its state and the evidence behind it |

A work item is `docs/work/<scope>/<slug>/`, holding `spec.md`, `report.md`
and optionally `study.md` (measurement and argument before a spec exists).

### Scope of a work item

A spec has one scope: the scope of its outcome, which names its directory.
Its increments may classify differently — a Unix-like spec whose procedure
lives in `CONTRIBUTING.md` has a `repository` increment — and each
increment's commit and pull request stays single-scope. A spec whose outcome
spans scopes is split into one spec per scope, linked through
`docs/work/roadmap.md`.

The documents carried from `docs/design/` keep the kinds and scope lists
they were written with (`study`, `plan`, `map`, several `scope:` lines) and
live under `repository`. `plan` and `map` are not written again, and only
`spec` and `report` are held to a single scope.

### A spec always has a report

- The spec and its report are created in the same commit. The report starts
  with every criterion `pending`, so no commit holds a spec without one.
- A report ends in exactly one of three states:
  - `done`: every criterion is `verified` in its required lanes;
  - `abandoned`: why, how far it got, what it left; unmet criteria are
    stated as unmet;
  - `superseded`: the spec that replaces it, and what was achieved.
- Once the report exists, a criterion in the spec is never removed or
  weakened in place. A change is a dated `Amended YYYY-MM-DD` paragraph
  naming the criterion, so the bar is visibly set before the work.
- A spec whose `review-by` has passed while its report is not terminal is
  reported by the audit, the way an overdue provisional measure is.

### Evidence lanes

A criterion names the lanes that must be `verified`: for a configuration
scope evaluation, build, native runtime, activation or Apply; for
`repository` fixtures, policy checks, affected dispatch. A criterion no
check can decide — what a document states, what remote state was observed —
names `review`: the evidence is the reviewer and the commit or the URL they
read, the standing an invariant's `manual` enforcement has.

### Not every change needs a spec

Work with more than one acceptance criterion or more than one pull request
has a spec. Any other change is a single pull request whose body carries its
evidence; an issue is optional.

### Issues

- An execution issue is opened when implementation of a spec starts; its
  first line names the spec path. One spec, one execution issue; the spec's
  header gains `issue: #<n>`.
- An issue carries no acceptance criteria and is never a source of
  evidence. What matters after closure is written into the report.
- A report issue — a bug, an upstream watch such as #176 — exists before any
  spec. When work on it starts it links a spec and becomes the execution
  issue.
- Closure follows the report. A tool reads the report: `done` and verified
  closes the issue; `abandoned` or `superseded` closes it with a comment
  linking the report. Nothing else closes an execution issue automatically.
- No commit message and no promotion pull request body carries a GitHub
  closing keyword — `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`,
  `resolve`, `resolves`, `resolved`, with or without a colon, before `#<n>`
  or `<owner>/<repo>#<n>`, anywhere in the message. Hooks are opt-in, so the
  merge gate checks every commit message in a pull request's range and the
  promotion job checks the promotion body; `commit-msg` refuses early.

### Milestones are retired

GitHub milestones are no longer used; the roadmap is
`docs/work/roadmap.md`. No lane labels are introduced.

A new decision record supersedes
`docs/policy/decisions/repository/branch-lives-as-long-as-its-milestone.md`
and the sentence of
`docs/policy/decisions/repository/design-documents-outside-the-authority-model.md`
that has work report through ordinary output and "not a report". What it
states:

- A branch is one reviewable increment — one issue, or what one judgement
  covers — cut from `origin/dev` and merged through one pull request when it
  is complete and green. A spec takes as many pull requests as it needs.
- Unchanged: commits, branches and pull requests are single-scope; the
  branch name rule; `dev`-only promotion; domain release tags; evidence
  reported per lane and never upgraded.

### The authority boundary

A work document is not policy. Authority stays where `AGENTS.md` puts it —
`AGENTS.md`, `CONTRIBUTING.md`, `docs/policy/`, the provisional registry and
the executable policy in `tool/`, hooks and CI. A spec binds only the work
it describes; a durable rule it produces lands in a decision record or an
invariant.

What `design-citations` enforces, restated for `docs/work/`:

- refused: a path to a work item (`docs/work/<scope>/<slug>/…`) in
  `AGENTS.md`, `CONTRIBUTING.md`, `docs/policy/**` except its `source:`
  header lines, `docs/provisional/**` except `source:`, `tool/`,
  `.githooks/`, `.github/`, `unixlike/`, `windows/`;
- allowed: `docs/status/**`, which links the reports behind current state
  instead of repeating them; `docs/work/**`; `docs/README.md`;
- allowed anywhere: the area's own files, `docs/work/README.md` (the format
  contract) and `docs/work/roadmap.md`, which name no argument.

The `AGENTS.md` sentence that work "reports through commits, check evidence
and docs/status.md rather than through a document of its own" is removed.

### Existing design documents

`commit-granularity-and-branch-lifetime` closes as superseded before it was
measured; `unixlike-restructure-plan` closes (its stages landed, #235);
`unixlike-restructure-study` records its question 6 as answered for the
milestone half, the tag half remaining open; `repository-domain-map` stays
closed.

## Components

| Component | Content |
| --- | --- |
| `docs/work/README.md` | the format contract: kinds, headers, the acceptance table, lanes, report states, the amendment form, the scope rule |
| `tool/version-control/work` | checks every work item: spec and report paired; header keys; a spec's single scope matching its directory; every criterion in the spec has one report row and the reverse; report state consistent with rows (`done` only if every required lane is `verified`); in range mode, a criterion removed or rewritten after the report exists needs a matching `Amended` paragraph; `--table` prints the index; `--overdue` lists specs past `review-by` |
| fixtures in `tool/version-control/test` | both directions for every rule above and for the citation rule |
| `.githooks/pre-commit`, CI | run `work` on every commit and in the merge gate |
| closing keywords | `.githooks/commit-msg` over the whole message; a merge-gate step over the pull request's commit messages; the promotion job over the promotion body |
| a workflow on push to `dev` | for each report that became terminal in the push and whose spec names an issue, run `work` on it and close the issue with a comment linking the report; `issues: write` only |
| `tool/version-control/audit` | reports overdue specs |
| `tool/version-control/audit-remote` | reports an execution issue whose report is terminal but which is still open |
| policy text | the new decision record; `AGENTS.md` Governance design (the milestone paragraph, the removed sentence, the authority boundary); `CONTRIBUTING.md` (branch and commit flow; "Plan work with GitHub milestones" replaced by "Plan and verify work"); the version-control skill (the Milestone operation replaced by Work); `docs/status/repository.md` (the milestone open condition removed); `INV repository/design-outside-authority` restated |
| `docs/work/roadmap.md` | the content below |

## Roadmap content

`docs/work/roadmap.md` states lanes and order, not schedule.

| Lane | Host | State on 2026-09-19 |
| --- | --- | --- |
| darwin | aarch64-darwin | operational; generation 36 activated |
| utm | aarch64 NixOS guest, UTM on the Mac | not started; `aarch64-linux` not in `systems` |
| orbstack | aarch64 NixOS OrbStack machine | not started |
| desktop | x86_64 NixOS, physical AMD APU desktop | not started |
| vm | x86_64 NixOS guest, VMware Workstation on a Linux and a Windows host | not started |
| wsl-standalone | x86_64 Ubuntu WSL, standalone Home Manager | operational; tagged `unixlike-v2026.08.31` |
| wsl-nixos | x86_64 NixOS-WSL | activated (generation 2); no in-place update path |

| Order | Work | Scope |
| --- | --- | --- |
| 1 | docs layout | repository |
| 2 | work model | repository |
| 3 | NixOS-WSL updated in place | unixlike |
| — | release tag contract: an annotation that states each host's evidence state (before 4) | repository |
| 4 | typed NixOS host inventory | unixlike |
| — | judgement on the CI decision's `reopen-when` (before 5) | repository |
| 5 | headless x86_64 guest on VMware Workstation | unixlike; a windows spec for the host install |
| 6 | headless aarch64 guest on UTM | unixlike |
| 7 | aarch64 OrbStack machine | unixlike |
| 8 | shared GNOME Wayland profile and the Linux terminal layer | unixlike |
| 9 | x86_64 desktop on an AMD APU | unixlike |
| 10 | GNOME on the VM guests | unixlike |
| 11 | installation and deployment (disko, nixos-anywhere, deploy-rs) | unixlike |
| deferred | WSLg on NixOS-WSL | unixlike |

Recorded with the roadmap:

- VMware Workstation for the vm lane: one guest profile serves both hosts,
  `vmwgfx` carries the later GNOME stage, and on the Windows 10 host it
  runs over the Windows Hypervisor Platform beside WSL2. Hyper-V is
  Windows-only, has no 3D guest graphics, and its enhanced session is xrdp.
  The decision record lands with order 5.
- aarch64 builds never use qemu binfmt on a WSL distribution; binfmt_misc
  is shared by every distribution. They run natively in the UTM guest or on
  a remote builder.
- The content of issues #18–#25 and #42 is carried into the roadmap items
  above and into the specs that start them; #21 into the deferred item.

## GitHub reorganisation

Remote writes, each restated before it runs:

- Close milestones 1, 2 and 5.
- Close #18–#26 and #42 with a comment linking the roadmap item that
  carries each; #26 as superseded by reports.
- Keep #176, #121 and #241 as report issues; the evidence #121 and #241 owe
  stays recorded in `docs/status/windows.md`.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | `docs/work/README.md` states the format; the new decision record, `AGENTS.md`, `CONTRIBUTING.md` and the skill state the work model and the retirement of milestones; outside superseded records and closed work documents, nothing tracked describes milestones as the planning surface. | review |
| AC2 | `work` refuses, each proved by a fixture: a spec without a report; a report without a spec; a criterion with no report row and a row with no criterion; `done` with a criterion not `verified` in a required lane; a spec whose scope does not match its directory or that lists two; a criterion removed or rewritten after the report exists without an `Amended` paragraph. It accepts the valid form of each, and a carried `study` with several scopes. | fixtures |
| AC3 | `work` passes on every work item in the tree, `docs-layout` and this one included. | policy checks |
| AC4 | Closing keywords are refused in every form listed, in the subject and the body, by `commit-msg`, by the merge-gate step and by the promotion job; `Refs #<n>` is accepted. Proved by fixtures. | fixtures |
| AC5 | The closure workflow closed a real execution issue from a terminal report and left open one whose report was not terminal, both observed on GitHub and linked here. | review |
| AC6 | `audit` reports an overdue spec and `audit-remote` reports a terminal report whose issue is open, each proved by a fixture. | fixtures |
| AC7 | `design-citations` refuses a work-item path in each refused location and accepts it in each allowed one, and accepts the area files anywhere. Proved by fixtures. | fixtures |
| AC8 | `docs/work/roadmap.md` exists with the content above. | review |
| AC9 | The GitHub reorganisation is done as listed, each item observed and linked here. | review |
| AC10 | Every pull request of this work passed `Required checks`. | affected dispatch |

## Out of scope

- The release tag contract and the CI `reopen-when` judgement: separate
  items on the roadmap.
- Any host work.
