# Declare every NixOS host in a typed inventory

kind: spec
date: 2026-09-19
scope: unixlike
status: approved
review-by: 2026-10-31
issue: #289

Agreed with the maintainer in the session of 2026-09-19. Order 4 in
`docs/work/roadmap.md`; it carries issue 18 as the roadmap re-scoped it.

## Problem

1. **The flake can express one NixOS host.** `identity.wsl.hostName` names
   the only `nixosConfigurations` output, `configurations.nix` writes that
   output by hand, `modules.nixos.wsl` is the only NixOS class, and the
   `Justfile` asserts that exactly one output exists. Orders 5 to 9 each add
   a host of another kind, and none of them has a place to declare it.
2. **Nothing says which hosts are legal.** A host's system, kind and
   hypervisor are related — a UTM guest is `aarch64-linux`, a WSL
   distribution is not a `vm` — and no schema holds that relation, so a
   wrong combination would fail late, in a module that assumed the other.
3. **`aarch64-linux` is not an evaluated system.** Three lanes are aarch64,
   and the first change that adds one would also have to change what the
   per-system outputs and the checks cover.
4. **The NixOS state version is a class value.** `state-version.nix` sets it
   on `modules.nixos.wsl`, but it is the release a host was first installed
   with, which is a fact about a host.

## Decisions

### A host is an entry of `identity.nixosHosts`

`identity.nixosHosts.<name>` declares a host; the attribute name is the
output name and `networking.hostName`, so the two cannot differ. An entry
has:

| Field | Type | Meaning |
| --- | --- | --- |
| `system` | `x86_64-linux` or `aarch64-linux` | the platform the host runs |
| `kind` | `wsl`, `orbstack`, `vm` or `desktop` | what the host is, which selects its composition |
| `hypervisor` | `vmware`, `utm` or null | required for `vm`, refused for every other kind |
| `user` | string | the primary account |
| `stateVersion` | string | the NixOS release the host was first installed with |

Only the combinations the lanes name are legal, and any other fails
evaluation with an error that names the host and the combination:

| Lane | `system` | `kind` | `hypervisor` |
| --- | --- | --- | --- |
| wsl-nixos | `x86_64-linux` | `wsl` | — |
| vm | `x86_64-linux` | `vm` | `vmware` |
| utm | `aarch64-linux` | `vm` | `utm` |
| orbstack | `aarch64-linux` | `orbstack` | — |
| desktop | `x86_64-linux` | `desktop` | — |

The schema stays in `identity.nix` and the values in `inventory.nix`
(`docs/policy/decisions/unixlike/identity-contract-values-separated.md`).
Darwin and the standalone home keep `identity.darwin` and
`identity.wsl.user`. `identity.wsl.hostName` is removed. The `wsl` home
classes are written for `identity.wsl.user`, so a host of kind `wsl` whose
`user` differs from it fails evaluation.

Excluded, as issue 18 had it: hardware detection stored in the inventory,
secrets, runtime state, a deployment target (order 11 owns it), and implicit
module discovery.

### Five hosts are declared, four of them as placeholders

The maintainer chose to declare a host for every lane now, so that every
legal combination is a real output the evaluation check reaches, and not
only a fixture. The host names are the lane names, except the registered
distribution, which keeps the name it answers to:

| Host | Lane | State after this work |
| --- | --- | --- |
| `nixos` | wsl-nixos | unchanged: the same toplevel derivation as before |
| `vm` | vm | placeholder |
| `utm` | utm | placeholder |
| `orbstack` | orbstack | placeholder |
| `desktop` | desktop | placeholder |

A placeholder is the least that evaluates to a system: the shared NixOS
fragments, the kind's guest or container module, a boot loader, and a root
and a boot file system named by label (`nixos`, `boot`), the convention the
installing order will create; OrbStack has neither and imports the LXC
container profile. It carries no home, no desktop and no service of its own.
Its `stateVersion` is the release of the pinned nixpkgs, and the order that
first installs the host confirms or corrects it before anything is
activated. A placeholder has evaluation evidence only. No document presents
one as built, booted or installed, and `docs/status/unixlike.md` says so for
each.

Rejected: schema and fixtures only, with `nixos` the only declared host
(the maintainer preferred real outputs); a `kind` enum that grows with each
order (the legal combinations could not be proved here).

### Composition stays in one place, keyed by kind

`configurations.nix` generates `nixosConfigurations` from
`identity.nixosHosts` and holds one explicit table from kind (and
hypervisor) to the NixOS classes and the Home Manager classes that host
receives; a feature file still never names a host
(`INV unixlike/composition-in-one-place`). The classes:

