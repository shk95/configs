# Agent workflow verification
kind: report
spec: docs/work/repository/agent-workflow/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review: independent agent scenario review of the five role skills, routing skill, procedure and session tool at source d899f9d. Broad implicit intent, scope drift, interrupted owner, recovered PR workspace, changing admission head and competing lane pickup were traced. Five findings were fixed and re-reviewed; no live merge was performed. |
| AC2 | verified | Policy checks: commit hooks at b72e497 and d899f9d passed work pairing/amendments, records, design citations, invariants, hygiene and provisional checks. Review: same-scope outcomes span evidence lanes; standalone plans and small direct work are allowed; plan and execution revisions are distinct; roadmap separates current, deferred and historical outcomes. |
| AC3 | verified | Fixtures: session-test and the full version-control suite passed locally and in CI run 36222560670 at source d899f9d. Primary-checkout refusal, duplicate start, empty handoff, active replan refusal, suspended replan and preserved resumption, valid delivery, abandoned resume refusal, stale write lock refusal, recovered head with unknown base and symlink refusal were exercised. |
| AC4 | verified | Review: independent scenario review closed all five findings. Current GitHub dev protection was read on 2026-09-26: strict Required checks, PR required with zero blanket approvals, administrator enforcement, conversations resolved, no force push/deletion. Existing auto-merge requests must be cancelled before worker repair; default integration is an immediate expected-head GitHub merge. Native stacks remain unsupported pending separate production verification. |
| AC5 | verified | Review: scope-owned follow-ups are PR #413 (CI selection), #415 (Unix-like internal efficiency) and #414 (Windows timing). Baselines and retained guarantees appear in their reports. Windows has no demonstrated safe test deletion or speedup. Post-merge reuse and native-stack admission are explicitly deferred; neither is implemented optimistically. |
| AC6 | verified | Fixtures and policy checks: [CI run 36222560670](https://github.com/shk95/configs/actions/runs/36222560670) passed Required checks at source d899f9d, including the new checkpoint suite. Local commit and push hooks passed with audit reporting zero warnings/failures. PR #416 is kept Draft until its final delivery head passes again; that final-head result is preserved on the PR. |

## Delivery

[PR #416](https://github.com/shk95/configs/pull/416) delivers the operating
contract and local checkpoint support. Integrate it before
[PR #413](https://github.com/shk95/configs/pull/413), then the independent domain
follow-ups [#415](https://github.com/shk95/configs/pull/415) and
[#414](https://github.com/shk95/configs/pull/414). Their own reports hold their
scope-specific evidence; this report does not promote another domain's results.
The implementation branches may be prepared in parallel; adoption starts only
when the corresponding PR enters dev. No dev merge or auto-merge was requested.

A read-only merge-tree check of d899f9d with the CI branch at 68cca356 reported
no textual conflict. This is not combined CI evidence. The integration session
must re-query exact heads, base and requirements before each admission and ask
the relevant worker for an update only when necessary.

## Review and recovery evidence

The independent reviewer identified and then confirmed fixes for:

- an outstanding auto-merge request admitting a later worker head;
- picking up an apparently free lane without an explicit assignment;
- resuming a recreated worktree without its deleted local checkpoint;
- retaining stale plan metadata or losing the replan handoff on resume;
- a hard-killed checkpoint writer leaving an unexplained local write lock.

The checkpoint stores execution context only. Replan updates the reviewed plan
revision/content digest; recover records a recovered start head and does not
invent an original base. The local write lock is not an integration lock.
Resume command syntax was checked against the installed Codex CLI help. The
bundled Python skill validator was unavailable on this host; Ruby YAML parsing
checked all six skills' metadata and the independent scenario review checked
behavioral instructions. No model-specific policy copy was introduced.

The hook initially found literal synthetic work paths in the new fixture;
constructing those paths from their area root fixed the fixture without adding
an exception to the design-citation checker. The final suite and hooks passed.

## Remaining operational limits

- Role adherence and lane assignment are agent procedures, not OS isolation or
  an atomic multi-planner claim protocol. One planner assigns a lane; conflicting
  claims stop implementation. Protected dev enforces remote PR/check admission.
- A local active marker or PID does not prove liveness. Operator-confirmed
  ownership and preservation of partial data precede stale-lock recovery.
- Reclaim is an assessment by default. Explicit deletion authorization and
  checks of unpushed, untracked and ignored data precede non-force removal.
- Legacy explicitly confirmed human publication helpers retain their contracts;
  workers do not invoke their auto-merge behavior.
- No GitHub settings changed. There is no required manual setting change for
  this first delivery. Risk-specific CODEOWNERS needs real reviewer identities
  and a separate review decision; no blanket review bottleneck was introduced.
- Merge Queue is not used. The native-stack lab is not certification of this
  repository; CI follow-up rejects unsupported stack events rather than losing
  lower-layer coverage. Sequential prerequisite-first PRs remain available.
- The initial CI optimization removes irrelevant documentation-triggered
  platform suites but keeps executable/platform input coverage conservative.
  Safe cross-run validation reuse is not established; post-merge checks remain.

No release, activation, Windows Apply, deployment or source promotion evidence
is claimed. The maintainer's separate integration session owns dev admission.
