# The only place that decides which feature fragments reach each Unix-like
# configuration. Feature files contribute modules; they do not name hosts.
#
# INV unixlike/desktop-not-wsl — `home.desktop` is composed below into the
# Darwin home only; the WSL homes take `shared` and `wsl` and nothing
# graphical. tool/checks/flake-test evaluates that.
{
  config,
  inputs,
  withSystem,
  ...
}: let
  wslUser = config.identity.wsl.user;
  darwin = config.identity.darwin;
  home = config.modules.homeManager;
in {
  flake = {
    homeConfigurations.${wslUser} = withSystem "x86_64-linux" ({pkgs, ...}:
      inputs.home-manager.lib.homeManagerConfiguration {
        inherit pkgs;
        modules = [
          home.shared
          home.wsl
          home.wslStandalone
        ];
      });

    nixosConfigurations.wsl = inputs.nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        inputs.nixos-wsl.nixosModules.default
        inputs.home-manager.nixosModules.home-manager
        config.modules.nixos.wsl
        {
          nixpkgs.config = config.nixpkgsConfig;
          home-manager = {
            useGlobalPkgs = true;
            useUserPackages = true;
            users.${wslUser}.imports = [
              home.shared
              home.wsl
            ];
          };
        }
      ];
    };

    darwinConfigurations.${darwin.hostName} = inputs.nix-darwin.lib.darwinSystem {
      inherit (darwin) system;
      modules = [
        inputs.home-manager.darwinModules.home-manager
        config.modules.darwin.system
        {
          nixpkgs.config = config.nixpkgsConfig;
          home-manager = {
            useGlobalPkgs = true;
            useUserPackages = true;
            users.${darwin.user}.imports = [
              home.shared
              home.desktop
              home.darwin
            ];
          };
        }
      ];
    };
  };
}
