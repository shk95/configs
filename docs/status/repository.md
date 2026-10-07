# Current state: repository

## Local workflow redesign

The adopted direction is local development completion with later optional
push and protected master acceptance:
docs/policy/decisions/repository/local-development-workflow.md.
Implementation and evidence are recorded in
docs/work/repository/local-development-workflow/report.md.

The separate first-parent lanes continue from dev 0fc573e and master 81229c1.
The accepted Unix-like input patch/tag at master 60bcd46 is retained. Master
synchronization uses a dev-based no-ff merge; dev continues on its own lane
after protected master promotion. The backup conditional merge, base-drift and
qualification flow is not an active dependency. Cancelled workspace history
and uncommitted extraction data were preserved in verified recovery archives
before cleanup; Agent Rack is outside this redesign. Historical reconstruction
and host evidence are not rewritten.

## Remote adoption

On 2026-10-07 the maintainer-authorized cutover replaced old remote dev
b8e9273 and master 6c60f37 with the reset-based candidate and master basis.
The initial promotion through [PR #546](https://github.com/shk95/configs/pull/546)
passed its selected native jobs and Required checks, but its topology advanced
dev onto the master lane. That topology was superseded by the maintainer's
history-only correction through [PR #547](https://github.com/shk95/configs/pull/547).
The corrected merge 8698a8b has first parent 60bcd46 and second parent 4e6cd4a.
Its exact-source CI and Required checks passed, and actual merge parents/tree
were confirmed. At that transition both branch trees exactly matched their
pre-correction trees, published tag objects were unchanged, and dev continued
on its own lane. Subsequent master synchronization follows the amended procedure.

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
