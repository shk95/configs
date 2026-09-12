# Why the Unix-like domain's shape costs what it does

kind: study
date: 2026-09-08
scope: unixlike
scope: repository
status: closed
outcome: docs/candidates/citation-by-section-not-line.md
outcome: docs/candidates/comment-carries-unregistered-rationale.md
outcome: docs/candidates/domain-tool-placement-and-justfile-exception.md
outcome: #213
outcome: #214
outcome: docs/design/unixlike-restructure-plan.md
outcome: docs/decisions/unixlike-domain-owns-its-tree.md
outcome: docs/decisions/concern-first-inside-the-domain.md

Opened from one observation, that the Unix-like entry points were unpleasant
to use, and carried through 2026-09-08 to 2026-09-10 against `dev` fc57495.
It measured where the cost actually falls, whether a relocation is feasible
at all, and how far the repository's own principles already allow one. It
changed no file in the repository; what came out of it is listed above.
`docs/design/repository-domain-map.md` is the picture of the tree it reads.

## What it concluded

The felt bottleneck is a boundary running through the inside of a file.
`tool/version-control/commit` holds repository procedure and Unix-like
authoring knowledge at once, and every new feature has to pass through that
one gate.

The physical layout is not the bottleneck. It is a tax: painful, but paid
once per location. It is also a precondition for fixing the bottleneck,
because without a domain directory there is nowhere to put the pieces the
split produces.

A missing vocabulary is a third defect, separate from both. The contract has
no type for a cross-scope unit of work and none for a library release. It
survives the relocation and the split.

And no trade-off has been reached yet. Most of what this study found is a
Pareto improvement on every axis it cares about. Exactly one choice demands a
real sacrifice, exporting the fragments against keeping the names free, and
that one does not have to be made now.

Why a logical problem wears a physical face: `classify` can only answer per
file, because the atom of ownership is a file. A boundary that runs through
the inside of a file cannot be expressed by any path scheme, so it presents
as a classification and layout problem.

## Three causes, with different cost behaviour

| | What it is | Example | Cost recurs per | Fix |
|---|---|---|---|---|
| 1 | Physical misalignment; the boundary is right, the location is not | `modules/`, `assets/`, `tool/checks/`, `tool/darwin/` | location | move |
| 2 | Wrong unit; the boundary runs inside a file | `tool/version-control/commit` | feature | split |
| 3 | Missing vocabulary; there is no type to express it | cross-scope milestone, library tag, citation grade, runtime premise | act of recording | amend the contract |

Adding one new feature touches, on the physical side, `classify`,
`tool/dispatch/select` and `tool/version-control/domain-reads`; on the unit
side, a `Justfile` recipe and a `tool/version-control/commit` subcommand; and
normally an invariant with its fixture and a `CONTRIBUTING.md` line. The
request that opened this work was that flavours other than Darwin will need
extras too, so the growth axis is the second group. But fixing it properly
needs `unixlike/tool/<feature>`, and without a domain directory that means a
ninth pattern in `classify`, which makes the first group worse. The tax has
to be paid before the bottleneck can be fixed.

Measured on 2026-09-08:

| | windows | unixlike |
|---|---|---|
| classifier patterns | 1 | 8 |
| how the domain's code is defined | one prefix | enumerated by hand in a header |
| the same enumeration repeated in | — | `tool/dispatch/select` |
| cost of a new location | nothing to edit | 3 places, plus CI and the documents |

## The spike: Nix is not the obstacle

Measured by actually moving the tree in a dedicated worktree, which was
restored to a clean `HEAD` afterwards. No activation and no input refresh.

In every layout and spelling that evaluated, all three toplevel derivation
paths were byte-identical to the baseline. A path literal is content
addressed, so the layout never reaches the derivation, and the move is
invisible to reproducibility.

| Question | Answer | Why |
|---|---|---|
| Does `../assets` escape the store? | No | The boundary is the source-root store copy, not the flake directory; `?dir=` copies the whole repository |
| Is a mechanical `git mv` enough? | No | `modules/karabiner.nix` interpolates `${../tool/darwin/karabiner}`, a third directory joined in |
| Do the derivation paths move? | No | Darwin, home and nixos all matched, and so did the payload store paths |
| Layout A, modules left at the root? | Works, but worse | Gains nothing, blocks `path:./unixlike`, and breaks the import-order check |
| Flakeref spelling | `path:.?dir=` yes, `./unixlike` yes, `.?dir=` no | The failure message does not hint at the cause |
| direnv | `use flake ./unixlike` | The `path:.?dir=` form works, but nix-direnv picks its watch list with `[[ -d $flake_dir ]]` and silently stops watching the flake files |

