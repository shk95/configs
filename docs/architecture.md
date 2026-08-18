# Configuration domains

## Decision

This monorepo has three independent configuration domains: `unixlike`,
`windows`, and `common`.

The repository boundary provides search, provenance, and review history. It
does not require the domains to share an evaluator, module graph, release, or
deployment. Each deployable domain must be understandable and operable from
its native environment.

The previous model optimized for the smallest common implementation by making
the flake compose Windows output on a Unix-like host. That reduced duplicated
text but introduced synchronous coupling, foreign-platform validation gaps,
and a growing cross-platform option model. The new model optimizes for local
ownership and independent change instead.

## Default rule: keep implementations separate

Similarity is not sufficient evidence for a common abstraction. Begin with
separate Unix-like and Windows implementations, even when that duplicates
settings or code.

Agents and maintainers may inspect another domain and copy the useful parts.
The copy is an adoption event, not a permanent synchronization contract. Once
copied, the destination domain owns the result, validates it natively, and may
change it independently.

Do not add cross-domain generation merely to avoid duplication. Duplication is
cheaper than a shared authority when platform behavior, package versions,
paths, release cadence, or validation environments can diverge.

## Unix-like domain

The Unix-like domain covers Linux, WSL, NixOS, Home Manager, and macOS. Nix and
the flake are its composition authority.

It owns:

- `flake.nix` and `flake.lock`;
- feature and host modules under `modules/`;
- Unix-like source payloads consumed by those modules;
- Unix-like evaluation, build, and activation tooling.

A payload is not only a file a domain owns. It has a format, and being well
formed is a property of that format rather than of the domain holding it, so it
needs a parser that the domain's own evaluator does not provide. Nix delivers
payloads with `.source`, which copies without reading, so evaluation and build
evidence say nothing about payload content. Each deployable domain therefore
declares its payloads and their formats — `assets/payloads.json` for Unix-like,
the `Parser` field of `windows/desired/manifest.json` for Windows — and
validates them with the parser that will consume them. The two declarations are
independent copies of one idea, not a shared authority, and neither imports the
other.

Linux and macOS may share Nix modules where the Nix module system can evaluate
the complete result directly for both. Platform-specific Nix modules remain
preferable when behavior differs. This internal sharing does not make their
content part of the repository-wide `common` domain.

Unix-like deployment consumes a domain release tag and activates only on a
matching host after evaluation and native build evidence.

## Windows domain

The Windows domain covers native Windows packages, files, registry values,
application lifecycle, validation, backup, and reconciliation. Its target
authority is a Windows-owned source manifest and payload tree consumed directly
by PowerShell.

It must be possible to author, check, and Apply Windows desired state without
building a Nix output on Linux or macOS. Foreign-host syntax checks may be
useful supplementary evidence, but they cannot be the authority for Windows
runtime behavior.

Windows deployment consumes a Windows domain release tag. Native Pester and
read-only `bootstrap.ps1 -Check` evidence precede any explicit Apply.

The source manifest and every owned payload live below `windows/desired/`.
PowerShell reads that source directly; there is no Nix-rendered Windows
consumer tree.

The manifest declares features, and every package, managed file, font, and
registry delegation is owned by exactly one of them. A feature may declare that
it requires another when its payload cannot be honest without it. Which
features a host deploys is host state recorded in that host's `state.json`, not
desired state: the repository declares what exists and a host records how much
of it it took. A minimal deployment is therefore a supported outcome rather
than an incomplete one, and drift is only ever computed against the selected
set. Deselection stops management; it never uninstalls or deletes what an
earlier Apply deployed.

## Common domain

The common domain is an explicit exception for material whose semantics are
demonstrably platform-neutral. It is not a home for convenient helpers, similar
files, or speculative reuse.

Common material must:

- live below an explicit `common/` boundary;
- state the contract it owns and the consumers it intends to support;
- avoid platform paths, package managers, shell executable names, host
  inventory, and deployment behavior;
- have checks that do not depend on one consumer silently supplying context;
- be versioned and released independently;
- have no direct host activation or Apply step.

Consumers adopt a common release explicitly and asynchronously. Prefer copying
the selected content into the consuming domain so that it becomes locally
owned. If direct consumption is ever justified, pin the consumed common
version and document why the resulting dependency is worth the coupling. A
change to common `HEAD` must never silently change Unix-like or Windows output.

