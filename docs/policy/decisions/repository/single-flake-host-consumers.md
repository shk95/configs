# One consumer flake owns explicit host declarations and shared inputs
date: 2026-09-30
scope: repository
status: accepted
supersedes: docs/policy/decisions/repository/one-private-host-repository-from-public-template.md
reopen-when: A demonstrated host compatibility or ownership requirement cannot be expressed clearly with shared inputs and independent host deployment.
source: 3d6d945f1a7c32428ae506586eb5b644129e5614:docs/work/unixlike/provider-consumer-contract/spec.md § Single-flake dendritic consumers and delivery boundary
source: docs/work/repository/provider-documentation-alignment/spec.md § Decisions

## Decision

Retain one private `configs-hosts` repository and the public
`configs-host-template` as its one-time starting point. Each consumer uses one
root flake and lock to produce its declared host outputs. Its concern-oriented
flake-parts/import-tree modules define available fragments; each host explicitly
selects its constructor, inputs, native system/home modules and output identity.
Discovery of a fragment does not select it for every host. Internal provider
module classes and paths are not a consumer API.

Use one shared set of provider and selected host-integration inputs, including
SOPS and NixOS-WSL where the consumer needs them. Transition directly to the
shared lock rather than pre-creating older-version inputs for every host.
Concrete compatibility failures require investigation and an explicitly
justified exception; the structure does not promise every host's output stays
byte-identical across a shared input update. Encrypted payloads, keys and
private identities remain outside automatic Nix-module discovery. SOPS is
optional and owned by the host consumer.

A small consumer-owned connection module derives final configurations and
optional comparison declarations from the same explicit host inputs. It
validates its declaration structure without copying provider input types,
defaults or support rules. Native modules are passed to public constructors;
comparison declarations contain module-presence flags, not module bodies.
Output identifiers do not implicitly set hostnames.

The repository and template share a pattern, not mutable composition authority.
The template contains synthetic, non-secret values; an existing private
repository adopts later template changes only by explicit review or copy.
There is no submodule, implicit synchronization or common-domain component.
Host identity, access, storage, boot, hypervisor realization, safety assertions,
installation tools and secret delivery remain consumer-owned.

One lock changes future evaluations together. Builds, activation, deployment
and recovery remain individually selected per host. Evaluation and build
evidence do not authorize activation. Provider delivery, required template
delivery, private source adoption and API release readiness are separate
results; private activation is not a provider completion prerequisite. Record
current delivery gaps in status rather than presenting this decision as proof
that a consumer already adopted it.

## Rationale and cost

This adopts the agreed consumer-structure amendment and replaces the original
per-host-lock choice while retaining repository ownership. Explicit host files
keep their own realization understandable; one input set avoids duplicating
lock maintenance and pretending compatibility partitions already exist.
The cost is that advancing a shared input affects future evaluation of every
declared host, so adoption verifies the affected consumer outputs before
individual deployment. Separate deployment does not restore independent pins.

Rejected: continuing per-host flakes as the default, adding compatibility
inputs without a concrete failure, importing private provider classes,
automatically synchronizing template revisions, or requiring private host
activation before provider completion.
