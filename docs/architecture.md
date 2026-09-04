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

Composition, identity, and ownership in this domain rest on seven rules, each
registered under `invariants/unixlike/`. One file maps module classes to
hosts, and a feature file writes into a class without naming a host or
forcing another class's decision, so where a program reaches is read in one
place. A graphical class is composed only into a home that has a display; the
WSL homes take no graphical program, because their terminal is declared in the
Windows domain. Host identity is a typed option set whose values live in the
inventory, so an evaluator refuses a wrong shape before any host is composed,
and no untyped argument carries identity around the module system. Module
files are collected by a directory walk, so nothing order-sensitive may depend
on that order. A package has one declaring module: a feature module when it
generates the package's configuration, otherwise the shared list, and a system
module only when a service, activation script, or system account needs it,
because two owners on one PATH make precedence an accident; the one accepted
imperative exception is a version manager the user installs, which is never
declared as a package and runs last so declared packages keep precedence.
Finally, evaluation is evidence only when it reached every configuration: a
check that found nothing to evaluate has failed, not passed.

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

The manifest is held to a few more rules because a host reads it with no
evaluator in front of it. Every identifier is unique, so a plan and a state
record can name an item without ambiguity. A file that varies by Windows
build declares its variants as a strictly descending list ending in an
unconditional one, so every host resolves to exactly one payload and none
falls through. A managed file names a parser the domain actually has and a
comparison mode the domain declares, and a mode that reads both sides in one
format is refused on any other parser, because a check that cannot parse
what it compares reports nothing. An unsupported manifest or state schema is
refused before any comparison, so an older module never misreads a newer
shape as drift. A subset payload declares a list only when it has content,
because an empty declared list would claim whatever the host holds there and
absorb host state silently. The desired-state hash covers the manifest, the
selected features, and every variant of a selected file, and nothing a host
did not select, so drift is never reported for a payload a host never
deploys. Deployment expands exactly one content placeholder and capture
restores exactly that one; any other host-specific spelling is refused
rather than invented. A read-only check answers whether an Apply is needed:
it returns 0 when converged, 2 when anything drifted, and the unverified
status only when its sole open question, or a prerequisite the host lacks,
could not be decided there, with native evidence able to turn that into a
failure. Finally, the Windows checks and suite read only the Windows tree
and need no Unix-like toolchain, because this domain must be authorable and
checkable on its own host.

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

Until a common component exists the repository carries no common
classification, dispatch unit, or gate job; the change that creates the
domain restores all three together with its contract and checks, so common
content cannot land unchecked. A removed scope keeps a classifier arm for the
paths it once owned until its historical deletions are no longer inside any
pull-request range; a path nothing classifies cannot be pushed, and that
includes its own removal.

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

### Desired-state hygiene

Committed desired state carries no secret, no undeclared user or host name, no
absolute home path, and no snapshot of runtime state. The registry entries
named below state it. The invariant is repository-wide because every
domain publishes its desired state from one history, and it belongs to the
`repository` governance scope because assigning it to one platform would make
that platform authoritative for the others. The repository maintainer owns the
decision.

The failure it prevents is not hypothetical. A host path that reaches history
stays there after the file is edited, the way a credential does, and it turns a
public description of intended state into a description of one machine. Two
absolute home paths reached `docs/troubleshooting.md` and stayed for the
document's whole history, because the sentence had a policy owner and no
enforcement owner, which "Governance design" says must not happen.

The invariants are registered, one file each, as
`INV repository/hygiene-home-paths`, `INV repository/hygiene-declared-names`,
`INV repository/hygiene-runtime-state`, `INV repository/hygiene-machine-identity`,
`INV repository/hygiene-exclusion-symmetry`, and the manual
`INV repository/hygiene-prose-account-name`; secret detection stays with the
secret scan as `INV repository/no-secret-in-history`. Each entry carries its
own qualifications, so this section no longer restates them.

One half of the first invariant is decidable by no scanner: a bare account name
in free prose has no naming context to recognise it by. It remains a manual
invariant, its evidence is the reviewer's reading of prose in the diff as
required by `docs/definition-of-done.md`, and the repository maintainer is its
decision owner. Nothing in the enforcement plane covers it.

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

The hooks a clone runs are audited as a directory rather than a string, and
the outcomes the hooks produce are recorded outside the working tree so that
the local gate's yield can be measured.

## Invariant registry

The third layer of this repository's specification — what must remain true
of committed desired state and tooling — is enumerated under
`invariants/<scope>/`, one entry per invariant, rather than written as prose
in this document or in `AGENTS.md`. The registry is the authority for which
invariants exist. This document remains the authority for why: every entry
cites a section of this file or of `AGENTS.md` as its rationale, and an
entry with no such section is refused.

An entry declares its enforcement as `schema` (an evaluator or loader refuses
the violation), `tool` (a script exits non-zero), `fixture` (a test holds
positive and negative cases), `manual` (a reviewer evidence item named in
`docs/definition-of-done.md`), or `pending` (an issue, until a check exists).
`schema` and `tool` require a `fixture` on the same entry, because an
enforcement with no fixture is a convention written as a control. `pending`
is a declared gap with an owner; it is reported, never passed off as
enforcement.

The canonical statement lives in the registry and the enforcement point
carries only the entry's id, as the literal `INV <scope>/<slug>`. This is a
deliberate departure from the rule "rule text lives where it is enforced":
enforcement here spans POSIX shell, PowerShell and Nix, and a loader's error
string in one of them cannot serve as the repository-wide sentence. The id
at the enforcement point is what lets `tool/version-control/invariants`
verify coverage in both directions.

The registry does not replace the decision record. An entry may point at a
`docs/status.md` section with `decision:`; the pointer is checked, so a
renamed section fails the check rather than leaving a dangling citation.

The rule runs in both directions. A fixture unit — a top-level `Describe` in
a Pester file, a banner section in a shell suite — names the invariant it
proves, and a unit that names none is a deletion candidate rather than
coverage. The 2026-09-03 review of the suite measured why: over 157 CI runs
the suite caught one configuration defect, and no fixture had ever caught a
regression, because every fixture proved a tool once and nothing tied it to
a claim.

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

Commit subjects on the integration branches are Conventional Commits, and a
`flake.lock` refresh is its own commit: the first keeps history readable by
tools that group by type, the second keeps a change that moves every
Unix-like derivation hash separable from the source change beside it
(`INV repository/conventional-subject`, `INV repository/flake-lock-isolated`).

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