| Class | Reaches |
| --- | --- |
| `nixos.shared` | every NixOS host: host name, state version, the flake-only Nix settings a fragment already writes for every kind |
| `nixos.wsl` | kind `wsl`, as today |
| `nixos.vmware`, `nixos.utm`, `nixos.orbstack`, `nixos.desktop` | their kind, holding the placeholder |

A fragment moves from `nixos.wsl` to `nixos.shared` only where the `nixos`
toplevel derivation is unchanged by the move; anything else waits for the
order that needs it. The host name and the state version are per-host
values, which a class cannot carry, so `configurations.nix` sets them from
the entry and `state-version.nix` and `host/wsl.nix` lose their NixOS
halves.

### `aarch64-linux` is evaluated and never built here

`aarch64-linux` joins `systems.nix`. The evaluation check already reports a
configuration for another platform as `eval ✓ build — targets <system>`,
and no binfmt emulation is registered on a WSL distribution (the roadmap's
constraint). On a NixOS host the check builds only the output that host's
name selects, not every NixOS output of its platform.

### Recipes name their host

`_nixos-target` no longer assumes one output. A recipe that touches the
running system (`_nixos-host` and what calls it) uses the output named after
the current host and refuses when there is none. A recipe that runs anywhere
(`nixos-eval`, `nixos-build`, `nixos-tarball`) takes the host as a required
argument and refuses a name the flake does not export, listing the names it
does; `nixos-tarball` also refuses a host that is not of kind `wsl`, and
`nixos-stage` copies a file and names no output. The maintainer chose a
required argument over a default.

## Increments

1. This spec and its report.
2. The schema, the inventory, the generated composition with the `nixos`
   host alone, `aarch64-linux`, and the fixtures — the `nixos` toplevel
   derivation unchanged.
3. The recipes and the evaluation check's build selection, while one host
   is declared, so that no commit exports several outputs to recipes that
   assume one.
4. The four placeholder hosts and their classes, the decision record and
   `docs/status/unixlike.md`.
5. A `repository` increment: `README.md`, `CONTRIBUTING.md` and
   `tool/doctor.sh` where they show a recipe or assume one NixOS output, and
   `docs/work/roadmap.md`; then the end of the report.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | `identity.nix` declares `nixosHosts` with the five fields; the inventory declares `nixos`, `vm`, `utm`, `orbstack` and `desktop`; `identity.wsl.hostName` is gone and nothing reads it. | evaluation |
| AC2 | Each of the five legal combinations is accepted, and evaluation fails, naming the host, for: a `vm` without a hypervisor; a hypervisor on a kind that is not `vm`; `vmware` on `aarch64-linux`; `utm` on `x86_64-linux`; `wsl` or `desktop` on `aarch64-linux`; `orbstack` on `x86_64-linux`; a system or kind outside the enums; a `wsl` host whose user is not `identity.wsl.user`. Fixtures prove both directions. | evaluation |
| AC3 | For every declared host the output name, `networking.hostName` and the inventory name agree, and `system.stateVersion` is the entry's. | evaluation |
| AC4 | The toplevel derivation of `nixosConfigurations.nixos`, of the standalone home and of the Darwin system are each the same before and after this work. | evaluation |
| AC5 | `unixlike/tool/checks/test` reaches all five NixOS outputs, reports the two aarch64 ones as evaluated and targeting `aarch64-linux`, and fails when one of them fails to evaluate. | evaluation |
| AC6 | `tool/checks/composition` and `tool/checks/import-order` pass with the generated composition, and no feature file names a host or a kind's output. | evaluation |
| AC7 | On a NixOS host the evaluation check builds only the output named after that host; elsewhere it builds none, as before. A fixture proves the selection. | evaluation |
| AC8 | `just nixos-eval <host>` and `just nixos-build <host>` act on the named output; without an argument, or with a name the flake does not export, a recipe refuses and lists the exported names; a recipe that touches the running system refuses on a host whose name is not an output. | native runtime |
| AC9 | `just nixos-build nixos` builds on the WSL host. | build |
| AC10 | A decision record states the inventory, the legal combinations, the placeholders and what they are not evidence of; `INV unixlike/typed-identity` and any new invariant name their enforcement; `docs/status/unixlike.md` states each placeholder as evaluated only; `README.md` and `CONTRIBUTING.md` show the recipes with their argument. | review |
| AC11 | `Required checks` passes on the head of every pull request of this work before it merges. | evaluation |
