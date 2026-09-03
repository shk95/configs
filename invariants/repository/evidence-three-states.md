id: repository/evidence-three-states
statement: A check reports verified, failed, or unverified and nothing else; a failure outranks unverified, and unverified never passes the merge gate.
rationale: docs/architecture.md § Repository governance plane
enforced-by: tool .githooks/pre-push
enforced-by: fixture tool/version-control/test
decision: docs/status.md § Check evidence states

Exit 0, 69 and any other status carry the three answers. `.githooks/evidence`
is the one library that decides what each means; the hooks that source it
are the executables, and `REQUIRE_NATIVE=1` turns 69 into failure in CI.
Call sites that still invent a third state are tracked in the audit, not
excused here.
