id: repository/windows-ci-runtime-bound
statement: Native Windows CI verifies the domain-declared management artifact and fresh process identity, binds direct and nested management execution to that runtime, records inbox bootstrap coverage separately, and refuses failed or unavailable selected checks.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: schema .github/scripts/WindowsCiRuntime.psm1
enforced-by: schema .github/scripts/assert-windows-ci-runtime.ps1
enforced-by: schema .github/scripts/windows-ci.ps1
enforced-by: fixture .github/tests/test-windows-ci-runtime.ps1
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/windows-ci-consumes-domain-runtime.md § Native Windows CI consumes domain-owned runtime identity

Native fixtures cover matching and tampered archives, actual version and
architecture, missing runtime/conflicting nested resolution, successful and failed or
unavailable children, reader refusal, and separate inbox entry/bootstrap
success and refusal. The final head's hosted Windows job supplies native
execution evidence; local foreign checks never substitute for it.

The PowerShell runtime loader and process probe refuse the mismatch; they
are interpreted source, not POSIX executables. Workflow/controller selection
is held by repository wiring fixtures and exercised in the native job.
