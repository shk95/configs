id: repository/bounded-release-automation
statement: Automatic and manual input patch writes use current master with already-published Unix-like configuration source and only the permitted input boundary, match current source and successful checks without development promotion or Windows publication, separate candidate execution from writer credentials, preserve immutable tags, and confirm ambiguous remote writes before continuing.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool tool/version-control/release.py
enforced-by: fixture tool/version-control/test-release.py
owner: repository maintainer
decision: docs/policy/decisions/repository/master-input-patch-releases.md § Operation

The writer rechecks the current branches and PR metadata before the merge and
updates master only if the receiver still holds the reviewed base. The update
contains precisely the reviewed merge parents and tree. It rechecks reachability through
current master while creating an immutable tag that names the verified PR run
and attempt. The same checks govern recovery of the original patch merge.
Losing the original source stops automation until a person identifies its SHA.
Before a proof-format transition, resolve any pending patch publication while
its evidence is still usable and let the paused writer drain.
There is no private execution-state store.
