# CI runs the suites and adds no hosted runner

date: 2026-08-16
scope: repository
status: accepted
reopen-when: the required headless VM check becomes unreliable or makes ordinary Unix-like changes impractical, another installed host gains runtime behaviour a hosted test can assert, or a defect class an additional hosted runner would have caught occurs twice
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

2026-09-21: The installed VMware guest gave the generic headless class the
account, ssh and firewall behaviour the second condition required. The
maintainer accepts one minimal `runNixOSTest` check in the existing required
Unix-like job. It imports the real shared and headless classes, uses one guest
and a network namespace, and keeps the faster evaluation fixture for its
positive and negative declaration coverage. No runner or workflow is added.

The final local TCG run took 4:55.15, of which the VM script took 277.56
seconds. The first hosted KVM run reached the successful public-key session
but exposed a test-harness defect: `ip netns exec` did not return after sshd
closed the session, so the job reached its 60-minute limit. A guest marker now
proves the remote command ran and a timeout bounds wrapper cleanup. The next
hosted run passed, and the up-to-date-base run
[`35571092957`](https://github.com/shk95/configs/actions/runs/35571092957)
passed the required workflow in 8:30; its Unix-like job took 8:06 and
`unixlike/tool/checks/test` took 3:01. That cost is accepted for Unix-like pull
requests. This is affected-dispatch evidence for the generic headless contract,
not VMware native-runtime or activation evidence. The consumed condition is
replaced above with the circumstances that would require another judgement.

2026-09-26: documentation-only PR #392 paid a 13:02 Unix-like job (run
36109055733), versus 12:42 for lock refresh #408 (run 36216060416). The
maintainer accepts CI effect selection: ownership still selects policy-scan
scope, but documents do not select platform suites. Actual platform inputs
still require their complete native suite; shared dispatch changes exercise
all suites. This amends the ownership-only condition in the opening paragraph,
not the runtime guarantees of a selected suite. Internal suite optimization and
safe removal of PR/push repetition remain separate work; a successful PR is
not evidence for a changed integration tree.
