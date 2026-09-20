id: unixlike/orbstack-shared-kernel
statement: A NixOS machine under OrbStack registers no binfmt emulation, because the registry belongs to the kernel it shares with every other machine and with the container engine beside it.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema unixlike/modules/host/orbstack.nix
enforced-by: fixture unixlike/tool/checks/flake-test

An OrbStack machine is a container without a user namespace: its root is
root on the one kernel OrbStack runs, and `binfmt_misc` is that kernel's.
OrbStack registers the entries that let an aarch64 Mac run x86 containers,
masks `systemd-binfmt.service` inside each machine at every boot, and mounts
no `binfmt_misc` there. A machine that declared emulated systems would hand
that masked service entries to register, and the first host on which the
mask is absent — another OrbStack version, a unit started by hand — would
write them into a registry that is not the machine's. It is the rule the
repository already keeps for WSL's distributions, where the shared registry
was broken once and traced for a day.

The class asserts that neither an emulated system nor a registration is
declared. The fixture adds each to the real host and requires the refusal,
and holds the real host to the shape OrbStack needs from a guest.
