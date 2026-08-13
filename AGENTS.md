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

## Durable decisions

- Do not introduce `specialArgs` for repository identity or host inventory;
  declare typed flake-parts options inside the Unix-like domain instead.
- Do not rely on import-tree collection order for order-sensitive list values.
  Use explicit ordering or a keyed attribute model.
- Do not recreate plugin or addon discovery between repository domains.
- Do not make `common` the default location for new code. Promotion into
  `common` requires demonstrated stable semantics on every intended consumer.
- Keep secrets, undeclared usernames, absolute home paths, and snapshots of
  runtime state out of every domain's committed desired state.
- Version and release `unixlike`, `windows`, and `common` independently even
  when their tags point to commits in the same repository.
- Treat release tags as immutable, annotated domain certifications. Put the
  required evidence in the tag annotation rather than in model context or a
  snapshot of host state committed to desired state.
- Keep branch protection independent of conditional job names. Require the
  stable `Required checks` CI gate, which accepts only the selected domain jobs
  plus the repository-wide secret scan.

## Host safety

- Never activate Home Manager, NixOS, or nix-darwin without an explicit request.
- Never run Windows `Apply` without an explicit request. `-Check` is the
  read-only Windows path.
- Do not update flake inputs, change login shells, garbage-collect Nix stores,
  shut down WSL, or change global Git configuration unless the task calls for it.
- Treat WSL cgroups, binfmt_misc, mounts, and similar kernel-global resources as
  shared by every distribution.
- Preserve externally managed PowerShell profile blocks. Do not change Windows
  OpenSSH DefaultShell or add a `.wslconfig` firewall value without explicit
  direction.
- Do not commit, push, tag, rewrite history, or change branches unless the user
  explicitly requests it.

## Working contract

1. Read `CONTRIBUTING.md`, `docs/architecture.md`, and the relevant part of
   `docs/status.md`.
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
`docs/troubleshooting.md`, and executable policy in `tool/`, hooks, and CI.
The canonical reusable agent workflow lives under `.agents/skills/` and
follows the Agent Skills open standard. Model-specific context and skill files
only point to canonical sources.
