# Report: daily provider refresh before promotion
kind: report
spec: docs/work/repository/scheduled-flake-refresh/spec.md
status: pending

## Planning delivery clarification, 2026-09-30

The pickup clarification distinguishes independent fake-interface fixture preparation
from final scheduler wiring after the actual refresh tool and shared controller are
delivered. B owns planning continuation only; no scheduler/controller implementation
owner, issue, PR, credential or live schedule is created by this review. Acceptance
and all pending rows are unchanged. Document preflight is form validation only.

## Current controller alignment, 2026-09-28

Cross-work reconciliation supersedes the earlier App proposal and design deferral:
one PAT/shared master controller, Actions write for bounded cancel, failure/action
notifications, credential-free retries and 05/06/07 KST apply. The refresh tool and
trusted-controller wiring are explicit implementation dependencies. No App/PAT,
workflow, schedule or remote operation was provisioned. All rows remain pending.

Implementation and live schedule evidence remain pending. Planning preflight
verifies format only.

2026-09-27: retained as an earlier draft, with pickup deferred by the dated
spec amendment. Continue from provider-release-contract/study.md for stages
2 and 3; no automation or credential provisioning has been performed.

2026-09-28: AC1/AC4/AC5 now specify daily 08:00 KST refresh before promotion,
the one-hour refresh-wait limit, and designated compatible-patch dev admission.
The earlier twice-daily/non-merging-controller design is superseded in those
respects. No automation, credential or remote operation was performed; all
acceptance rows remain pending.

2026-09-28 continuation: AC5 now includes the accepted public-controller/private-
records boundary, opt-in behavior, emergency stop/resume and action-only alerts.
These are planning requirements; no private connection or scheduled run exists
as evidence for this work item.

## Later operating agreement, 2026-09-28

The later amendment adopts 05:00 refresh, 06:00 promotion and 07:00 cutoff
(Asia/Seoul), termination-confirmed takeover, intent/result reconciliation,
exact candidate/approval binding, merge-result checks and delayed/missed-run
handling. Failure fixtures remain required, including alert deduplication and
both permitted and refused progress. No separate watchdog is required. All
implementation and live evidence remains pending; no row is verified here.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | pending | |
| AC2 | pending | |
| AC3 | pending | |
| AC4 | pending | |
| AC5 | pending | |
