# Master release branch with optional topics and workspaces

date: 2026-11-02
scope: repository
status: accepted
supersedes: docs/policy/decisions/repository/local-development-workflow.md
source: docs/work/repository/master-topic-workflow/spec.md

## Decision

Master is the release and ordinary development branch. A single logical
commit normally stays there; a selected linked workspace also uses a topic.
Estimate the work before editing: when one coherent
outcome needs several logical commits, start a same-scope topic from master
and retain the group through a no-ff merge into master. Worktrees are optional;
agents ask the user whether to use the current checkout or a linked worktree.
Keep an existing choice when continuing the same task. Parallel authors need
isolated workspaces. Never infer a user's workspace
choice or Git mutation permission from a tool allowlist.

Dev is retired from the operating model. Preserve existing refs and published
objects until separately authorized retention review; do not rewrite history.
There is no source promotion step. Master commits and merged topics are
accepted source; domain publication and deployment remain separate decisions.

## Mechanical operation

Tracked repository tools expose start, inspection, effect-selected checks and
exact-base/head no-ff integration. Start requires explicit scope, estimated
commit count and workspace choice. A tool cannot determine logical scope or
whether a human answered, so those decisions remain user/agent procedure.
Merge checks clean state, full source identities and current master ancestry;
changed bases or failed/unavailable checks stop it. No helper implicitly
fetches, commits source edits, pushes, publishes or prunes. Merge is an explicit
commit-producing operation and requires authorization.

Shared operating values live in `tool/version-control/policy.json`, validated
by its repository-owned reader. Operator tools, hooks and remote audit consume
that declaration. Workflow-only wiring lives in tracked CI YAML without a
second JSON copy. Agents use `tool/configs policy show` and the tracked
operator commands; private skills, memory, shell configuration and installed
plugins contribute no project obligation or approval. Human judgements remain
explicit: logical scope, size estimate, workspace answer and mutation approval.
Start records its inputs/base in the workspace's Git administrative directory;
inspect reports this record alongside actual Git state. It is execution data,
not approval, process liveness or cleanup eligibility. Missing data is unknown.
Verification prints source identities and proof rather than persisting another
work-record receipt. Merge verifies the candidate itself; a prior check is
optional and supplies no cached permission.

CI runs on master pushes, optional PRs and explicit candidate dispatch from
accepted master tooling. Hosted proof is read live for a run ID and must bind
successful workflow/gate/artifact to exact base, head, tree and event. Local
index scans still run; selected suites may use that proof. No PR is needed for
ordinary work or candidate native checks. Direct master writes have no PR or
status admission. The bounded input patch retains its PR-based proof/recovery
as an explicit automation contract. Ordinary pre-push rejects non-fast-forward
updates, including forced refspecs, without trusting an agent approval flag.

## History maintenance exception

Force pushes remain denied to ordinary credentials. An optional dedicated
maintenance App alone may bypass the non-fast-forward restriction on master.
Default classic protection keeps force disabled. An approved adoption first
installs an active exact-master non-fast-forward ruleset with only that App
in its bypass list, then enables classic force behind that ruleset. This
supports a personal public repository without relying on organization-only
classic bypass actors. Deletion and administrator enforcement stay active.
The executor audits the combined effective protection and refuses unknown or
inherited rules; it does not change settings. Its private key
exists only in the `history-rewrite` environment with explicit human reviewers
and administrator bypass disabled, restricted to the exact master branch; ordinary agent/CI credentials must not have
that capability. The tracked manual workflow displays immutable old/new SHA
and reason, uploads a verified recovery bundle before execution, and releases
the writer credential only after approval. The executor rechecks live run,
review, App identity, exact source, recovery and the expected-old lease. Reruns
cannot reuse approval. Published tags and their master ancestry are preserved.

The executor never edits protection and never uses naked force, deletion or
tag replacement. Confirm actual remote result after an ambiguous response.
Preserve recovery; do not retry against another old SHA without a new reviewed
dispatch. Owners able to change GitHub permissions remain an administrative
trust boundary: repository scripts are not an OS or credential sandbox.
If the App/environment is absent or cannot be verified, the exception refuses;
there is no local boolean or private agent approval token that enables it.

