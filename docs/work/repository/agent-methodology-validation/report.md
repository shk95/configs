# Agent methodology correction results
kind: report
spec: docs/work/repository/agent-methodology-validation/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | One retained runner exercised immutable A/B and content-identified C in three sequential repeats; source digests, fixed cases and primary-checkout preservation are recorded below. Historical routes are explicitly reconstructed. |
| AC2 | verified | All 11 targeted cases pass in C, including partial staging, staged checker content, linked/alternate indexes, caller-data preservation and local/required-native states. Real format/lint/payload checks also pass in a metadata-free index export. The new invariant and applicable policy checks pass. |
| AC3 | verified | Missing-gitleaks fixture observes unavailable candidate verification. Author review compared README, environment and verification routes against AGENTS/procedure: continuation is conditional, prerequisites are explicit, dirty/staged/committed evidence is distinguished and no native/deployment evidence is inferred. |
| AC4 | verified | Corrected full repository suite exits 0: 16 workflow, 17 mechanics, 11 staged-check and 21 release cases plus existing isolation/commit/retirement/handoff fixtures. Alternate-index policy checks pass; the report records timing costs, failed exploratory checks, final limits and uncommitted scope-pure delivery. |

## Session observations

- Inspected actual Git state and the existing optimization spec/report before
  editing. The primary master checkout was clean at B and 13 commits ahead of
  its existing origin snapshot; no remote refresh was needed.
- Asked once for the missing workspace choice, as required by project policy.
  Continued read-only baseline inspection while the answer was pending.
  The maintainer selected a linked workspace. The tracked start command created
  `feature/repository-agent-methodology-validation` from B with one estimated
  logical commit; this is execution data, not commit authorization.
- Read the applicable work-record format, governance procedure, relevant
  invariants and repository definition of done. No role plugin, extra agent,
  remote audit or native provisioning was required.
- The first pre-edit repository doctor repeated capability evidence already
  available from the preceding analysis. That run was unnecessary for source
  inspection. Post-edit doctor runs were justified smoke checks of changed
  output, and the Unix-like doctor preceded reliance on real Nix checks.
- Added a focused runner before changing production code. The first B probe
  satisfied 2 of 11 desired cases. The first corrected-source run passed all
  11; the same runner was then applied to A/B/C.
- The first full suite failed because its absent-format fixture removed only
  the working file. Staging that deletion and staging its later restoration
  makes the fixture test the actual index subject while preserving all its
  local/unverified/required-native expectations. No passing expectation was
  weakened to hide the failure.
- An exploratory three-repeat timing batch overlapped the full fixture suite.
  Its correctness results were consistent, but its timings are excluded from
  the final timing sample. Final samples run without another agent-launched
  suite in parallel. Background host load remains uncontrolled.

## Source identities and reproduction

A is `e824c6f328edb9f9a73a66b5c00ae6523aefc23c`; B is
`53a3f7e09aa1e217567941c884e87f1af56de270`. A was exported with
`git archive` into disposable storage. B is read from the unchanged primary
checkout at that exact commit. C is uncommitted source in the selected linked
workspace, based on B. No branch switching, historical checkout mutation or
new commit is needed to compare the sources.

The retained `tool/version-control/test-staged-checks.py` accepts
`--source-root <export-or-checkout> --probe`. Run the same corrected runner
against each source three times, rotating A/B/C order within each repeat.
Default invocation is the failing/passing regression suite used by
`tool/configs test`; probe mode returns JSON observations even for failed
historical cases. A source failure is never reported as a passing regression.
The runner owns its temporary Git repositories and fixture environment.

The executed-source digest includes these six paths in this order:
`.githooks/pre-commit`, `.githooks/evidence`, `tool/doctor.sh`,
`tool/dispatch/select`, `tool/version-control/classify`,
`tool/version-control/hooks.sh`. For each, hash UTF-8 path, NUL, file bytes,
NUL using SHA-256; an absent historical helper uses the literal `<absent>`.
This identifies the measured mechanics, not an invented C commit or every
document in this outcome. The final runner itself has SHA-256
`ff0281c91dbdf249c456cae71e6b01800f5436439e23e010e4486e7632f86311`.

| State | Measured-source SHA-256 |
| --- | --- |
| A | `b9f211372ab007524256cb460b01be4ac60cd94d23e15ea05540c5d400a1faba` |
| B | `b7a2e497520f26854a0be3d6f617dceb7bb542f52e215a99a1c96f63c035c6cc` |
| C | `55b1a13ac564e1b4c0417709672b8df182389a4def4a3acf1a6089dab7d21ee1` |

