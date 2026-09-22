id: unixlike/graphical-guests-keep-recovery
statement: Each self-booting VM guest retains its hypervisor integration and key-only recovery layer while consuming the shared graphical environment.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: schema unixlike/modules/host/utm.nix
enforced-by: schema unixlike/modules/host/vmware.nix
enforced-by: fixture unixlike/tool/checks/flake-test
decision: docs/policy/decisions/unixlike/vm-guests-share-the-graphical-profile.md § Composition owns the shared environment

The UTM and VMware guests share Niri and Noctalia but do not stop being
recoverable virtual machines. UTM retains the QEMU guest service and both
console routes. VMware retains the full open-vm-tools integration. Both keep
the account, key-only SSH daemon and one-port firewall of the headless class.

Each hypervisor class asserts its merged system shape, so removing its own
integration or either shared layer is an evaluation failure. The fixture
reads the real guests, replaces one defining property of each in turn and
requires both violations to be refused.
