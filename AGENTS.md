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
live in the Unix-like scope directories under `docs/`. For module structure or
composition, read [Unix-like module layout](docs/policy/architecture.md#unix-like-module-layout).

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
| Commit, integrate, push, tag, rewrite history or change branches only within the user's explicit task authorization; preserve a staged-only boundary when requested. | Authorization persists within its agreed scope; a tool allowlist supplies none. | manual authorization review |
| Use the user-selected current checkout or linked worktree; ask when the choice is missing or must change, and isolate parallel authors. | A continuing task keeps its agreed workspace instead of repeating the question. | explicit workspace argument; manual user-choice review |
| Do not update flake inputs, change login shells, garbage-collect Nix stores, shut down WSL, or change global Git configuration unless the task calls for it. | Each is host-global or irreversible from inside a session. | none |
| Treat WSL cgroups, binfmt_misc, mounts, and similar kernel-global resources as shared by every distribution, and the kernel under an OrbStack machine as shared by every machine and by OrbStack's container engine. | One distribution's fix is every distribution's change, and an OrbStack machine's UIDs are mapped one to one: its root is UID 0 on that kernel. | none for WSL; consumer-owned assertion and fixture for an OrbStack machine's binfmt registry |
| Preserve externally managed PowerShell profile blocks. Do not change Windows OpenSSH DefaultShell or add a `.wslconfig` firewall value without explicit direction. | Both are host state another owner writes. | none |
| Classify a change before editing and change only the owning domain. | Ownership determines boundaries and release scope; effect selects checks. | classifier reports ownership; hooks and CI reject unclassified paths |
| Report evaluation, build, native runtime, and activation or Apply evidence separately, and never upgrade partial evidence. | A tag or a merge is only as true as the lane it names. | domain checks and manual report review |
| Register a temporary measure under `docs/provisional/` in the change that adds it, tag every disposable line `PROV <scope>/<slug>`, and retire it by deleting the entry and its tags together. | A measure with no exit condition and no review date becomes permanent by neglect. | tool (`tool/version-control/provisional`) |

## Where invariants are enforced

`docs/policy/invariants/<scope>/` states the invariants and their enforcement.
Read the affected entries when changing behavior or governance; the format is
`docs/policy/invariants/README.md`. The registry check validates declarations
and fixture tags, not the truth or sufficiency of evidence.

## Governance design

Each obligation has one authoritative source. Procedures, tools and optional
agent orchestration implement it without adding policy. Keep project policy,
procedure and enforcement here; model-specific adapters only point to them.
Local notes, installed plugins and agent memory supply no project rule or
permission. Reusable orchestration is optional and owned externally.

When changing governance:

- Put rationale in this file or `docs/policy/architecture.md` and invariants in
  `docs/policy/invariants/<scope>/`. Keep statements independent of a command,
  product or model. Enforceable invariants need positive and negative fixtures;
  manual evidence needs a named owner and a definition-of-done item.
- Put human procedure in `CONTRIBUTING.md` and deterministic decisions in
  tools, hooks, CI or remote settings. Operators use `tool/configs`; hooks and
  CI call implementations. Domain operations stay in their owning domain.
- Put adoption state in `docs/status/`, costly choices in decision records and
  unaccepted observations in candidates. A candidate is not authority and does
  not delay a change the maintainer has explicitly requested.
- Use paired specs/reports for sustained planning or evidence, with dated
  criteria amendments; small clear changes need only concise results and
  verification. Work records bind their task, never future project behavior
  (`INV repository/design-outside-authority`).

## Version control

Master is the release and ordinary work branch. Several logical commits for
one same-scope outcome use a topic and no-ff integration. A selected linked
worktree also uses a topic, even for one commit. Follow the workspace and
authorization boundaries above throughout the agreed task; do not request the
same answer or approval again. A workspace choice is not commit/push consent.
History maintenance still needs fresh approval for its exact operation.
If work grows after a master commit, keep that commit and group remaining
work on a topic rather than rewriting accepted history.

Use the relevant operation in `CONTRIBUTING.md` through tracked tools instead
of reproducing their checks or inventing agent-only exceptions. Integration,
push, release, history maintenance and workspace removal use their respective
procedures when requested. Ordinary force pushes are forbidden; approved
maintenance uses the isolated capability. Deletion requires preservation
review. Missing evidence and uncertain liveness never authorize either.

Issues, ordinary PRs, external role plugins and local checkpoint files are
optional. No planner/worker split or separate bookkeeping delivery is required.
Source preparation, publication and deployment are distinct outcomes. Preserve
existing history and data; never prune as incidental cleanup.

## Working contract

1. Classify the task and inspect actual Git state. Continue existing work
   without reinitializing it or disturbing its staged changes.
2. Read only relevant current procedure, ownership, affected invariants and
   status. Consult decisions or work records when the task or an ambiguity
   calls for them; historical citations are not a session reading list.
   The [procedure index](docs/development/README.md) selects one concern;
   `CONTRIBUTING.md` retains platform procedures and existing section links.
3. Use `tool/configs doctor <scope>` before depending on an unverified host
   capability or after the environment changes. Consult `policy show` when
   resolving mechanical rules and use `workflow start` for a clean new start,
   not as a prerequisite to inspection or continuing work.
4. Change only the owning scope, run the relevant tracked checks and report
   actual evidence and unavailable checks. Read only the applicable review
   items in `docs/policy/definition-of-done/<scope>.md`; a passing tool result
   need not be manually reimplemented or reported checkbox by checkbox.

`docs/README.md` maps documentation: usage is in `README.md`, procedure in
`CONTRIBUTING.md`, ownership and rationale in architecture, current state in
status, adopted choices in decisions, invariants in their registry, work proof
in specs/reports and recurring symptoms in troubleshooting.

`notes/` is untracked maintainer scratch space. It is free-form by design and
carries no structure, review, or retention promise, so it states no policy and
records no decision. It is not project context: do not read, search, summarise,
or act on anything in it unless the user names a file inside it.
