# Current state: repository

## Local workflow redesign

The adopted direction is local development completion with later optional
push and protected master acceptance:
docs/policy/decisions/repository/local-development-workflow.md.
Implementation and evidence are recorded in
docs/work/repository/local-development-workflow/report.md.

The reconstruction basis is reset dev 0fc573e and master 60bcd46. The accepted
Unix-like input patch/tag at master is retained. The backup conditional merge,
base-drift and qualification flow is not an active dependency. Existing
worktrees and uncommitted extraction data are preserved; Agent Rack is outside
this redesign. Historical reconstruction and host evidence are not rewritten.

## Remote adoption

Remote cutover has not yet been performed. The 2026-10-07 captured remote
tips were dev b8e9273 and master 6c60f37; these are snapshots, not a live
assertion. Existing remote dev PR/check gates and old workflows remain until
the explicitly reviewed one-time ref/settings transition. Local source is not
proof that GitHub already runs the new policy.

The intended protection is ordinary dev push without PR/required checks or
conversation resolution; master retains strict Required checks and protected
merge-commit PRs with zero required approvals. Both enforce administrators
and prohibit everyday force pushes/deletion. Live gate, writer and scheduled
evidence are recorded operationally, separately from local implementation.

## Input patch and domain boundaries

The independent master-based automatic/manual input patch function remains.
It refreshes only inputs from unixlike/automatic-refresh-inputs.json, validates
the exact PR/merge and preserves immutable tags and original publication
recovery. General development, Windows publication and host activation/Apply
are separate. Manual qualification never proves the scheduled trigger.

Domain ownership and current host/native evidence remain in the domain status
files. A repository change has no configuration output or domain release tag.
