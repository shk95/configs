{config, ...}: let
  inherit (config.identity.darwin) hostName user;
in {
  modules.darwin.system = {
    networking = {
      inherit hostName;
      computerName = hostName;
    };
    system.defaults.smb.NetBIOSName = hostName;
    users.users.${user} = {
      description = user;
      home = "/Users/${user}";
    };
  };

  modules.homeManager.darwin = {
    home = {
      username = user;
      homeDirectory = "/Users/${user}";
    };
  };
}
