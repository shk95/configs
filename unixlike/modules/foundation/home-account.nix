# Which account this home belongs to, and the tool that manages it.
#
# Standalone only: the integrated system owns account identity and installs
# Home Manager itself. The constructor supplies the standalone home directory.
_: {
  modules.homeManager.standalone = {config, ...}: let
    user = config.providerIdentity.user;
  in {
    home = {
      username = user;
    };

    programs.home-manager.enable = true;
  };
}
