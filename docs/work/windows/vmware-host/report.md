# Report: observe whether a Windows host can run the VMware guest

kind: report
spec: docs/work/windows/vmware-host/spec.md
status: abandoned

Abandoned by the repository maintainer on 2026-09-20, the day the spec was
agreed, before any of it was merged.

**Why.** The guest needs VMware Workstation and runs on it; that does not
make VMware something the Windows domain manages. The domain reconciles what
it deploys. The `vmware` feature the spec describes would have owned no
package and no file, and its whole content was a read-only answer to a
question the maintainer already has: a host without VMware Workstation says
so the moment the guest is started. Against that, the spec added two
precondition types, a way for a precondition not to block Apply, an
invariant, six fixtures and a support boundary row, to be kept for one
program on one host. Nothing in the Windows scope is planned to grow
around the guest. The manual installation is one line of the VMware guest's
own procedure, which belongs to the Unix-like spec of that order.

**How far it got.** The two probes, the refusal of a broken precondition at
load, the non-blocking readiness rule, the `vmware` feature and their Pester
cases were written and passed under PowerShell 7 on the maintainer's host
(Windows 10 build 19044), and the read-only check reported the installed
version with `vmware` added to the recorded selection. None of it was
committed; the branch was discarded.

**What it left.**

- A defect found while observing the check on the host and fixed on its own
  (#304): `windows/tools/setup.ps1` had evaluated no feature precondition
  since feature selection was added, because its loop variable was the
  script's own typed parameter (`INV windows/selected-precondition-evaluated`).
- The refusal of a broken precondition when the manifest loads, kept as a
  change of its own (#305, `INV windows/precondition-declared`), because it
  does not depend on VMware.
- Host observations of 2026-09-20, build 19044, from an elevated shell,
  recorded here because nothing else holds them: WinGet's `winget` source,
  answering from a cached index after a failed refresh, lists no VMware
  Workstation package; `HypervisorPlatform`, `VirtualMachinePlatform` and
  `Microsoft-Hyper-V-All` are enabled; VMware Workstation 26.0.0.25388281 is
  installed, and its installer writes
  `HKLM:\SOFTWARE\VMware, Inc.\VMware Workstation` with `ProductVersion` and
  `InstallPath`, not the `WOW6432Node` key an older installation used.

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | unmet | No `vmware` feature is declared; abandoned. The refusal of an unknown precondition type at load survives on its own, outside this work. |
| AC2 | unmet | The probes were written and passed on the host, and were discarded with the branch. |
| AC3 | unmet | Abandoned. |
| AC4 | unmet | Abandoned. Apply installs and enables nothing for VMware because the domain declares nothing about it. |
| AC5 | unmet | Abandoned; the manifest is unchanged. |
| AC6 | unmet | Abandoned. The manual installation is left to the VMware guest's own procedure. |
| AC7 | unmet | Abandoned. The host observations above were made and are recorded in this report only. |
| AC8 | unmet | Abandoned; `docs/status/windows.md` states no `vmware` feature. |
| AC9 | unmet | The spec's own pull request (#298) passed `Required checks`; no implementing pull request was opened. |
