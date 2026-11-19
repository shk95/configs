id: repository/no-secret-in-history
statement: Credentials are refused before publication. The scan covers incoming side history and merge diffs as well as ordinary commits.
rationale: docs/policy/architecture.md § Desired-state hygiene
enforced-by: tool .githooks/pre-commit
enforced-by: tool tool/version-control/scan-secrets
enforced-by: fixture tool/version-control/test
enforced-by: fixture tool/version-control/test-workflow.py

The secret scan owns detection; the hygiene scan deliberately does not
duplicate it. The commit hook runs the scanner on the staged state when
available. Push requires it before outbound branch updates. Candidate checks
and CI scan incoming patches from the reviewed event base, including merges.
The scanner defines which content is a credential. Fixtures check the patch
stream, the outbound base and the veto when scanning fails or is unavailable.
