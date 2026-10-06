# Master-based Unix-like input patch releases
date: 2026-10-06
scope: repository
status: accepted
issue: #525
source: docs/work/repository/master-input-patch/spec.md
reopen-when: Another domain needs its own patch lane or a permitted input patch cannot complete without general development promotion.

## Decision

Restrict automatic and one-call manual operation to the current master Unix-like
permitted inputs: nixpkgs, home-manager, nix-darwin and nixos-wsl. Changes in dev
are independent. Unchanged locks produce no commit, PR or tag. A changed lock
gets the next patch version from master's published Unix-like declaration.
A same-repository input patch branch carries exactly one commit on the current
master, changing only admitted lock data and the fixed patch declaration. It
enters master through a checked PR and merge commit; no direct commit or
protection bypass is introduced. Windows is not read or published by this lane.
A future Windows patch path requires its own explicit design and checks.

Master Unix-like configuration source must match its current published release
before input patching. An accepted but unpublished general change is never
relabelled as an automatic patch, even if its declaration was left unchanged.

General development remains topic-to-dev-to-master and its version declaration
and publication are developer-owned. Before promotion, dev incorporates input
patch history already accepted on master through an ordinary reviewed dev PR.
An actual patch source update may be merged from master into that topic branch;
promotion-only merge commits need not flow backward. Source ancestry preserves
patches while permitting later intentional development changes and versions.

## Operation

One shared workflow serves a daily 05:00 Asia/Seoul schedule, CI completion
continuations and the thin manual dispatch entry. Manual execution waits up to
60 minutes for the one patch PR; scheduled execution releases the runner and
resumes on the next event. The former 06/07 clock stages, daily development
promotion cap and general Environment approval are retired from this lane.
General promotion competes through the one-open-master-PR rule, not by silently
joining the input patch. Active manual runs defer scheduled writes.

Accepted master tooling validates candidate artifacts without granting execution
writer credentials. Only the protected writer obtains release-control
credentials. Current source, Required checks and actual merge parents/tree
must agree. A stale candidate stops and its PR is preserved for inspection.
Interrupted publication completes missing immutable Unix-like tags before any
new refresh; explicit recovery accepts only a known input patch merge reachable
from master and still requires its exact checked PR evidence. Brief read-only
retries tolerate delayed GitHub merge association; invalid proof still refuses.
No state database, automatic source repair or host adoption/activation is added.

## Adoption

This repository policy change follows the existing topic/dev/master route before
the direct patch lane is used. Branch protections remain PR-only, merge-only
and Required-checks gated. Remote Actions qualification and actual schedule
observation remain separate from local fixture proof.
