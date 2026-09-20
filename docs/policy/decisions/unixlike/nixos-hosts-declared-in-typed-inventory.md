# NixOS hosts are declared in a typed inventory

date: 2026-09-19
scope: unixlike
status: accepted
issue: #18
reopen-when: A host lane is added or retired, or a host needs a field the entry cannot carry without storing detected hardware.
source: docs/work/unixlike/nixos-host-inventory/spec.md § Decisions

The flake could express one NixOS host: `identity.wsl.hostName` named the
only output, the composition wrote that output by hand, and the recipes
asserted that exactly one existed. The roadmap adds a VMware guest, a UTM
guest, an OrbStack machine and a desktop, and none had a place to be
declared or a rule saying which declarations are legal.

## A host is an entry of the inventory

`identity.nixosHosts.<name>` declares a host's system, its kind, for a `vm`
its hypervisor, its primary user and the NixOS release it was first
installed with. The attribute name is the output name and the host name, so
they cannot differ, and every `nixosConfigurations` output is generated from
an entry. The schema and the values stay in two files
(`docs/policy/decisions/unixlike/identity-contract-values-separated.md`).
Darwin and the standalone home keep the identity they had. A host learns its
own entry through the `host` option of `modules.nixos.shared`, so a fragment
that needs a per-host value reads it inside the NixOS evaluator and still
names no host. The entry stores no detected hardware, no secret, no runtime
state and no deployment target.

## Only the combinations the lanes name evaluate

x86_64 `wsl`; x86_64 `vm` on `vmware`; aarch64 `vm` on `utm`; aarch64
`orbstack`; x86_64 `desktop`. Any other combination, and a `wsl` host whose
user is not the account the WSL home classes are written for, fails
evaluation by host name. A guest module written for one platform or
hypervisor would otherwise fail late, in whatever option it assumed.

## Composition is one table keyed by kind

`modules/flake/configurations.nix` maps a kind — for a `vm`, its hypervisor
— to the NixOS classes and the Home Manager classes a host receives, and a
kind with no row does not evaluate. It remains the only file that decides
what reaches a host.

## A host is declared for every lane, four as placeholders

The maintainer chose to declare `vm`, `utm`, `orbstack` and `desktop` now,
named after their lanes, so that every legal combination is an output the
evaluation check reaches and not only a fixture. A placeholder is the least
that evaluates for its kind: the guest or container module and, for a host
that boots from a disk, a boot loader and two file systems named by label,
which is the convention the installing order creates and not a description
of a disk. It has no home. Its account and its state version are
provisional values that the installing order confirms before anything is
activated. A placeholder is evaluation evidence and nothing else: it has not
been built, booted or installed, and no document may present it otherwise.

Rejected: the schema proved by fixtures alone, with the registered
distribution the only declared host; a `kind` enum that grows with each
order, which could not prove the legal combinations when they were decided.

## `aarch64-linux` is evaluated and never emulated

It joins the evaluated systems. An aarch64 host is built natively or on a
remote builder: binfmt_misc on a WSL distribution is shared by every
distribution, so no emulation is registered there. The evaluation check
builds a NixOS output only on the host it is named after, since that is the
only output the host can activate.

## Recipes name their host

A recipe that touches the running system acts on the output named after the
host it runs on and refuses when there is none. A recipe that runs anywhere
takes the host as an argument and refuses, listing the exported names, when
it is missing or unknown. The maintainer chose a required argument over a
default, so that nothing is selected implicitly.

Cost: four outputs exist for machines that do not, every evaluation run
instantiates them, and a reader must know that a declared host is not an
installed one; `docs/status/unixlike.md` carries that statement.
