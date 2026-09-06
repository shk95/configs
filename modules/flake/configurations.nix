# The only place that decides which feature fragments reach each Unix-like
# configuration. Feature files contribute modules; they do not name hosts.
#
# INV unixlike/desktop-not-wsl — `home.desktop` is composed below into the
# Darwin home only; the WSL homes take `shared` and `wsl` and nothing
# graphical. tool/checks/flake-test is the enforcement.
#
# INV unixlike/composition-in-one-place — this file is that place.
# tool/checks/composition refuses a feature file that names a host flavour
# or forces a class's decision.
#
# The NixOS output is named by the typed identity's host name, as the Darwin
# one is, so `networking.hostName` and the output attribute cannot drift
# (modules/wsl-host.nix, #191).
{
  lib,
  config,
  inputs,
  withSystem,
  ...
}: let
  inherit (lib) attrValues;
  wsl = config.identity.wsl;
  darwin = config.identity.darwin;
  home = config.modules.homeManager;
in {
  flake = {
    homeConfigurations.${wsl.user} = withSystem "x86_64-linux" ({pkgs, ...}:
      inputs.home-manager.lib.homeManagerConfiguration {
        inherit pkgs;
        modules = [
          home.shared
          home.wsl
          home.wslStandalone
        ];
      });

    nixosConfigurations.${wsl.hostName} = inputs.nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        inputs.nixos-wsl.nixosModules.default
        inputs.home-manager.nixosModules.home-manager
        config.modules.nixos.wsl
        {
          nixpkgs.config = config.nixpkgsConfig;
          nixpkgs.overlays = attrValues config.nixpkgsOverlays;
          home-manager = {
            useGlobalPkgs = true;
            useUserPackages = true;
            users.${wsl.user}.imports = [
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
          nixpkgs.overlays = attrValues config.nixpkgsOverlays;
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
