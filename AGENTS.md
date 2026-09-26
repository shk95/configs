# Repository guidance for agents

## Goal and authority

This repository contains three deliberately separate configuration domains:

- `unixlike`: Linux, WSL, NixOS, and macOS configuration evaluated by Nix.
- `windows`: native Windows desired state evaluated and reconciled on Windows.
- `common`: explicitly platform-neutral material with no host deployment of its
  own.

The domains share a repository for discovery and history, not one composition
authority or one release train. The flake is authoritative only for the
Unix-like domain. The Windows domain must become independently authorable,
testable, and deployable without a Unix-like host. `common` is an exceptional
domain: do not create common material merely because two implementations look
similar.

Repository-wide version-control policy, hooks, CI dispatch, and reusable agent
workflows form a `repository` governance scope. This is not a fourth
configuration domain, has no host output, and receives no domain release tag.
Use it only when one configuration domain cannot honestly own the change.

The Unix-like domain owns one tree, `unixlike/`, and everything the classifier
answers `unixlike` for lives under it, except `.envrc` and the `Justfile`,
which stay at the root because direnv reads the first there and where the
second belongs is a separate decision, and the domain's documents, which
live in the Unix-like scope directories under `docs/`. Files below `unixlike/modules/` are
flake-parts modules collected by import-tree. The first level groups concerns
as `flake`, `machines`, `platforms`, `foundation`, `desktop`, and `programs`.
Inside a group, a concern with one fragment is one file, and a concern with
more, or with a payload or a script beside it, is a directory. The class a
fragment reaches is read in the file that writes it, never from its directory.
`unixlike/modules/flake/configurations.nix` is the only place that decides
which deferred module classes reach a Unix-like host.

## Domain boundaries

- Classify a change as `unixlike`, `windows`, or `common` before editing.
- Classify root version-control governance as `repository`; do not use that
  scope for configuration or deployment behavior.
- Keep a change inside one domain unless transfer between domains is the
  explicit purpose of the work.
- Do not introduce implicit imports, generated dependencies, or shared mutable
  payloads across domains.
- Do not recreate plugin or addon discovery between repository domains.
- Prefer two locally understandable implementations over a cross-platform
  abstraction.
- Copying from another domain is allowed and preferred to premature sharing.
  Once copied, the destination owns the copy and may diverge.
- Put genuinely common material only under an explicit `common/` boundary.
  Common material needs its own contract and checks, is versioned independently,
  and is never deployed directly to a host.
- A platform adopts common material through an explicit, reviewable import or
  copy on that platform's schedule. A common change must not silently alter a
  platform output.

See `docs/policy/architecture.md` for the complete ownership, versioning, and
deployment model.

## Rules that are expensive to break

Absolute rules for a session. Each names what enforces it; `none` means the
rule stands on this sentence alone.

| Rule | Why | Enforced by |
| --- | --- | --- |
| Never activate Home Manager, NixOS, or nix-darwin without an explicit request. | Activation changes a host; evaluation and build evidence never imply permission. | none |
| Never run Windows `Apply` without an explicit request. `-Check` is the read-only path. | The same boundary on the Windows side. | none |
| Do not commit, push, tag, rewrite history, or change branches unless the user explicitly requests it. | A tool allowlist reduces prompts; it never authorizes a mutation. | skill (`run-version-control-workflow` refuses); `tool/version-control/commit` refuses on `master` |
| Author tracked source changes and commits in a linked worktree dedicated to the task. Keep the primary checkout for read-only inspection and integration. | A task's edits must not disturb the integration checkout or another task's index. | tool (`tool/version-control/require-linked-worktree` refuses commits from the primary checkout); fixture |
| Do not update flake inputs, change login shells, garbage-collect Nix stores, shut down WSL, or change global Git configuration unless the task calls for it. | Each is host-global or irreversible from inside a session. | none |
| Treat WSL cgroups, binfmt_misc, mounts, and similar kernel-global resources as shared by every distribution, and the kernel under an OrbStack machine as shared by every machine and by OrbStack's container engine. | One distribution's fix is every distribution's change, and an OrbStack machine's UIDs are mapped one to one: its root is UID 0 on that kernel. | none for WSL; schema for an OrbStack machine's binfmt registry (`INV unixlike/orbstack-shared-kernel`) |
| Preserve externally managed PowerShell profile blocks. Do not change Windows OpenSSH DefaultShell or add a `.wslconfig` firewall value without explicit direction. | Both are host state another owner writes. | none |
| Classify a change before editing and change only the owning domain. | Evidence, release tags, and CI jobs are selected by ownership. | hook (`tool/version-control/classify` refuses an unclassified path) |
| Report evaluation, build, native runtime, and activation or Apply evidence separately, and never upgrade partial evidence. | A tag or a merge is only as true as the lane it names. | `.githooks/evidence`; skill |
| Register a temporary measure under `docs/provisional/` in the change that adds it, tag every disposable line `PROV <scope>/<slug>`, and retire it by deleting the entry and its tags together. | A measure with no exit condition and no review date becomes permanent by neglect. | tool (`tool/version-control/provisional`) |

## Where invariants are enforced

Codebase invariants — what must remain true of committed desired state and
tooling — are enumerated under `docs/policy/invariants/<scope>/`, one file each. An entry
states the rule without naming a command, cites its rationale in
`docs/policy/architecture.md` or this file, and declares its enforcement as
`schema` (an evaluator or loader refuses it), `tool` (a script refuses it),
`fixture` (a test proves both directions), `manual` (a reviewer evidence item
in `docs/policy/definition-of-done/<scope>.md`), or `pending` (an issue, until a check
exists). `tool/version-control/invariants` checks in both directions that
every declaration exists and names its invariant, on every commit and in CI.
Read the classified scope's list before editing that scope.
`docs/policy/invariants/README.md` is the format.

