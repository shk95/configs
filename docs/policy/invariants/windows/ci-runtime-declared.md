id: windows/ci-runtime-declared
statement: The Windows-owned CI runtime contract distinguishes exact management artifact identity from inbox bootstrap coverage and refuses malformed or unsupported declarations before automation consumes them.
rationale: docs/policy/architecture.md § Windows domain
enforced-by: schema windows/tool/read-ci-runtime.ps1
enforced-by: fixture windows/tests/CiRuntime.Tests.ps1
decision: docs/policy/decisions/windows/ci-runtime-is-verification-data.md § CI runtime is Windows-owned verification data

Verification-runtime selection is not a consumer minimum-version or installation
contract. The reader has no host mutation or current-runtime enforcement;
positive and negative fixtures hold that data boundary before repository wiring.
