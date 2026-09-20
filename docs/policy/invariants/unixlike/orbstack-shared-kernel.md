id: unixlike/orbstack-shared-kernel
statement: A NixOS machine under OrbStack registers no binfmt emulation, because emulation on the kernel it shares with every other machine and with the container engine beside it is OrbStack's to provide.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema unixlike/modules/host/orbstack.nix
enforced-by: fixture unixlike/tool/checks/flake-test

Every OrbStack machine and OrbStack's Docker run on one kernel, and a
machine's UIDs are mapped one to one, so root in a machine is UID 0 on that
kernel. OrbStack provides the emulation that lets an aarch64 Mac run x86
programs, masks `systemd-binfmt.service` inside each machine at every boot
that was observed, and mounts no `binfmt_misc` there. A machine that declared
emulated systems would hand that masked service entries to register, and the
first host on which the mask is absent — another OrbStack version, a unit
started by hand — would write them.

What is not known is stated, because an earlier version of this entry said
more than was observed. The machine runs in a user namespace that is not the
kernel's initial one (read on 2026-09-20; it is also why the debug file
system cannot be mounted there). On a kernel this recent a `binfmt_misc`
registry belongs to a user namespace, and whether that namespace is one
machine's or all of OrbStack's could not be read from inside. So a
registration made here might reach another machine's registry or might not.
The rule does not depend on the answer: the machine has no use for a
registration of its own, and it is the care the repository already takes for
WSL's distributions, where the shared registry was broken once and traced
for a day.

The class asserts that neither an emulated system nor a registration is
declared. The fixture adds each to the real host and requires the refusal,
and holds the real host to the shape OrbStack needs from a guest.