Creating or expanding `common` requires evidence from existing independent
implementations. The burden is to prove stable shared semantics, not to prove
that two files contain similar lines.

## Change and dependency rules

```text
unixlike change ──> Unix-like checks ──> unixlike release ──> activation

windows change  ──> Windows checks  ──> windows release  ──> Apply

common change   ──> common checks   ──> common release
                                             │
                              explicit later adoption
                                  ┌──────────┴──────────┐
                                  v                     v
                           unixlike change       windows change
```

- A domain change does not require an unrelated domain release.
- Cross-domain adoption is a separate commit or pull request from the source
  change.
- CI may report similarities or available adoptions, but drift between
  independently owned copies is not a failure.
- A direct dependency across domains is forbidden unless its contract,
  version, and failure boundary are explicit.
- Root-level tooling may dispatch domain checks, but must not turn unrelated
  domain success into a prerequisite for a local change.

## Repository governance plane

Version-control policy, check dispatch, hooks, CI wiring, and reusable agent
workflows are repository governance rather than configuration desired state.
They use the `repository` change scope because assigning them to one platform
would make that platform authoritative for the others.

This scope is deliberately narrow:

- it creates no host configuration, package, payload, or deployment;
- it does not participate in `unixlike`, `windows`, or `common` release tags;
- it may classify and dispatch domain checks without owning their semantics;
- domain behavior discovered during governance work is changed separately in
  the owning domain.

Check dispatch uses three evidence states rather than two. A check reports
verified with exit status 0, failed with any other status, and unverified with
69 when the host cannot supply one of its prerequisites. A failure outranks an
unverified result. `REQUIRE_NATIVE=1` turns unverified into failure; CI sets it
so the merge gate never accepts an unchecked change, and hooks leave it unset
so a clone is never blocked from pushing work for a domain it cannot verify.
The governance plane owns this contract and the hooks that consume it. Each
domain owns the detection of its own prerequisites and reports through the
contract rather than deciding what a missing tool means.

The canonical agent workflow follows the Agent Skills open standard under
`.agents/skills/`. Product-specific discovery locations may contain thin
adapters, but they do not own or duplicate the workflow.

Branch protection consumes one stable CI contract named `Required checks`.
The gate validates classification, the repository-wide secret scan, and each
job selected by the classifier. Individual domain jobs remain conditional and
are not protection contracts, so adding or skipping a domain does not silently
weaken or deadlock protected branches.

Governance itself has separate authority layers:

```text
decision and invariant -> human procedure -> agent orchestration
                                      \-> deterministic enforcement -> evidence
```

The left side is durable project judgement. The right side is replaceable
implementation. A procedure may select commands but cannot invent a new
obligation; an enforcement mechanism must trace back to an invariant; evidence
records an execution and never becomes desired-state authority. This separation
keeps context concise while retaining reproducible operations.

## Version control and releases

The repository keeps shared integration branches so history remains easy to
inspect. Readiness and deployment are domain-scoped rather than repository-wide.

- `dev` integrates reviewed source changes.
- `master` contains accepted repository history; it is not proof that every
  domain at that commit was deployed.
- `unixlike-vYYYY.MM.DD[.N]` identifies a validated Unix-like release.
- `windows-vYYYY.MM.DD[.N]` identifies a validated Windows release.
- `common-vYYYY.MM.DD[.N]` identifies a validated common release.

A tag certifies only its named domain. Unrelated files present at the same Git
commit do not acquire that certification. Evidence is recorded and reported
per domain.

Release tags are annotated and immutable. A release target must be reachable
from `master`, but it need not be the newest commit when a domain intentionally
releases an earlier accepted state. The annotation is the portable release
evidence record and distinguishes evaluation, build, and native-runtime checks.
Activation and Apply remain later deployment events and are never inferred
from the tag.

Source flows one way from topic branches through `dev` into `master`.
`master` accepts only a same-repository `dev` pull request and preserves that
boundary with a merge commit. It does not flow its promotion merge commit back
to `dev`. Consequently `dev` protection requires the proposed head to include
its current base, while `master` protection may evaluate the pull request merge
without requiring `dev` to contain the previous promotion merge commit. The
single allowed source, one-open-promotion rule, and CI source gate preserve
serialization.

## Why the repository remains a monorepo

Independent ownership does not require separate repositories. Keeping the
domains together preserves provenance and makes selective comparison and
copying inexpensive for people and agents. Repository separation is justified
only if access control, lifecycle, or release infrastructure later requires it.