Two layouts remained. Under B, `tool/darwin` stays in `tool/` and the
Karabiner reference becomes `../../tool/darwin/karabiner`; the source root is
then the whole repository, 2.3M, and `path:./unixlike` is unavailable. Under
B2 it moves into the domain; the source root is 340K.

The first write-up of B was too strong and is corrected here. It said the
whole-repository copy would be invalidated by unrelated edits. Measured on
2026-09-10 across eleven commits that touched only `windows/` and the
documents, the Darwin toplevel derivation was unchanged: the source copy
happens, the rebuild does not. What B actually costs is copy time and the
flakeref. What decides for B2 is ownership.

The real gate is not Nix. `classify` answers `unclassified` for every moved
path and the hooks and CI refuse there, so the classifier change and the
`git mv` would have to be in one commit, and that commit mixes `repository`
with `unixlike`. The cost of relocation is governance, not evaluation.

## Pattern identity: an internally stored variant of the Dendritic Pattern

The Dendritic Pattern is a proper noun: Shahar "Dawn" Or (@mightyiam), first
commit 2025-05-08, subtitled "A Nixpkgs module system usage pattern" — a
module-system pattern, not a flake pattern. Its definition has three parts.
Every `.nix` file but the entry point is a module of one top-level
configuration; each module implements one feature across every configuration
it applies to, and its path names that feature; and the sub-modules for
NixOS, Home Manager and nix-darwin are stored as option values of the
top-level configuration.

| Subject | Verdict | Why |
|---|---|---|
| This repository | Orthodox, with a qualifier | Fragments are stored in `config.modules.<class>` rather than in `flake.*`: a non-exporting variant. It avoids all four of the original's anti-patterns and forces two of them as invariants |
| zmre/pw-nix-dendritic | Orthodox, one weakness | Exports through `flake.{darwin,nixos}Modules`. Two of its hosts select by string name with `moduleSet.${n} or null`, so a typo is silent; the third refers to attributes directly and is safe |
| ryan4yin/nix-config | Not dendritic | Zero of three. No top-level configuration, attribute-set merging, path imports, and two of the anti-patterns at the centre of the design |

Worth taking: file per host, but as data rather than as a module; evaluation
tests in the `expr.nix` / `expected.nix` shape; a directory axis for outputs.
Not worth taking: `genSpecialArgs`, flake-file generation, string-name
filtering, haumea, colmena.

Three independent sources agree on one thing, avoiding `specialArgs`. The
dendritic write-up names it an anti-pattern, zmre says in its own agent file
that it avoids it, and this repository enforces `INV unixlike/typed-identity`.
Only ryan4yin takes the other side.

## Composition: a flake takes no dynamic argument, so the answer is layers

There is no argument channel on the command line, so "compose from outside"
has exactly four forms: a consumer flake, which is pure and static;
`--impure --expr`, which is genuinely dynamic and bypasses the evidence;
folding data held inside the flake, which is declarative; and generating a
flake. Both repositories surveyed took the third.

```text
L1  fragments        config.modules.<class>, 8 classes
                     exporting is one line of code and, in substance, the
                     decision to have a public API
       │
L2  composition      configurations.nix becomes flake.lib.mkHome / mkNixos /
                     mkDarwin; the policy stays in one place and only the
                     call site moves out
       │
L3  host instances   this repository's 3 hosts, the first consumer of L2,
                     foldable from hosts/<name>.nix as data

take L3 out of the repository and these break:
  INV unixlike/eval-covers-every-host      INV unixlike/desktop-not-wsl
  INV unixlike/import-order-independence   INV unixlike/typed-identity
  and a tag stops certifying a deployable state

anything outside that wants to consume this needs only L1 and L2, and none
of the contracts break
```

Half of "separate the Nix into pure source" is already done: that a feature
file does not know its host is enforced lexically by `tool/checks/composition`.
What is left is whether to export, which is one line of code and a decision
to have a public API.

## Citations: freshness is decided by the form

Two forms live in the same tree and the difference between them is whether a
check runs in both directions.

| Citation form | Count | Broken | Check |
|---|---|---|---|
| `INV <scope>/<slug>`, `PROV` | 53 | 0 | `tool/version-control/invariants`, both directions |
| a `docs/.../<slug>.md` path | 28 | 0 | none, and healthy anyway |
| `AGENTS.md line N` | 4 sites, 2 distinct | all 4 | none |
| implicit, "recorded as a cost" | — | no referent | impossible |

The sentence cited as `AGENTS.md line 93` had moved to line 104, and line 93
was something else; one of the three sites was a refusal message printed to
the operator. The rule cited as line 127 had moved inside a table.
`modules/flake/module-classes.nix` claimed a cost was "recorded" somewhere
that held no such record.