## Same-case correctness comparison

These are deliberately selected problem/regression cases, not a sample from
which to estimate overall repository quality. Checkers are fixture doubles;
Git indexes, linked worktrees and hook processes are real. Every hook case
also checks that the caller's target content, index bytes and refs survive.
The alternate-index case separately checks the ordinary index.

| Fixed desired case | A | B | C |
| --- | --- | --- | --- |
| Bad staged content cannot hide behind a corrected working file | fail | fail | pass |
| Good staged content survives a bad unstaged working file | fail | fail | pass |
| A failing staged checker cannot be replaced by an unstaged passing checker | fail | fail | pass |
| An unstaged failing checker does not replace the staged passing checker | fail | fail | pass |
| Untracked payloads do not join staged checks | fail | fail | pass |
| A staged deletion ignores the untracked replacement | fail | fail | pass |
| Linked-hook Git context preserves source/index and checks staged content | fail | fail | pass |
| An alternate index supplies the checked content and both indexes survive | fail | fail | pass |
| Unverified local checks remain distinct from required-native failures | pass | pass | pass |
| Repository-only changes execute no domain checker | pass | pass | pass |
| Doctor names unavailable candidate verification when gitleaks is absent | fail | fail | pass |
| Total desired cases, consistent in three repeats | 2/11 | 2/11 | 11/11 |

A and B have the same selected-case failures. This is a gap retained across
the earlier optimization, not a regression attributed to that optimization.
Its other navigation, shared implementation and provider-entry improvements
are assessed separately below.

## Sequential timing sample

Environment: Linux x86_64, Python 3.14.8, Git 2.56.0. Three fresh disposable
fixture runs per source, in orders A/B/C, B/C/A and C/A/B. No other
agent-launched suite ran alongside these final samples. The host was not
dedicated, caches were not flushed and background load remains uncontrolled.

| State | Complete 11-case runner samples (seconds) | Median (seconds) |
| --- | --- | ---: |
| A | 4.253, 4.409, 4.348 | 4.348 |
| B | 4.340, 4.424, 4.421 | 4.421 |
| C | 4.851, 4.780, 4.791 | 4.791 |

The corrected runner costs about 0.370 seconds more than B at these medians.
This includes fixture setup, snapshot exports, checker subprocesses and
different failure termination points in old sources. It is not an isolated
snapshot microbenchmark or an estimate of end-to-end agent time. The outcome
is a correctness gain with measured local overhead; it supplies no evidence
of faster agent work or statistically established performance regression.
The added default fixture suite itself takes approximately five seconds here.

## Reconstructed document routes

These are source inspections with identical starts and finishes, not historical
agent sessions. A knowledgeable operator can open the relevant section
directly in all states. The shortest valid operation does not acquire extra
mandatory setup, planning or verification commands in C.

| Task start and finish | A | B | C and bounded difference |
| --- | --- | --- | --- |
| S1: Correct a known repository paragraph, ending with relevant review/global evidence | Relevant Classify/Verify sections of CONTRIBUTING and the affected source. | Authoring/verification concerns reached through the static index; source and required scans remain. | The 21-line development-feedback section explicitly distinguishes working prose review from index scans. It adds explanation, not a required suite. |
| S2: Modify a Unix-like payload, ending with parser/provider evidence and separate consumer evidence | CONTRIBUTING Unix-like/Verify sections; affected payload and checker. | Same domain checks through a shorter concern map; provider Just recipes/paths were separately corrected by the existing optimization. | Feedback table gives the parser route and labels its working-tree subject. Only later staged quick-check orchestration changes; domain semantics are unchanged. |
| S3: Change Windows behavior, ending with native validate/test/check or explicit unavailability | Windows section includes setup-dev in a block labeled read-only, despite that command installing tools. | Existing optimization separates installation from native read-only verbs. | Prerequisite/feedback tables point to the same native verbs and installation boundary; no Nix or new native-runtime improvement is claimed. |
| S4: Resume a task with known workspace/authorization, preserving current work | AGENTS and contributor procedure permit continuation, but README suggests inspect then start. | Conditional continuation remains in authority/procedure, while README still suggests that sequence. | README now agrees: inspect when orientation is needed, start only for clean new work, retain the known choice. Reinitialization was never required by authoritative policy. |
| S5: Inspect/verify a clean full-SHA candidate, ending with exact-source evidence | Infer assembly from workflow source or run check; no plan operation. | Optional plan exposes the assembly consumed by check, with explicit blockers. | Same plan/check/merge paths; the new feedback section directs dirty/staged-only work away from this clean-candidate operation. No duplicate check-before-merge step. |
| S6: Inspect release/history behavior without accidental publication | Relevant release/tool source must establish inspection effects. | Publication concern documents local/hosted/ref/object effects. | Same operation and publication boundary. Capability output clarifies prerequisites, not hosted readiness or a new release protocol. |

