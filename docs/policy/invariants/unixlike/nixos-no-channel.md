id: unixlike/nixos-no-channel
statement: The NixOS host carries no channel, so the only source a rebuild can take is this flake.
rationale: AGENTS.md § Goal and authority
enforced-by: schema unixlike/modules/nix/shared.nix
enforced-by: fixture unixlike/tool/checks/flake-test
decision: docs/policy/decisions/unixlike/nixos-wsl-system-layer-ownership.md § The NixOS-WSL system layer declares only what Home Manager cannot

The flake is the authority for the Unix-like domain. A channel is a second
source of the same system: the imported distribution registered one and
carried a default configuration file beside it, and its welcome text advised
updating the channel and rebuilding, a path nobody maintains and that does
not describe this host. With channels off the search path names the flake's
nixpkgs alone, the channel command is gone, and the tarball builder registers
no channel at import, so a rebuild that names no flake stops on the search
path before it builds anything.

What an activation cannot do is remove the channel and the configuration file
an earlier import already wrote; that is a documented step on the host, once
for the imported distribution and once after every future import.
