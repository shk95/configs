# Native Windows CI consumes domain-owned runtime identity
date: 2026-09-30
scope: repository
status: accepted
reopen-when: A supported hosted Windows check cannot consume the declared artifact or preserve explicit process identity and separate bootstrap coverage.
source: docs/work/repository/windows-ci-runtime/spec.md § Problem and decision

Repository CI consumes the Windows-owned verification declaration and reader.
It chooses neither a second platform version nor a minimum consumer runtime.
The hosted image's existing PowerShell may run the trusted reader and acquire
the declared official ZIP. After SHA256 verification and runner-local temporary
extraction, fresh children must match the declared management version,
architecture and executable. Failed acquisition or identity proof refuses the
job; unavailable evidence cannot pass the stable Required checks gate.

Management orchestration, contributor setup, validation and full tests use
the selected executable explicitly. Its directory keeps PATH precedence when
setup or package installation refreshes machine/user PATH, and a fresh native
probe verifies nested pwsh resolves that same executable. Child status is read
immediately; a later successful command cannot erase failure or exit 69.

Inbox bootstrap coverage is a separate native child lane. Fixtures execute the
declared Windows entry/bootstrap source under that engine with controlled
dependencies for success, refusal and forwarded management-child failure.
They do not Apply desired state or use management version proof as inbox
evidence. A hosted server runner does not certify the separately named client
support baseline, private host behavior or activation.

Internal workflow scripts are CI implementation, not a new operator command.
They read only the selected Windows interface and exercise its own scripts;
Windows tests still own parsing their tree and do not read Unix-like source.
No maintainer-host runtime installation, private runner enrollment, new release
controller or runtime-result reuse is introduced.

Rejected: inheriting management version from the hosted image, duplicating
the Windows version selector in workflow data, trusting ZIP naming without
hash/process proof, PATH-only management invocation, or merging management
and inbox bootstrap evidence into one runtime claim.
