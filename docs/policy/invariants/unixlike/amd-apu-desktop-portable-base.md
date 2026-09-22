id: unixlike/amd-apu-desktop-portable-base
statement: The physical desktop preserves its reviewed encrypted storage, compressed-memory swap, AMD graphics, desktop networking and recovery shape until physical evidence revises that contract.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: schema unixlike/modules/host/desktop.nix
enforced-by: schema unixlike/modules/installation.nix
enforced-by: schema unixlike/modules/amd-apu.nix
enforced-by: fixture unixlike/tool/checks/flake-test
decision: docs/policy/decisions/unixlike/amd-apu-desktop-uses-labelled-luks-btrfs.md § The portable base names created values, not observed hardware

The committed base describes values the installation creates and portable
AMD support that nixpkgs supplies. It deliberately contains no disk UUID,
controller-specific module, monitor identity or generated hardware file. The
storage side keeps manual unlock of the labelled encrypted container, the
three reviewed Btrfs subvolumes and options, a private labelled EFI mount and
zram without disk swap. The machine side keeps the distribution AMDGPU,
firmware, microcode and Mesa path plus NetworkManager.

The assertions make an override of either half fail evaluation. The fixture
also reads every merged value from the real desktop, rejects representative
storage and graphics violations, and checks the source tree for the observed
hardware values that remain forbidden before physical review. The headless
class separately enforces the key-only SSH and firewall recovery boundary.
