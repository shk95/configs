id: repository/bounded-release-automation
statement: Automatic and manual input patch writes use current master and only the Unix-like permitted input boundary, match current source and successful checks without development promotion or Windows publication, separate candidate execution from writer credentials, preserve immutable tags, and confirm ambiguous remote writes before continuing.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool tool/version-control/release.py
enforced-by: fixture tool/version-control/test-release.py
owner: repository maintainer
decision: docs/policy/decisions/repository/master-input-patch-releases.md § Operation

The five properties are the complete initial operating obligation. Recover one
unfinished input patch publication, then continue. Losing the original source stops automation
until a person identifies its SHA. There is no private execution-state store.
