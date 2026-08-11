{config, ...}: let
  sshModule = user: {
    # The alias is declarative; keys and known_hosts remain host-owned.
    programs.ssh = {
      enable = true;
      enableDefaultConfig = false;
      settings.local = {
        HostName = "localhost";
        User = user;
        IdentityFile = "~/.ssh/id_ed25519";
      };
    };
  };
in {
  modules.homeManager.wsl = sshModule config.identity.wsl.user;
  modules.homeManager.darwin = sshModule config.identity.darwin.user;
}
