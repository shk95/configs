# What the three scopes own and what a change passes through

kind: map
date: 2026-09-08
scope: unixlike
scope: windows
scope: repository
status: closed
outcome: docs/design/unixlike-restructure-study.md

Three scopes share one tree. This document draws what owns what, which
evidence a change passes through on its way to a tag, and where the physical
layout disagrees with the logical ownership. It is a reading of the tree at
`dev` fc57495 on 2026-09-08, re-checked against `origin/dev` 0c87770 on
2026-09-10, where the Unix-like numbers were unchanged and the invariant
count had moved from 56 to 58. Every number below is that reading, not a
claim about the tree now; `docs/status.md` is what speaks in the present
tense.

Measured then: 3 host outputs, 8 module classes, 49 Nix module files, 15
declared payloads, 7 Windows features, 31 managed files, 58 invariants.

## Ownership, and the two places the root disagrees with it

`tool/version-control/classify` must answer exactly one scope for every path.
Windows is a prefix. Unix-like is eight patterns enumerated by hand.

```text
repository root                             owning scope
  flake.nix   flake.lock                  ┐
  modules/               49 .nix          │
  assets/                15 payloads      ├── unixlike
  .envrc                                  │     8 classifier patterns
  tool/checks/   tool/darwin/             │     10 invariants
  Justfile               37 recipes       ┘     tag unixlike-vYYYY.MM.DD

  windows/               7 features       ─── windows
                                                1 pattern, 23 invariants
                                                tag windows-vYYYY.MM.DD

  tool/version-control/                   ┐
  tool/dispatch/  tool/setup  doctor.sh   ├── repository
  docs/  invariants/  provisional/        │     no host output, no tag
  .githooks/  .github/  .agents/          ┘     25 invariants
```

Two lines leave their own scope.

The heavy one is `tool/version-control/commit`. It is a repository tool, and
it knows the list syntax of `modules/darwin-homebrew.nix`, the `masApps`
attribute set, and both Karabiner payloads under `assets/` well enough to
edit them. That is the structural debt this set of documents was opened over.

The light one is the `Justfile`. Twelve of its thirteen `[group('repository')]`
recipes run `tool/checks/*`, which is Unix-like material, so the classifier's
`unixlike` answer is correct and only the group label misleads. The two that
genuinely cross are `doctor` and `karabiner-capture`, the latter by calling
the repository tool above.

`common` has no arm at all. The change that creates the domain restores its
classification, its dispatch and its gate together
(`docs/architecture.md`, "Common domain").

## Unix-like composition: a feature file does not know its host

`flake.nix` is one line of wiring and `import-tree` walks `modules/`. Each
file contributes a fragment to `modules.<class>` and says nothing about where
it lands. The edges from classes to hosts are drawn in exactly one file.

```text
flake.nix ──import-tree──> modules/          ──> modules.<class>
                           43 feature files        homeManager.shared
                           modules/flake/ 6        homeManager.desktop
                                                   homeManager.wsl
                                                   homeManager.wslStandalone
                                                   homeManager.darwin
                                                   homeManager.agents
                                                   nixos.wsl
                                                   darwin.system
                                                        │
                    modules/flake/configurations.nix ───┤  the only gate
                                                        │
                    homeConfigurations   standalone Home Manager, Ubuntu WSL
                    nixosConfigurations  NixOS-WSL, headless
                    darwinConfigurations nix-darwin, aarch64
```

The missing edges carry information too: `homeManager.desktop` reaches no WSL
home, and that is `INV unixlike/desktop-not-wsl` rather than an accident.

Payloads run in a lane of their own, because Nix delivers them with `.source`
and copies without reading:

```text
assets/  ──>  assets/payloads.json  ──>  tool/checks/payloads
              15 declarations,            each format parsed by the
              format named per entry      consumer's own parser
```

Evaluation and build evidence therefore say nothing about whether a payload
is well formed, which is why the declaration and the parser exist at all.

## The Windows domain: one door that decides nothing

`windows/win-env.ps1` holds a verb table and no other policy. Each verb runs
exactly one script under `windows/tools/` and returns its exit status
unchanged (`INV windows/entry-point-forwards-status`).

