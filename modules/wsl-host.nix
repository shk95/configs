# The NixOS-WSL host's name, read from the typed identity so the name the
# host answers to and the name of its flake output cannot drift (#191);
# modules/darwin-host.nix is the Darwin half of the same rule.
# `wsl.wslConf.network.hostname` defaults to this value, so /etc/wsl.conf
# follows without a second declaration.
{config, ...}: let
  inherit (config.identity.wsl) hostName;
in {
  modules.nixos.wsl.networking.hostName = hostName;
}