Three rules follow. A comment says why this code has this shape — local
reasoning, rejected alternatives, measurements, citations — and never states
a durable rule registered nowhere else; the authority table has never listed
comments and they carry the longest prose in the tree. A citation into a
living document names a section and never a line, which is an extension of
the form `decision:` already uses in a registry entry rather than an
invention. And editing an authority file should be able to produce the list
of places citing it, though a machine can only answer whether a citation
resolves, not whether it is still right, so the second half is a review item.

The repository had already opened the door: `docs/candidates/README.md` says
what does not wait there includes "the correction of tracked text that is
false today". Four line numbers are false today, so they skip the candidate
stage. Only the rules wait.

One more real case. The zmre README says each host writes its modules in two
places, and the code filters one list twice. The prose is older than the code,
and a third party reading the prose carried a wrong conclusion into this
study. No format check catches that kind.

## Splitting: five axes, two of which become directories

| Axis | Separates | A directory? | Why |
|---|---|---|---|
| Owning scope | unixlike, windows, common, repository | required, level 1 | three tools must answer from the path alone |
| Kind of artefact | declaration, execution, claim, prose, evidence | yes, level 2 | — |
| Composition layer | fragment, function, instance | inside unixlike only | — |
| Authority grade | rationale, invariant, procedure, enforcement | no, an attribute | one rationale exists in several locations at once |
| Runtime premise | pre-Nix, dev shell, Nix, native pwsh | no, an attribute | 69 contracts already declare it |

The cost comes from mixing directions, not from choosing one. Scope first
makes the scope the first segment; kind first with a mandatory scope segment
makes it the second. Either is one rule. Today `windows/` is scope first,
`invariants/<scope>/` is kind first, `modules/` has no scope segment at all,
and `tool/` is inconsistent internally.

The proposal splits by nature. What is deployed or executed goes scope first.
Claims and prose go kind first with a mandatory scope segment. Only what an
external tool requires at a location stays at the root.

| Group | Contents | Rule |
|---|---|---|
| domain | `unixlike/{modules, assets, lib, outputs, tool}`, `windows/{win-env.ps1, desired, src, tools, tests}` | scope first; authorable and checkable from its own tree |
| governance | `tool/`, `.githooks/`, `.github/`, `.agents/` | nothing is deployed, so no domain tree is needed, and `tool/*` becomes `repository` without exception |
| specification | `invariants/<scope>/`, `provisional/<scope>/`, `docs/` | kind first with a scope segment |
| external convention | `flake.nix`, `.envrc`, `.github/`, `README.md`, `LICENSE`, `AGENTS.md` | the test is whether an outside tool requires that location |

This answers the spike's open question on its own. `tool/darwin/karabiner` is
executed and owned by the domain, so scope first puts it at
`unixlike/tool/`, which is B2. The 340K source root is a side effect and
ownership is the reason.

Flattening has two readings, and only one of them is safe.

```text
reading A                          reading B
concerns at the top level          concerns inside the domain

karabiner/                         unixlike/
homebrew/                            karabiner/ {module, payload, tool, check}
zellij/    unixlike + windows        homebrew/  zellij/
wezterm/   unixlike + windows        shell/ {shared, darwin, wsl}
powershell/ unixlike + windows       flake/ {configurations, identity, classes}
                                   windows/
three pairs of deliberate copies      the manifest already groups 7 features
become adjacent, which is the       the copies stay in separate trees and
pressure the architecture           Karabiner's three-directory join
explicitly refuses                  disappears
```

Windows reaches the same cohesion by declaration rather than by physical
layout, in `windows/desired/manifest.json`. That is two local
implementations, not a thing to unify.

Flattening does not fix the second cause. The publishing engine — branching,
confirmation, hooks, pull request, auto-merge — is procedure rather than a
concern and stays in governance. Flattening does not remove the gate; it
makes a place to split it into. And what is left over after the concerns are
taken out is exactly the other three groups above, so "flatten everything" is
impossible by definition.

## Where the existing principles push back

| | Subject | Principle | Result |
|---|---|---|---|
| blocked | planning the relocation as one milestone | one milestone, one scope; cross-scope work is linked | no way around it: two milestones, neither meaningful alone |
| blocked | tagging a library release | a tag is a domain release with evaluation, build and native evidence | a module library has no build evidence, so exporting is possible but an honest export is not |
| shape | file per host | `INV unixlike/composition-in-one-place` | a violation if a host is a module, untouched if a host is data; the principle chose the better form |
| shape | the moving commit | a change stays inside its owning domain | expand, migrate, contract as three commits, with the interim tolerance registered under `provisional/` |
| shape | a new entry point | the rejection recorded for the Windows entry point | it is work that follows the relocation; built first, it repeats a recorded rejection |
| open | correcting the citations | the explicit exemption in `docs/candidates/README.md` | correcting text that is false today does not wait |
| cost | a scope segment under `docs/` | `CONTRIBUTING.md`, "Documentation ownership" | the declared location-to-responsibility table has to be amended; the only contentious point in the four-way split |

