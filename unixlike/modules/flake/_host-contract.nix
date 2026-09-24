{lib}: let
  inherit (lib) mkOption types;
  legalHosts = [
    {
      system = "x86_64-linux";
      kind = "wsl";
      hypervisor = null;
    }
    {
      system = "x86_64-linux";
      kind = "vm";
      hypervisor = "vmware";
    }
    {
      system = "aarch64-linux";
      kind = "vm";
      hypervisor = "utm";
    }
    {
      system = "aarch64-linux";
      kind = "orbstack";
      hypervisor = null;
    }
    {
      system = "x86_64-linux";
      kind = "desktop";
      hypervisor = null;
    }
  ];
  describe = host:
    "${host.system} ${host.kind}"
    + lib.optionalString (host.hypervisor != null) " on ${host.hypervisor}";
in {
  hostType = types.submodule {
    options = {
      system = mkOption {type = types.enum ["x86_64-linux" "aarch64-linux"];};
      kind = mkOption {type = types.enum ["wsl" "orbstack" "vm" "desktop"];};
      hypervisor = mkOption {
        type = types.nullOr (types.enum ["vmware" "utm"]);
        default = null;
      };
      user = mkOption {type = types.str;};
      stateVersion = mkOption {type = types.str;};
    };
  };

  checkHost = {
    name,
    host,
    wslUser,
  }:
    if !(lib.elem {inherit (host) system kind hypervisor;} legalHosts)
    then
      throw ''
        identity.nixosHosts.${name}: ${describe host} is not a host this repository configures. The legal combinations are: ${lib.concatMapStringsSep "; " describe legalHosts}.''
    else if host.kind == "wsl" && host.user != wslUser
    then
      throw ''
        identity.nixosHosts.${name}: a host of kind wsl receives the WSL home classes, which are written for identity.wsl.user (${wslUser}), and declares ${host.user}.''
    else host;
}
