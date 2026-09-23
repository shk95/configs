# Let NixOS hosts select offered machine profiles

kind: spec
date: 2026-09-23
scope: unixlike
status: approved
review-by: 2026-10-23
issue: #348

The maintainer chose host-selected profiles on 2026-09-23. This first slice
moves the coding-agent class from a fixed NixOS-WSL composition into a typed
host choice. The existing graphical VM and desktop contracts remain required.

## Problem

The composition table fixes every class by machine kind. A second host of the
same kind cannot choose a different optional feature without a new kind or a
host-name condition in the composition file. The inventory carries identity,
so putting feature choices inside it would conflate two contracts.

## Decisions

Machine kinds provide required classes and named optional profiles. A separate
typed `hostSelections.nixos` option records each inventory host's chosen
profiles. The composition file alone validates the choice against that
machine's offerings and turns it into NixOS and Home Manager imports. Every
inventory host has an explicit selection entry, including an empty one.

`agents` is the first optional profile, offered only by the NixOS-WSL machine.
The `nixos` host selects it. UTM, VMware and the physical desktop continue to
require their graphical classes and recovery layer. This is a change in
composition authority, not a request to activate any host.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | Every NixOS host has one typed choice; unknown hosts, unknown profiles, duplicate choices and profiles unavailable to a machine fail evaluation. | evaluation |
| AC2 | Selecting `agents` adds Codex to the NixOS-WSL home and omitting it removes Codex, while feature files still name no host. | evaluation |
| AC3 | All seven existing output derivations remain unchanged after the choices are made explicit. | evaluation |
| AC4 | Architecture, decision, invariant and current state describe the new ownership without claiming activation. | review |

Amended 2026-09-23: AC1, AC2 and AC3 use the defined `evaluation` lane,
and AC4 uses the defined `review` lane. The criteria themselves are unchanged;
the earlier labels named methods within lanes, not valid lane names.

## Excluded

No host activation, flake-input update, release, Windows change
or new profile beyond `agents` belongs to this slice.
