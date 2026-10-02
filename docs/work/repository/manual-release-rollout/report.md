# Report: manual release operating cycle
kind: report
spec: docs/work/repository/manual-release-rollout/spec.md
status: pending

## Preparation observations, 2026-10-02

Root inspected dev 1a0e39c1a36b915c0dc162506603ef37ce726ec2 and actual postmerge CI
run 36954521862, which completed successfully. The maintainer selected a separate
private operating repository and its creation succeeded; its numeric identity and
empty initial state were observed independently. No operating branch or bootstrap
record was initialized. Root created the dedicated public Environment and verified
its selected branch policy contains only branch master. The selected private locator was stored as an Environment secret. No token,
wrapper dispatch, source promotion, domain tag, private operating record or schedule was created.
These are setup observations, not isolation/permission/bootstrap certification.

The maintainer will issue and store the dedicated fine-grained token directly.
Its actual access, denial and expiry behavior remain unverified. The legacy Windows
capture-publish issue was disposed as superseded because the current Windows status
explicitly retires that flow; no old native scenario was newly claimed.

All operating child criteria remain pending. Parent manual0/14 and scheduled0/5 remain
pending; the successful source CI cannot replace actual operating evidence.

## Credential qualification source, 2026-10-02

The user stored the dedicated token directly. Metadata inspection confirmed its
presence; no token value is retrievable and no actual token request is claimed.
The separate source probe has only fixed-host GET requests and binds observed run,
source, actor, workflow and sole job before reading required protection/check data.
The public Checks observation is anonymous; Checks is not a token selection
prerequisite. A denial probe reads only repository secret metadata, never values.
Output carries public source/run plus fixed booleans, not private identities.

Sixteen local Python 3.13 fixtures passed, with fake endpoints only. Native Windows
and final policy CI evidence will be recorded before source delivery is Ready.
Actual probe execution awaits accepted master source; no private operating record,
wrapper, bootstrap, mutation permission, dispatch or enablement is certified here.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | Repository and Environment prepared; actual deployed source, bootstrap and credential observations still missing. |
| AC2 | pending | |
| AC3 | pending | |
| AC4 | pending | |
| AC5 | pending | |
| AC6 | pending | |
| AC7 | pending | Local 16 source fixtures passed; policy review and native CI pending. |
