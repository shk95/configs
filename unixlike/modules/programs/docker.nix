# The NixOS-WSL host runs its own Docker Engine. Standalone Ubuntu WSL owns
# its Engine outside Home Manager, and the other NixOS hosts do not compose
# this class.
_: {
  modules.nixos.wsl = {config, ...}: {
    virtualisation.docker.enable = true;
    users.users.${config.host.user}.extraGroups = ["docker"];
  };
}
