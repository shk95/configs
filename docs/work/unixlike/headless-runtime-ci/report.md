# Report: exercise the headless contract in a booted VM

kind: report
spec: docs/work/unixlike/headless-runtime-ci/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Native runtime at `973bec8`: `nix build --no-link --print-build-logs path:./unixlike#checks.x86_64-linux.headless-runtime` booted under QEMU TCG and exited 0 after observing the account, sudo, key-only ssh, root refusal and blocked-port assertions. The build took 4:55.15; the VM script took 277.56 seconds and the successful ssh assertion completed in 22.42 seconds. |

## Cost and recovery observation

The unoptimised fixture passed in 5:16.77 with a measured maximum RSS of
622,212 KiB after a dry run estimated 320.7 MiB of downloads, 1.3 GiB
unpacked and 105 derivations on an empty store. A later forced rebuild under
host load reached the test driver's 300-second shell limit before assertions:
DHCP timeout and RSA host-key generation consumed about 90 seconds. Commit
`018eee4` removed those two fixture-only costs, retained the tested contract
and produced the verified run above. Hosted cost remains the repository work
item's affected-dispatch evidence.

The first hosted run used KVM and reached the successful public-key session in
about 18 guest seconds, but its `ip netns exec` wrapper did not return after
sshd closed the session. The job reached its 60-minute limit. Commit `973bec8`
uses a guest-side marker to prove the remote command ran and bounds wrapper
cleanup with `timeout`; the TCG run above verifies the revised assertion.
