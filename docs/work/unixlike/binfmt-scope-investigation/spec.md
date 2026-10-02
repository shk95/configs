# Investigate binfmt registry scope on WSL and OrbStack

kind: spec
date: 2026-09-21
scope: unixlike
status: approved
review-by: 2026-10-05
issue: #322

The maintainer requested evidence for the binfmt uncertainty left by Order 7,
then approved investigating WSL-NixOS through `ssh homewslnix`, Ubuntu through
`ssh homewsl`, and an investigator-created OrbStack container. Ubuntu hosts
live work and must not have its configuration or running services changed.

## Scope and decisions

Read kernel versions, user and mount namespaces, UID maps, binfmt mounts and
entries, service masks, and the repository's registration path. Match the
observations to primary kernel and platform sources. Distinguish observation,
source-derived inference and unknown runtime behavior. This investigates the
existing no-registration rules; it does not change them or reopen Order 7.

WSL commands are read-only: no installation, mount, registry write, service
change, distribution shutdown, Windows configuration change or activation.
SSH sessions and their ordinary process/log activity are unavoidable; no
claim of zero scheduling or logging impact is made. Use short bounded reads
and record inaccessible evidence rather than escalating to host mutation.

On OrbStack, inspect the existing machine and create one unprivileged,
native-architecture disposable container using an existing image where
available. Give it no host bind mounts, host namespaces, extra capabilities,
network access or daemon socket. Remove only the container this work creates;
record any newly pulled image retained. Do not restart existing workloads.
No direct binfmt registration, unregistration or binfmt mount experiment is
included on either platform. A shared-kernel mutation needs a separate
concrete experiment plan and the maintainer's explicit approval.

## Increments

One unixlike investigation increment: establish this spec and a pending report
in the first commit; then collect external host observations and source
review, and carry the evidence and report disposition in subsequent commits
on the same branch. Review and native observations belong to the same
bounded investigation. No configuration, policy or roadmap change is planned.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | WSL-NixOS and Ubuntu have dated, reproducible read-only observations of kernel, namespace, UID map, registry and service state; unavailable reads are explicit, and the evidence supports only the scope actually observed. | native runtime |
| AC2 | The existing OrbStack machine and a disposable unprivileged container have the same observation set where available; container provenance and removal are recorded. | native runtime |
| AC3 | Primary-source review explains registration versus execution lookup and the NixOS/systemd path, with version applicability and source gaps stated; a comparison separates facts, inferences and untested cross-environment behavior. | review |
| AC4 | The report records the executed command boundaries, compares WSL registry state before and after, records container cleanup, and gives the disposition of the existing rules without claiming an unperformed registration experiment or zero incidental SSH impact. | native runtime, review |