Is any of this a trade-off, or has the trade-off simply not been reached?
Most of what was found loses nothing in the steady state — physical
alignment, concern-first inside the domain, hosts as data, a fixed citation
form, evaluation tests, splitting `commit`. Exactly one choice demands a real
sacrifice: exporting the fragments against keeping the names free. Once
something depends on a name, changing it becomes expensive, and no design
removes that. But it does not have to be decided now, because not exporting
is reversible by adding one line while a published name cannot be recalled,
and an asymmetrically reversible choice is the kind to defer.

Four things that looked like trade-offs were confusions of dimension: scope
against concern, which are levels 1 and 2; domain self-sufficiency against
cohesion, which putting concerns inside the domain gives both of; a lexical
check against expressiveness, which holding hosts as data gives both of; and
an entry point against runtime premises, which an entry point hides rather
than removes.

That does not mean an optimum exists. There are several objective
functions — domain independence, local understandability, honest evidence,
cost of change — and some pull against each other. Optimality is also
undefined over time: the three `assert builtins.length names == 1` lines were
optimal when they were written. So the criterion is not optimality but the
cost of reversal, and the repository already has the instruments for that:
`provisional/`, `docs/candidates/`, and "copying is preferred to premature
sharing". The question is not whether to accept a trade-off but which one to
keep. The current one, doing nothing, costs per feature; the proposed change
pays once and removes it.

## What the maintainer has to decide

1. Target layout: B, `tool/darwin` stays in `tool/`, or B2, it moves into the
   domain. A is out. The test is whether the enumerations in `classify`,
   `select` and `domain-reads` actually shrink, and the split proposal leans
   to B2.
2. Whether the inside of the domain is divided by kind or by concern.
   Concern first removes Karabiner's three-directory join and promotes to
   directories a structure that was already in the file names, eight named
   `darwin-` and six named for WSL.
3. What becomes of the `Justfile`: moved into the domain, or kept as a
   repository adapter beside a new domain entry point.
4. Whether the name `tool/` stays. It appears 718 times in the tree, so
   keeping it is overwhelmingly cheaper, and the split proposal makes it the
   place for repository tools without exception.
5. Whether to export the fragments. One line of code, in substance a public
   API, and the irreversible direction, so deferring is the default.
6. Whether to amend the milestone rule and the tag contract, which have no
   vocabulary for a cross-scope unit of work or a library release. They are
   sentences this repository wrote, so they can be amended.
7. The deployment tool, once there are more NixOS desktop hosts: an entry
   point verb, or colmena or deploy-rs.

## What this study got wrong

It overstated the `Justfile`'s dual ownership. Twelve of the thirteen
`[group('repository')]` recipes run `tool/checks/*`, which is Unix-like, so
the Unix-like lane being selected is correct behaviour and the classifier is
not wrong. Only the group label misleads.

It repeated, from the zmre README, that each host writes its modules in two
places. The code filters one list twice. The sentence is in that repository's
README and the code moved on after it; carrying a summary without checking
the source was the mistake.

It discarded one number a subagent reported. "41 modules, 34 feature files"
was wrong; the tree holds 49 and 42, and `tool/checks/composition` answers 42
as well. The relative results — derivation-path equality, the error messages,
the spelling table, the direnv source — are independently reproducible and
were kept; only the absolute count was dropped.

## Resolved after the study was written

On 2026-09-10, flake-parts was found to declare `flake.nixosModules` itself,
in `modules/nixosModules.nix`, as a `lazyAttrsOf deferredModule` with an
`apply` that sets `_class` and `_file`. Our `module-classes.nix` comment that
it mirrors what flake-parts does is accurate, and the subagent's conclusion
that zmre's nixos class was an untyped freeform set was wrong.

Also on 2026-09-10: `darwin-rebuild` splits only on the last `#` and passes
the front unchanged to `nix build`, so the `?dir=` spelling is accepted, and
`build` triggers no activation. The `home-manager` script's parsing was run
through the same shell expansion and its `nix eval` accepted the `?dir=`
form; one run of the command line on a WSL host is what remains. And
`nix flake update` against a subdirectory flake writes that subdirectory's
lock and creates none at the root, measured on a throwaway fixture without
touching this repository's inputs.
