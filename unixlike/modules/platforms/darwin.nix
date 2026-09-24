_: {
  modules.darwin.system = {config, ...}: let
    inherit (config.providerIdentity) hostName user;
  in {
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

  modules.homeManager.darwin = {config, ...}: let
    user = config.providerIdentity.user;
  in {
    home = {
      username = user;
      homeDirectory = "/Users/${user}";
    };
  };
}
