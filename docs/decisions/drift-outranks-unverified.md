# Drift outranks unverified in the check exit status

date: 2026-08-30
scope: windows
status: accepted
source: 9f1e8ce:docs/status.md § Check evidence states

The Windows check now carries the third state itself, and its ranking is a
decision rather than a derivation. `windows/setup.ps1` reports a detection its
host could not decide — today an Appx package whose module will not load — as
unverified instead of as absence, and `Get-WinEnvCheckStatus` is the one place
that ranks the run. The contract is stated in `docs/architecture.md § Windows
domain` and held by `INV windows/check-exit-contract`; this record keeps why the
ranking is a decision. The recorded answer is that drift outranks unverified.
The reason is what the command is for: it answers whether an Apply is needed,
drift is the actionable half of that answer, and a known 2 must not collapse
into a 69. The cost, which the decision accepts, is that 69 is observable only
on a host that has already converged — a host that has never applied reports
`state missing` drift and returns 2, naming the undecided items in its summary
but not in its status. The repository maintainer owns the decision and it is
recorded on the issue that introduced it; the evidence is the Pester fixture
over the whole ranking plus a native `-Check` on an already-applied Windows 10
host.
