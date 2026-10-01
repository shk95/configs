# Release controller preview boundary
date: 2026-09-30
scope: repository
status: accepted
reopen-when: Authenticated live operating transport or scheduled enablement is proposed.

## Decision

Deliver a disabled, synthetic-input repository controller before operating rollout.
Its operator entry is an explicit preview; its endpoint adapter interprets supplied
transcripts and constructs proposed requests without HTTP or credentials. Its
master-only workflow is inert and carries no schedule, secret or Environment.
The fixture package needs a functional standard-library Python >=3.9, independently
of Nix; CI supplies an explicit runtime and native Git-for-Windows proof.

Retained batches execute their exact approved package and complete executing
dependency manifest, including the release-preview engine/rules and classifier.
Current entry code may verify and load it but never silently substitute current
decision, approval or serializer dependencies. Synthetic approved-master assertions
exercise that boundary, without authenticating production approval/provenance.
Unknown compatibility or incomplete identity refuses.

2026-10-01: current semantic protocol 2 adds finite refresh outcomes and separate
refresh-branch/refresh-pr proposals targeting dev. Promotion keeps its original
dev-to-master meaning. Supported protocol 1 retains its exact historical code,
records and eight-file executing closure. The stable loader admits only explicit
supported protocols and does not substitute newer semantics for old batches.
Actual trusted CLI/local Git preparation runs exclusively in credential-free
disposable fixtures, outside retained preview execution. Bound preparation DTOs
are synthetic assertions; strict validation is not source authentication.
The fixture adopts the delivered domain utility explicitly rather than copying
selection logic. CI selects the existing Nix-enabled lane for affected controller
or preparation-fixture inputs, alongside Linux/native-Windows fake governance
proof. Nix is not a Windows prerequisite and no production transport is added.

## Limits and authority

Existing calendar tags, promotion authorization and host boundaries remain in
force. There is no production semantic release adoption, live controller or
credential authorization here. Fixture completion cannot certify real actor,
endpoint permission, ref/Environment isolation, protection or notification receipt.
Generation checks are not external API fencing and head matching is not base CAS.

The source work is described in `docs/work/repository/release-controller/spec.md`.
Its parent retains affected-domain and live manual/scheduled obligations. A later
operating proposal must be reviewed separately rather than turning a preview flag
into permission to mutate.
