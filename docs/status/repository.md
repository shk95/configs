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

On 2026-10-07 the maintainer-authorized cutover replaced old remote dev
b8e9273 and master 6c60f37 with the reset-based candidate and master basis.
The first normal promotion was accepted through
[PR #546](https://github.com/shk95/configs/pull/546), with all selected native
jobs and Required checks successful. Actual merge parents/tree were confirmed.
Its master merge history was reflected into dev without source reauthoring.

Dev protection now permits ordinary push without PR/required checks or
conversation resolution. Master retains strict Required checks and protected
merge-commit PRs with zero required approvals. Both enforce administrators
and prohibit everyday force pushes/deletion. Automatic and manual input patch
operation and its schedule are enabled again; no new patch publication or
actual scheduled trigger is certified by the source promotion.

Cancelled conditional-merge/qualification issues and PRs were retired. Related
topic/backup/reconstruction branches and worktrees were reclaimed after a
verified recovery archive preserved their history and dirty/checkpoint data.
Current remote facts are checked explicitly for remote operations, not cached
as prerequisites of local development. Operational documentation can complete
on dev without another immediate master promotion.

## Input patch and domain boundaries

The independent master-based automatic/manual input patch function remains.
It refreshes only inputs from unixlike/automatic-refresh-inputs.json, validates
the exact PR/merge and preserves immutable tags and original publication
recovery. General development, Windows publication and host activation/Apply
are separate. Manual qualification never proves the scheduled trigger.

Domain ownership and current host/native evidence remain in the domain status
files. A repository change has no configuration output or domain release tag.
