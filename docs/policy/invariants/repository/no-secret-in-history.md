id: repository/no-secret-in-history
statement: Credentials are refused before publication. The scan covers committed content, incoming commit messages, and release tag annotations.
rationale: docs/policy/architecture.md § Desired-state hygiene
enforced-by: tool .githooks/pre-commit
enforced-by: tool tool/version-control/scan-secrets
enforced-by: fixture tool/version-control/test
enforced-by: fixture tool/version-control/test-workflow.py

The secret scan owns detection; the hygiene scan deliberately does not
duplicate it. The commit hook runs the scanner on the staged state when
available. Push requires it before outbound branch and tag updates. Candidate
checks and CI scan patches and messages from the reviewed event base, including
merges and side history. The release writer scans the exact generated annotation
before it creates a tag object. The scanner defines which content is a credential.
Fixtures check those inputs, the outbound base and the veto when the scan fails
or is unavailable.
