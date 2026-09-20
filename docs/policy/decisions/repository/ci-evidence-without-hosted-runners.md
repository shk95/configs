# CI runs the suites and adds no hosted runner

date: 2026-08-16
scope: repository
status: accepted
reopen-when: a defect class a hosted runner would have caught occurs twice, or an installed x86_64 NixOS guest declares behaviour of its own — an account, a service, a port — for a VM test to assert
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

2026-09-20: The second condition came true in its letter when the typed
inventory gave the flake NixOS outputs beside the WSL one
(`docs/policy/decisions/unixlike/nixos-hosts-declared-in-typed-inventory.md`),
and the repository maintainer judged it: no runner is added. The four new
hosts are placeholders, the least that evaluates for their kind, so a VM test
would boot a system that declares nothing to assert; the two aarch64 ones do
not run on a hosted x86_64 runner at all; and evaluation, which the merge
gate already performs for every output, is the whole of their evidence. The
first condition has not occurred: the one failure the gate caught in that
work was a fixture flake missing an attribute the gate's Nix reads, a defect
of the verification machinery. The condition is restated above so that it
fires when a test would have something to prove.
