# Report: provider documentation and consumer topology
kind: report
spec: docs/work/repository/provider-documentation-alignment/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Review on 2026-09-30 compared the successor decision and superseded predecessor with the single-flake consumer amendment at provider merge 3d6d945f1a7c32428ae506586eb5b644129e5614. It preserves one-time template origin, explicit host module selection, shared inputs and individually authorized deployment. No registry decision pointer refers to the predecessor; its remaining status citation is historical. Staged invariants and design-citation checks pass. |
| AC2 | verified | Root usage/workflow/architecture reviewed against that merge's public-environment-host-boundary decision, api/contract.json, configurations.nix, contract-tools.nix, contract-inspect, standalone-readiness and checks/test. Nix-app --help smoke checks pass for both documented apps and their flags. The procedure selects the actually delivered consumer output, not the pending root-flake candidate. Staged hygiene, domain-read and design-citation checks pass. |
| AC3 | verified | Fresh GitHub/source review on 2026-09-30 confirms PR #421 merged at 3d6d945f1a7c32428ae506586eb5b644129e5614 and published private/template main refs f7f3010ca4675f705e8a8895dede19786530b6ca / dcb8c6d81ebd72ca4b19e8364269494ffcbdc5c2 retain hosts/; candidate bootstrap pins remain e11bd1368d2f5138ad0f9b7017040b2b76e055e6. Status preserves the dated earlier adoption and separately states remaining reference alignment, required template delivery, private source migration and release evidence. No activation is inferred or required for provider completion. Policy scans pass. |
| AC4 | verified | Dedicated linked worktree picked up origin/dev at 3d6d945f1a7c32428ae506586eb5b644129e5614. Diff review finds only eight assigned repository documents; the original detached candidate remains at e11bd136 with its same three staged files and 82 additions / 61 deletions. Working-tree and staged work preflights, whitespace, hygiene, domain-read, design-citation, records, invariants and provisional checks pass. Actual staged commit/push dispatch selects no suite; CI dispatch selects repository:fixtures only. |

## Delivery and evidence limits

One repository-only outcome implements the reviewed documentation adoption.
The execution issue is #425; this report records local review, policy and
dispatch evidence, while the delivery PR retains its current-head hook and CI
results. No fixture implementation, enforcement tool or configuration source
changed. CI's selected existing repository fixture suite remains required;
local documentation dispatch does not claim it ran. Configuration evaluation,
configuration builds, native host runtime, activation, Apply and releases are
not applicable to this documentation result.

Consumer revision observations are a dated snapshot, not a continuing claim
that publication cannot advance. Both exact-pair final pins and required
companion delivery remain separately owned. This report completes the
repository documentation work and does not close the provider contract's
remaining U1/companion, U2 capture or release obligations. Maintainer acceptance
and protected dev integration remain separate from worker delivery.
