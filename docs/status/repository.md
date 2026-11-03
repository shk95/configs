# Current state: repository

## Remote master/topic adoption — 2026-11-03

PR #579 installed the accepted source and hosted-portability corrections through
the existing protected admission path, merging as
`d1a3093e68b84ab456480beb554db8ba8a8e0d61`. CI run 41577858716 passed
all selected repository, Unix-like and native Windows jobs and Required checks.
The exact base/head/tree check accepted that hosted evidence.

The maintainer-authorized protection migration removed mandatory PR, status
check and conversation admission. Administrator enforcement, force-push and
deletion denial, and merge-commit-only PR settings remain active. The live
`tool/configs audit-remote` passed after migration. Local master was advanced
without rewriting accepted history. Earlier pending-adoption statements below
record preparation checkpoints rather than current protection state.

Optional history-maintenance App adoption and actual bounded patch-writer
qualification remain separate; no App, credential, tag, host activation or
Windows Apply was performed. PR #578 remains a separate input patch. No related
open issue required closure. Master-push CI reports its own tested revision.

## Local acceptance — 2026-11-02

The maintainer accepted the completed policy redesign and authorized its local
commit after verification. The staged-only descriptions below record preparation
checkpoints; the resulting source revision is recorded in Git. Remote adoption
and publication remain pending.

## Master/topic source preparation — 2026-11-02

The maintainer selected master as the release and ordinary authoring branch,
optional topics for several logical commits with no-ff integration, and an
explicit user choice of current versus linked workspace. The source contract
is docs/policy/decisions/repository/master-topic-workflow.md. Tracked workflow
commands carry start, inspection, check selection and exact-source integration.

This change is prepared and staged only, at the maintainer's request. No source
commit, topic integration, push, remote protection change, dev deletion, tag or
host activation is performed. Existing local master already contains all dev
source; this topic starts from that master without rewriting history.

Remote adoption remains pending: install the source on master through the
currently protected admission path with explicit authorization, then explicitly
migrate master protection to ordinary direct writes while retaining administrator,
force-push/deletion and merge-method safeguards. Run the read-only remote audit,
confirm master-push/topic-PR CI and qualify patch automation. Retain dev until
separately authorized preservation review. Do not bypass current protection.
Local fixture proof is not actual GitHub adoption or publication evidence.
See docs/work/repository/master-topic-workflow/report.md for verification.

## Final review corrections — staged preparation

The prepared source now shares topic ownership validation between local and
PR paths and audits incoming commit ranges in CI. CI tokens are explicitly
read-only with no persisted candidate credentials. Windows runtime-governance
changes require exact hosted native proof. Scope growth has an in-place
transition that preserves existing master commits and uncommitted work.

Worktree removal accepts and verifies the retained exact topic ref without
requiring an external archive. Approved history maintenance now uses the
public personal-repository branch-ruleset path with isolated App bypass,
minimum API grants and a read-only preflight. Unknown effective protection
still refuses. No actual ruleset, App, credential, protection or remote ref
is changed; hosted qualification remains pending.

The final corrected combined suite passes: 13 workflow, 17 mechanics and
21 release cases plus existing policy, handoff and retirement fixtures.
Actionlint, Python/shell checks, 80 invariants and staged policy/secret/diff
scans pass. This is source-preparation evidence with simulated API/receivers;
it does not certify actual hosted approval, App visibility or deployment.

## Mechanical follow-up — earlier staged checkpoints

Agent context is also simplified in the prepared source. Continuing work keeps
its workspace choice and explicit task authorization; capability discovery and
new-work initialization are conditional. Role/plugin orchestration and local
handoff files remain optional. Current guidance corrects isolation topics,
classifier/evidence limits and adapter permission claims, and review checklists
apply only to the requested scope. Executable behavior, permission allowlists,
fresh maintenance approval and preservation boundaries are unchanged.
Two independent reviews and staged policy/secret/diff checks pass, including
all 9 manual evidence references. Earlier combined fixture results apply to
unchanged executable mechanics; this context-only follow-up did not rerun
those suites or perform remote adoption.

Independent simplification review retained approval, exact-source CI/merge and
preservation boundaries. The current source removes unused push selection,
duplicate worktree creation and persisted verification receipts. Start records
remain inspectable; session tooling saves/inspects plain handoff text without
lifecycle state or Codex identity. Workflow-only secret/concurrency wiring
stays in CI YAML with cross-workflow safety assertions. Configuration-editing
commit helpers remain; only unused bookkeeping is removed. CI artifact parsing
is shared without changing release-specific admission. This source remains
staged preparation, not remote adoption. The final combined fixture suite,
80 invariants, Python lint, shell syntax and staged policy/secret/diff scans
pass. Earlier verification below records the pre-simplification checkpoint;
the work report carries the final proof and evidence boundaries.

The same current checkout now prepares a validated policy.json, inspectable
Git-local work records, preservation-safe worktree review/removal, candidate CI
dispatch with live exact-source proof, and an approved isolated-App maintenance
workflow. Legacy linked-worktree/promotion tool names are removed. General
work needs no PR; bounded input patch PR proof remains unchanged.

Actual remote settings observed in the prior read-only review still require
PR/strict checks and deny force/deletion, applying to administrators. No new
remote writes, environment, App credentials, approval or maintenance run are
performed by this source preparation. Default force denial remains until the
separately approved App/environment adoption. Never expose the dedicated key
to ordinary agent sessions. GitHub owner/admin authority remains outside the
script enforcement boundary.