```text
operator ──> win-env.ps1 ──> windows\tools\*.ps1 ──> windows\src\WinEnv.psm1
             check                                   desired\manifest.json
             apply                                     7 features
             capture                                   31 managed files
             validate                                   5 packages
             test                                   state.json
             setup-dev                                the features this host
             font                                     selected: host state,
                <── exit status forwarded unchanged    not desired state
                    0 converged, 2 drift, 69 unverified, 1 failed
```

Because the door holds no policy, calling a script directly and calling it
through the door answer the same way, and a fixture holds that. Adding
another script under `windows/` requires no change to classification,
dispatch or the boundary scan.

## The governance plane: ownership and effect are different questions

`classify` answers who owns this change, which decides the tag and the CI
jobs. `tool/dispatch/select` answers which checks this change could alter,
which decides the local units. One function answering both is what made a
one-line edit to `assets/zellij/config.kdl` run a whole flake evaluation over
a file Nix never parses.

```text
LOCAL      change ─> classify ─> dispatch/select ─> pre-commit ─> pre-push
                     ownership    effect            format, lint,  unixlike:test
                                                    payloads and   windows:*
                                                    the scans
           evidence has three states: 0 verified, 69 unverified, anything
           else failed, and a failure outranks an unverified result

CI         PR to dev ─> classify ─> repository | unix | windows | secrets
                        scope only   fixtures    flake   native     scans
                                                 eval    pwsh
                                       └────────> Required checks <────┘
           REQUIRE_NATIVE=1, so 69 fails the merge gate

RELEASE    dev ─PR, merge commit─> master ─> <domain>-vYYYY.MM.DD
                                              annotated, the only record
                                                    │
                                              activation / Apply
                                              on explicit request only
```

The last arrow is policy, not flow. Everything up to the tag is automatic;
nothing makes activation or Apply follow from evidence.

## The asymmetry, and what it costs per location

This is measured rather than felt. `tool/version-control/domain-reads`
enumerates Unix-like code in its header by hand — `flake.nix`, `Justfile`,
`.envrc`, `modules/`, `tool/checks/`, `tool/darwin/` — and writes Windows
code as `windows/`. The same enumeration is repeated in `classify` and in
`tool/dispatch/select`.

```text
add windows\tools\New.ps1      add a new Unix-like location
  windows/* already answers      classify         8th pattern
  nothing to edit                dispatch/select  the same list again
                                 domain-reads     the same list a third time
                                 + the CI workflow, the documents, a registry
                                 entry; miss one and the path is silently
                                 unclassified
```

Entry-point fragmentation is a symptom of this, not a cause. Windows could
gather its commands behind one door because `windows/` already existed as a
physical boundary; the Unix-like domain is the repository root, so it rewrites
that boundary as text everywhere it is needed.

```text
operator ─┬─> layer 1  pre-Nix POSIX sh   tool/setup, tool/doctor.sh <scope>
          ├─> layer 2  dev shell          Justfile, 37 recipes, only inside
          │                               nix develop
          ├─> layer 3  domain tools       tool/darwin/karabiner,
          │                               tool/checks/*, each with its own
          │                               argument convention
          └─> layer 4  repository tools   tool/version-control/commit
                                            brew, cask, mas, capture karabiner
                                          just karabiner-capture calls it, and
                                          it edits modules/darwin-homebrew.nix
                                          and assets/karabiner/*.json
```

The layers themselves are justified: `doctor.sh` has to run before Nix
exists, and `just` lives only inside the development shell. What is not
written down anywhere is where each layer's boundary falls, and the calls
that cross a layer also cross a scope.

## What this document does not say

It draws the tree as it was read and proposes nothing. Three questions were
open when it was written, and the study beside it takes them up: what the
target layout is, what becomes of the `Justfile`, and whether the name `tool/`
stays, which appeared 718 times in the tree.

One thing was already breaking. The `Justfile`'s `_home-target`,
`_darwin-target` and `_nixos-target` each carry
`assert builtins.length names == 1`. A typed NixOS host inventory gives the
nixos output a second host and all three fail together: the target axis is
already class by host rather than four flavours.

Read from the tree itself: `tool/version-control/classify`,
`tool/dispatch/select`, `tool/version-control/domain-reads`,
`modules/flake/configurations.nix`, `modules/flake/module-classes.nix`,
`windows/win-env.ps1`, `windows/desired/manifest.json`,
`.github/workflows/ci.yml`, `assets/payloads.json`, `invariants/` and
`docs/architecture.md`.
