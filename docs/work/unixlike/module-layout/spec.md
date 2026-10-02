# Group Unix-like modules without changing composition

kind: spec
date: 2026-09-24
scope: unixlike
status: approved
review-by: 2026-11-24
issue: #367

The maintainer chose on 2026-09-24 to put a physical module grouping ahead
of the unfinished host roadmap. The proposed file mapping and the older
decision's original context are in the study beside this spec.

## Problem

`unixlike/modules/` has 37 top-level `.nix` files alongside concern
directories. A reader has to scan program settings, machine facts, desktop
services and system foundations together. The existing concern-first rule
keeps a feature's fragments and payloads together but does not make those
larger roles visible. The upcoming external host API makes the distinction
between machine-kind facts and host instances especially important.

## Decisions

Use `flake`, `machines`, `platforms`, `foundation`, `desktop` and `programs`
as navigation groups inside the one `unixlike/modules/` tree. The study
assigns every current concern to one group and calls out ambiguous cases
for review. A concern with multiple Nix fragments or sidecar material keeps
one inner directory. A group name does not select a module class, a platform
flavour or a host. `flake/configurations.nix` remains the only file deciding
which classes reach a host during this work.

The accepted concern-first decision arose when separate root-level modules,
assets and tools were brought under `unixlike/`. Review that historical
argument and replace only its first-level placement rule with the grouped
navigation contract. Do not restore a class-first `darwin/nixos/hm` tree or
move Unix-like content outside the domain.

Keep this move separate from exporting the provider API and from removing
real host instances. The current seven outputs are the comparison baseline.

## Increments

1. Review the file inventory, decision change and move plan. Record current
   output derivation paths and the literal path consumers before editing.
2. Move each concern and its payloads, update paths and declarations, and
   verify all seven outputs, payload parsers and import-order independence in
   the Unix-like evaluation lane.
3. In a separate repository-scope increment, update active paths in CI and
   repository-owned policy and procedure; leave dated historical work
   evidence at its original referent.
4. Run affected native builds if any output changes or a relocated source
   affects a build; review every difference before the report ends.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Every current module concern has one documented destination and its Nix fragments, payloads and scripts stay together; no Nix file is lost or collected twice. | review, evaluation |
| AC2 | Directory names do not select classes or hosts, and only the existing composition boundary chooses classes for a host. | evaluation |
| AC3 | All 16 source payloads are declared at their new paths and parsed by their declared consumers; literal and relative path references to moved files resolve. | evaluation, review |
| AC4 | All seven current host outputs evaluate after the move; any changed derivation path is explained by a reviewed content or ordering difference rather than assumed harmless. | evaluation, review |
| AC5 | Composition and import-order positive and negative fixtures pass on the grouped tree. | evaluation |
| AC6 | The concern-first decision, architecture description and current-state document describe the grouped layout and preserve the domain and class-composition boundaries. | review |

## Excluded

No external provider API, new host instance, secret handling, flake-input
refresh, release or activation belongs to this work.