Local combined verification passed: 7 workflow cases, 13 mechanical cases,
21 release cases, 80 registered invariants, policy scans, secret scan, lint and
workflow syntax. This certifies staged repository source and local fixtures;
it does not certify actual hosted CI, approval, App installation or protection
migration. The complete report carries the evidence and remaining boundary.

## Historical adoption checkpoints

The following sections retain earlier snapshots and are not current operating
instructions. In particular their dev topology, worktree mandates and preparation
state are superseded by the source contract and adoption boundary above.


## Local workflow redesign

The adopted direction is local development completion with later optional
push and protected master acceptance:
docs/policy/decisions/repository/local-development-workflow.md.
Implementation and evidence are recorded in
docs/work/repository/local-development-workflow/report.md.

The separate first-parent lanes continue from dev 0fc573e and master 81229c1.
The accepted Unix-like input patch/tag at master 60bcd46 is retained. Master
synchronization uses a dev-based no-ff merge; dev continues on its own lane
after protected master promotion. The backup conditional merge, base-drift and
qualification flow is not an active dependency. Cancelled workspace history
and uncommitted extraction data were preserved in verified recovery archives
before cleanup; Agent Rack is outside this redesign. Historical reconstruction
and host evidence are not rewritten.

## Remote adoption

On 2026-10-07 the maintainer-authorized cutover replaced old remote dev
b8e9273 and master 6c60f37 with the reset-based candidate and master basis.
The initial promotion through [PR #546](https://github.com/shk95/configs/pull/546)
passed its selected native jobs and Required checks, but its topology advanced
dev onto the master lane. That topology was superseded by the maintainer's
history-only correction through [PR #547](https://github.com/shk95/configs/pull/547).
The corrected merge 8698a8b has first parent 60bcd46 and second parent 4e6cd4a.
Its exact-source CI and Required checks passed, and actual merge parents/tree
were confirmed. At that transition both branch trees exactly matched their
pre-correction trees, published tag objects were unchanged, and dev continued
on its own lane. Subsequent master synchronization follows the amended procedure.

Dev protection now permits ordinary push without PR/required checks or
conversation resolution. Master retains strict Required checks and protected
merge-commit PRs with zero required approvals. Both enforce administrators
and prohibit everyday force pushes/deletion. Automatic and manual input patch
operation and its schedule are enabled again; the 2026-10-07 source promotion
itself certified neither a new patch publication nor an actual scheduled
trigger. On 2026-10-11, the enabled schedule completed a permitted-input
refresh and writer run (#38171470068), producing PR #554. Its selected
Unix-like CI and Required checks passed; the protected merge is 219c3e8 with
the immutable unixlike-v1.0.7 tag. Follow-on run #38172240020 succeeded. This
is actual schedule-path evidence; it does not certify host activation or Apply.

Cancelled conditional-merge/qualification issues and PRs were retired. Related
topic/backup/reconstruction branches and worktrees were reclaimed after a
verified recovery archive preserved their history and dirty/checkpoint data.
Current remote facts are checked explicitly for remote operations, not cached
as prerequisites of local development. Operational documentation can complete
on dev without another immediate master promotion.

## Input patch and domain boundaries

The independent master-based automatic/manual input patch function remains.
It refreshes only inputs from unixlike/automatic-refresh-inputs.json, validates
the exact PR/merge and preserves immutable tags and original publication
recovery. General development, Windows publication and host activation/Apply
are separate. Manual qualification never proves the scheduled trigger.

Domain ownership and current host/native evidence remain in the domain status
files. A repository change has no configuration output or domain release tag.

## Work-role source separation

On 2026-10-07 the maintainer requested Codex-only extraction into Agent Rack's
existing Work Cycle package. The prepared configs worktree removes six tracked
role skills, one Claude workflow adapter and two command aliases. Policy,
contributor procedures, tools, hooks, CI and native checkpoint behavior remain
project-owned and usable without an installed replacement. Local ignored
Context Bridge data is preserved. Existing Claude instruction and permission
files provide no replacement plugin connection.

Agent Rack's previous extraction was remote-first and referred to retired
conditional integration behavior. Its 0.3.0 source preparation refreshes the
six roles from configs 4c72b000ad23b2a32c564c6f907192bd34f82870, retains
historical imports and defers Claude packaging. Publication, installation,
actual installed-host discovery and consumer adoption have not happened.
The maintainer subsequently authorized committing and integrating the configs
result into local dev. Agent Rack's separate source changes remain uncommitted;
external distribution and consumer adoption are separate operations.
See docs/work/repository/codex-work-cycle-extraction/report.md for evidence.

## Provider verification connection

The 2026-10-13 prepared connection uses one Unix-like provider suite in CI and
local checks. Automatic Unix-like annotations report focused artifact build
evidence and mark host native runtime not applicable. The connection depends on
the Unix-like provider-verification worktree; neither set of source edits is
committed or integrated yet. Existing tag annotations remain unchanged.

Independent review corrections passed locally on 2026-10-13. Existing complete
prior-format publications are recognized without writes; new-write confirmation
remains current-format-only. Twenty-one release fixtures cover this boundary.
No remote CI or publication was performed by this adjustment.
