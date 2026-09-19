# CI runs the suites and adds no hosted runner

date: 2026-08-16
scope: repository
status: accepted
reopen-when: a defect class a hosted runner would have caught occurs twice, or a NixOS host configuration exists for VM tests to target
source: 9f1e8ce:docs/status.md § Windows authority split
source: 9f1e8ce:docs/status.md § CI runners are not added

The merge gate is CI. The `windows-latest` job installs Pester, Lua, and Zellij,
then runs the desired-state check and the Pester suite, and `Required checks`
demands success whenever the change is in Windows scope. A Windows change
authored on Linux or macOS is therefore verified natively at the pull request
rather than locally. `bootstrap.ps1 -Check` stays outside CI because a fresh
runner has no host state to observe; it is host evidence for a `windows-v...`
tag, not a merge condition.

2026-09-03: Measured over 157 CI runs since 2026-08-11: one configuration
defect caught (a lint warning, before the hooks existed), eight failures
that were defects in the verification machinery itself, none in a fixture
that had caught a regression. Every defect found on a host — the Windows
Terminal generated profile, the partial font install, the older PowerToys
keys, the Windows 10 Appx route, the CP949 console — depended on host state
a fresh runner does not have, and `bootstrap.ps1 -Check` is host evidence
for that reason. The decision is to add no runner: no Windows Apply on a
Server runner, no per-run NixOS-WSL closure build, no macOS runner, no VM
test before a NixOS host configuration exists. Build evidence for a
`unixlike-v…` tag is `CHECKS_BUILD_ALL=1 tool/checks/test` on a matching
host.
