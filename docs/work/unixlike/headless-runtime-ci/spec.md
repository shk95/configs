# Exercise the headless contract in a booted VM

kind: spec
date: 2026-09-21
scope: unixlike
status: approved
review-by: 2026-10-05
issue: #326

Agreed with the maintainer on 2026-09-21 as the Unix-like increment of
`docs/work/repository/ci-headless-runtime/`. The installed x86_64 VMware guest
now gives the generic headless class real account, ssh and firewall behaviour
for a runtime fixture to exercise.

## Problem

`unixlike/tool/checks/flake-test` evaluates the real headless hosts and refuses
each invalid account, ssh and firewall declaration. That proves the desired
values compose, but it does not boot their services together or send traffic
through the running firewall. A regression between declarations and runtime
could therefore pass the merge gate.

## Decisions

### Boot the real classes

The test imports `modules.nixos.shared` and `modules.nixos.headless`, and takes
its system and user from the typed `vm` inventory entry. It does not import the
VMware host fragment: the test machine runs under QEMU, while VMware tools need
native evidence from the installed VMware guest.

### Use one guest and a network namespace

One guest keeps emulated execution small. A veth peer in a separate network
namespace supplies traffic that crosses the guest's input firewall, so the
test can prove ssh is reachable and another listening port is not without a
second virtual machine.

### Keep credentials disposable

The test writes its key and password only after the guest boots. No credential
or credential hash enters evaluated desired state. It verifies public-key
access to the declared account, password refusal and root refusal independently.

### Run without requiring KVM

The check does not require the Nix `kvm` system feature. QEMU may use KVM where
available and falls back to TCG on a runner that has none. The existing
evaluation fixture remains because it gives faster and more precise refusal
coverage than a runtime test.

## Increments

1. Add the flake check, register it on `INV unixlike/headless-key-only`, record
   its current state and verify the booted runtime criterion.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The x86_64 test boots the actual shared and headless classes, observes the inventory account in zsh and wheel with sudo authentication required, reaches it with a key from outside the firewall, refuses password and root logins, and refuses a non-ssh listening port. | native runtime |