## Governance design

When adding a repository rule, separate its concerns before implementation:

- Put durable rationale in `AGENTS.md` or `docs/policy/architecture.md` and the
  invariant itself in `docs/policy/invariants/<scope>/`. State what must remain true
  without depending on a particular command, product, or model.
- Put human-operable prerequisites, ordered steps, recovery, and authorization
  boundaries in `CONTRIBUTING.md`.
- Put repeatable agent orchestration in a canonical `.agents/skills/` skill.
- Put deterministic classification and enforcement in `tool/`, hooks, CI, and
  remote repository settings.
- Give repository operators one documented command entry point. Hooks, CI and
  implementation scripts call the underlying tools directly; a test may call
  the entry point to prove its public contract. Keep each configuration
  domain's operator commands and implementation inside that domain's boundary.
- Put current adoption state and migration gaps in `docs/status/<scope>.md` and
  expensive choices in `docs/policy/decisions/`; put per-run proof in CI, pull
  requests, and release evidence.
- Put a rule that has been observed but not accepted, and a document or tool
  judged stale, in `docs/policy/candidates/` until recurrence or silence decides it.
  A candidate is an observation and never a source of authority.
- Put the plan for a piece of work and its verification in `docs/work/`,
  outside the authority model: a spec with its acceptance criteria and the
  evidence lanes each requires, a report that answers every criterion, and
  optionally the study that argued the direction. A work document binds only
  the work it describes. A durable rule it produces belongs in a decision
  record or invariant; a temporary measure belongs in the provisional
  registry. A decision record or provisional entry may name the work as its
  source. Other rule-bearing material cites the adopted result
  (`INV repository/design-outside-authority`). An agent reads a work item
  when a task, an issue or a record points at it, never as a rule to follow.

Each obligation has one authoritative source. Procedures and tools implement
policy but must not silently create new policy. Model-specific adapters only
discover canonical skills. Every enforceable invariant needs positive and
negative fixtures, every fixture names the invariant it proves and a fixture
that proves none is removed, and non-automated invariants need an explicit
evidence item and named decision owner.

Extract a method into the sibling `skills` project only when it contains
no repository decision, path convention, branch name, infrastructure identity,
or current state. Keep project policy and enforcement here. Adoption of a
shared skill is explicit; product-specific adapters never become its authority.

For source promotion, only the same repository's `dev` branch may enter
`master`. Use a pull request and a merge commit; never commit, cherry-pick,
squash, or rebase directly into `master`. Promotion accepts source history but
does not certify a domain release or authorize deployment. Do not merge
`master` back into `dev` merely to carry a promotion merge commit. The
repository maintainer owns promotion decisions. There is no operational
bypass; change this policy through the governance workflow before deviating.

Work is planned and verified in documents, and issues hold execution state.
Work with more than one acceptance criterion or more than one pull request
has a spec and a report under `docs/work/<scope>/<slug>/`, created in the
same commit; any other change is a single pull request whose body carries
its evidence. An execution issue names its spec, holds the increments as a
checklist, carries no acceptance criteria and is never a source of evidence;
it closes from what the report says, and no commit message or promotion body
carries a closing keyword (`INV repository/no-closing-keyword`).
`docs/work/roadmap.md` states lanes and order, not schedule. GitHub
milestones are not used. A branch is one reviewable increment — one issue,
or what one judgement covers — cut from `origin/dev` and merged through one
pull request when it is complete and green. An increment of a spec is what
one evidence lane verifies, and the report rows, status and report end that
verification produces travel in the same pull request, so a spec takes as
many pull requests as it has evidence lanes and scopes, not as many as it
has steps (`INV repository/pull-request-spans-an-evidence-lane`). Neither a
finished report nor a closed issue certifies a domain release or authorizes
activation or Apply. The repository maintainer owns the roadmap and the
decision that a report is done.

## Working contract

1. Read `CONTRIBUTING.md`, `docs/policy/architecture.md`, `docs/policy/invariants/<scope>/` for
   the classified scope, the scope's current state in `docs/status/<scope>.md`, and
   every decision record those entries and that state cite.
2. Classify the task as `unixlike`, `windows`, `common`, `repository`, or an
   explicit transfer.
3. Use `tool/configs doctor` before relying on host-local capabilities.
4. Change only the owning domain. Treat a cross-domain copy as a separate,
   reviewable adoption change.
5. Run narrow domain checks before broader checks. Do not require an unrelated
   domain to pass merely to validate the changed domain.
6. Report evaluation, build, native runtime check, and activation or Apply
   evidence separately for each affected domain.

User-facing usage belongs in `README.md`, workflow in `CONTRIBUTING.md`,
architecture and ownership in `docs/policy/architecture.md`, current state in
`docs/status/`, decisions in `docs/policy/decisions/`, recurring symptoms in
`docs/reference/troubleshooting.md`, invariants in `docs/policy/invariants/`, plans and
their verification in `docs/work/`, and executable policy in `tool/`, hooks, and CI.
`docs/README.md` maps the document tree; a document is owned by the scope
directory, or the scope-named file, that holds it.
Canonical project-specific agent workflows live under `.agents/skills/` and
follow the Agent Skills open standard. Reusable
cross-project methods live in the separate sibling `skills` project.
Model-specific context and skill files only point to canonical sources.

`notes/` is untracked maintainer scratch space. It is free-form by design and
carries no structure, review, or retention promise, so it states no policy and
records no decision. It is not project context: do not read, search, summarise,
or act on anything in it unless the user names a file inside it.