Relevant source bounds reinforce that this is not a text-shrinking claim.
Prepare-a-clone text is 25 lines in A and 24 in B; C has 29 plus a 13-line
prerequisite section. Local-verification procedure is 49 relevant lines in A
(excluding its unrelated 44-line overlay subsection), 57 in B and 63 in C.
C adds the 21-line dirty/staged/candidate route. Extra text buys explicit
subjects and prerequisites; no time or token saving follows from those counts.
The repository status file gains one current summary above preserved historical
checkpoints. Domain status history remains owned by its domain.

## Implementation and actual parser smoke evidence

The hook exports the index once only when a quick Unix-like unit is selected,
then runs the staged implementations from that tree. It clears inherited
repository-routing variables in the child. The snapshot has no Git metadata;
there is no stash, reset, new commit, copied mutable index or worktree rewrite.
Global scans and evidence logging stay in the caller's original Git context.

The existing scripts really run without Git metadata: on Linux x86_64, the
materialized 568-path source occupied 4,948 KiB, exported in 0.144 seconds,
and real format/lint/payload commands exited 0 in 1.807/0.769/1.282 seconds.
These single smoke timings were collected alongside a fixture run and are
illustrative execution observations, not benchmark samples. The checks use
the domain's existing locked tools. This proves current quick-check packaging
and parser execution, not the full provider suite, host closure, Windows/macOS
runtime, hosted CI, activation or Apply.

## Source-preparation review, checks and delivery limits

At the completed uncommitted checkpoint, physical line deltas against B
included new files and blank lines, with each path counted once. These costs
exclude the later local-adoption record and are separate from the timing sample:

| Category | Net lines |
| --- | ---: |
| Production hook/capability implementation | +40 |
| Tests and runners | +234 |
| Operating documents, status and invariants | +79 |
| This spec and report | +266 |
| Total | +619 |

The outcome grows source to correct a proven gap and retain a reproducible
case. Most growth is regression/evidence material; it is not a reduction in
repository size or proof of lower maintenance cost. Further navigation engines,
capability schemas, caching and history cleanup lack evidence in this case and
are outside the completed correction.

The author read the new invariant's positive and negative cases and the final
diff for scope, source subjects, bare account/machine identity, authorization
boundaries and accidental startup requirements. This was author review, not an
independent reviewer result. No installed plugin or model role became required.

Repository checks use an alternate index containing this complete source,
including new files, while leaving the user's actual index unstaged. Scope
classification is repository only. Invariants report 83 registered, zero
pending and zero untagged fixture units. Records, design citations, domain
reads, desired-state hygiene, provisional registry and staged work checks pass;
so do staged secret/diff checks, shell syntax and Python parsing. The work
pair also passes its explicit working-tree check. The final source remains
based on B and the primary master checkout remains clean at B. No source
commit, integration, push, tag, input update, activation or Apply occurred.

The retained production increase is bounded to hook snapshot orchestration
and capability presentation. Existing domain scripts, CI dispatch and native
verification semantics are unchanged. Documentation grows to name source
states and prerequisites; the additional test runner is retained regression
coverage, not a new guide engine, provisioning system or persistent receipt.
Snapshot export adds a temporary copy for selected domain checks and no copy
for repository-only work. The six reconstructed routes justify clarity and
correctness claims; repeated future task observations are needed to assess
agent navigation time, token use or question frequency.

## Authorized local adoption — 2026-11-06

After accepting the completed correction, the maintainer explicitly requested
local commit, master integration and cleanup. The source-preparation boundary
and measurements above remain their original checkpoint. The selected base is
`53a3f7e09aa1e217567941c884e87f1af56de270`; the source commit containing this
record and its exact-base/head no-ff integration are identified in Git history.
Integration executes the tracked verification itself. Workspace removal uses
the exact reviewed tip and preservation inventory; topic deletion additionally
requires reachability from master. No push, tag or deployment is authorized.