Workspace removal uses the same public preservation review for all operators:
refuse primary checkout, unknown/non-topic workspace, unreviewed head, commits
not preserved by the exact retained topic ref or optional verified recovery,
tracked/untracked/ignored data, and an unfinished Git operation.
A recovery bundle is independently restored and checked for complete object
integrity. Retain the branch and never force-remove. Preserve flagged data explicitly
before trying again. Scratch-space presence blocks removal without reading it.

## Retained boundaries

Keep scope-pure source commits, Conventional Commits, isolated lock updates,
secret/hygiene scans, useful checkpoints, explicit preservation review and
immutable domain tags. The bounded Unix-like input patch still starts from
published master, uses its checked PR and exact merge proof, separates writer
credentials and recovers missing immutable publication. It is an automation
path, not a general source admission exception. It defers while a master PR
is open. No Windows publication or host activation is added.

## Adoption

Source preparation changes no remote setting or credential. Ordinary direct
master adoption and the optional maintenance App/environment require separate
explicit remote authorization and verification. With no maintenance adoption,
master force pushes stay disabled. With it, the exact App allowlist and approved
credential release are audited. No general PR admission or dev cleanup is added.
Old dev-era records remain historical; deleted compatibility tools supply no
alternative workflow. Actual hosted/native/approval evidence stays distinct
from fixture proof. The repository contract is sufficient without agent-local
operating context.

## Simplification — 2026-11-02

The maintainer requested implementation with independent agent review. Use
workflow start as the sole workspace creation path and keep worktree commands
for listing and preservation review/removal. Check selection has commit and
CI stages; pre-push audits transmitted history without a separate selection
stage. Optional session tooling saves and inspects plain handoff text, with
atomic nonempty writes and no lifecycle state or model identity. Existing
notes are preserved until explicitly replaced. Tracked project documents
remain the authority; these notes and start records supply no private policy.

Keep the configuration-editing commit helper and its hooks, exact-source CI
and merge checks, independent recovery restoration and isolated approval
capability. Share only CI artifact format parsing; release publication retains
its narrower accepted events and writer proof. Tests still check shared writer
serialization and secret/environment wiring declared in CI YAML.

## Final review corrections — 2026-11-02

The maintainer authorized reuse of topic ownership and source-range checks
between local and CI paths. Windows CI runtime-governance changes require
exact hosted evidence; local domain tests retain their narrower meaning.
Candidate token permissions are explicitly read-only and checkout credentials
are not persisted. Scope growth uses an authorized in-place topic transition;
existing master commits are retained and only remaining work is grouped.

Removing a worktree retains and verifies its exact topic ref, so it needs no
mandatory external archive. Branch or clone deletion remains separate.
Approved maintenance uses the supported branch ruleset capability described
above and declares its minimum API grants. Its actual hosted adoption is still
pending; fixtures never stand in for remote approval or permission evidence.

## Agent context — 2026-11-02

The maintainer requested a minimal non-mechanical contract. Agents read current
guidance relevant to the task and use repository tools for deterministic
decisions. Continuing work retains its workspace choice and explicit operation
authorization; scope changes require the missing decision, not a repetition
of approvals already given. Staged-only instructions still prohibit commits.
Fresh operation-specific history-maintenance approval is not reusable.
Capability discovery is conditional on the capability needed; start initializes
clean new work and is not a resumption requirement.

Role splits, plugins, issues, ordinary PRs and local handoff files are optional.
Sustained work uses the existing spec/report format; small clear changes use
concise results. Only applicable review items are read, and mechanical checks
need no duplicate manual execution. Candidates hold unaccepted observations;
explicit maintainer decisions and factual corrections proceed directly through
the owning scope. This clarifies candidates-observed-before-adoption.md.
Permission adapters and exit-state libraries do not attest human consent,
evidence sufficiency or isolation. Existing approval and preservation boundaries
remain in the tracked procedure and its enforcement.
