{lib, ...}: let
  inherit (lib) mkOption types;
in {
  options.identity = {
    gitName = mkOption {
      type = types.str;
      description = "Author name shared by the managed Unix-like Git configurations.";
    };

    gitEmail = mkOption {
      type = types.str;
      description = "Author address shared by the managed Unix-like Git configurations.";
    };

    wsl = {
      user = mkOption {
        type = types.str;
        description = "Account managed in the WSL configurations.";
      };
    };

    darwin = {
      user = mkOption {
        type = types.str;
        description = "Account managed by nix-darwin and Home Manager.";
      };
      hostName = mkOption {
        type = types.str;
        description = "Darwin host and computer name.";
      };
      system = mkOption {
        type = types.enum ["aarch64-darwin" "x86_64-darwin"];
        description = "Darwin target platform.";
      };
    };
  };

  config.identity = {
    gitName = "shk";
    gitEmail = "101378576+shk95@users.noreply.github.com";
    wsl.user = "user1";
    darwin = {
      user = "shk";
      hostName = "shk-macbook";
      system = "aarch64-darwin";
    };
  };
}
