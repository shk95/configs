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

Files below `modules/` are flake-parts modules collected by import-tree for the
Unix-like domain. Prefer one feature per file.
`modules/flake/configurations.nix` is the only place that decides which
deferred module classes reach a Unix-like host.

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

See `docs/architecture.md` for the complete ownership, versioning, and
deployment model.

## Rules that are expensive to break

Absolute rules for a session. Each names what enforces it; `none` means the
rule stands on this sentence alone.

| Rule | Why | Enforced by |
| --- | --- | --- |
| Never activate Home Manager, NixOS, or nix-darwin without an explicit request. | Activation changes a host; evaluation and build evidence never imply permission. | none |
| Never run Windows `Apply` without an explicit request. `-Check` is the read-only path. | The same boundary on the Windows side. | none |
| Do not commit, push, tag, rewrite history, or change branches unless the user explicitly requests it. | A tool allowlist reduces prompts; it never authorizes a mutation. | skill (`run-version-control-workflow` refuses); `tool/version-control/commit` refuses on `master` |
| Do not update flake inputs, change login shells, garbage-collect Nix stores, shut down WSL, or change global Git configuration unless the task calls for it. | Each is host-global or irreversible from inside a session. | none |
| Treat WSL cgroups, binfmt_misc, mounts, and similar kernel-global resources as shared by every distribution. | One distribution's fix is every distribution's change. | none |
| Preserve externally managed PowerShell profile blocks. Do not change Windows OpenSSH DefaultShell or add a `.wslconfig` firewall value without explicit direction. | Both are host state another owner writes. | none |
| Classify a change before editing and change only the owning domain. | Evidence, release tags, and CI jobs are selected by ownership. | hook (`tool/version-control/classify` refuses an unclassified path) |
| Report evaluation, build, native runtime, and activation or Apply evidence separately, and never upgrade partial evidence. | A tag or a merge is only as true as the lane it names. | `.githooks/evidence`; skill |

## Where invariants are enforced

Codebase invariants — what must remain true of committed desired state and
tooling — are enumerated under `invariants/<scope>/`, one file each. An entry
states the rule without naming a command, cites its rationale in
`docs/architecture.md` or this file, and declares its enforcement as
`schema` (an evaluator or loader refuses it), `tool` (a script refuses it),
`fixture` (a test proves both directions), `manual` (a reviewer evidence item
in `docs/definition-of-done.md`), or `pending` (an issue, until a check
exists). `tool/version-control/invariants` checks in both directions that
every declaration exists and names its invariant, on every commit and in CI.
Read the classified scope's list before editing that scope.
`invariants/README.md` is the format.

## Governance design

When adding a repository rule, separate its concerns before implementation:

- Put durable rationale in `AGENTS.md` or `docs/architecture.md` and the
  invariant itself in `invariants/<scope>/`. State what must remain true
  without depending on a particular command, product, or model.
- Put human-operable prerequisites, ordered steps, recovery, and authorization
  boundaries in `CONTRIBUTING.md`.
- Put repeatable agent orchestration in a canonical `.agents/skills/` skill.
- Put deterministic classification and enforcement in `tool/`, hooks, CI, and
  remote repository settings.
- Put current adoption state, migration gaps, and expensive choices in
  `docs/status.md`; put per-run proof in CI, pull requests, and release
  evidence.

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

GitHub milestones are the repository's planning surface, not a source of
configuration, architecture, release, or deployment authority. Each milestone
owns exactly one of `unixlike`, `windows`, `common`, or `repository`, uses the
title `<scope>: <outcome>`, and contains only issues in that scope. Cross-scope
dependencies are linked instead of being assigned to the same milestone. A
closed milestone means its planned source work is complete; it does not certify
a domain release or authorize activation or Apply. Repository documents remain
authoritative for durable decisions and current support boundaries. The
repository maintainer owns milestone scope and closure decisions, with the
milestone description and final evidence issue providing the manual evidence.

## Working contract

1. Read `CONTRIBUTING.md`, `docs/architecture.md`, the relevant part of
   `docs/status.md`, and `invariants/<scope>/` for the classified scope.
2. Classify the task as `unixlike`, `windows`, `common`, `repository`, or an
   explicit transfer.
3. Use `tool/doctor.sh` before relying on host-local capabilities.
4. Change only the owning domain. Treat a cross-domain copy as a separate,
   reviewable adoption change.
5. Run narrow domain checks before broader checks. Do not require an unrelated
   domain to pass merely to validate the changed domain.
6. Report evaluation, build, native runtime check, and activation or Apply
   evidence separately for each affected domain.

User-facing usage belongs in `README.md`, workflow in `CONTRIBUTING.md`,
architecture and ownership in `docs/architecture.md`, expensive decisions and
current state in `docs/status.md`, recurring symptoms in
`docs/troubleshooting.md`, invariants in `invariants/`, and executable policy
in `tool/`, hooks, and CI. Canonical project-specific agent workflows live
under `.agents/skills/` and follow the Agent Skills open standard. Reusable
cross-project methods live in the separate sibling `skills` project.
Model-specific context and skill files only point to canonical sources.

`notes/` is untracked maintainer scratch space. It is free-form by design and
carries no structure, review, or retention promise, so it states no policy and
records no decision. It is not project context: do not read, search, summarise,
or act on anything in it unless the user names a file inside it.
