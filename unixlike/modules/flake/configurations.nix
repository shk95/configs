# The only place that decides which feature fragments reach each Unix-like
# configuration. Feature files contribute modules; they do not name hosts.
#
# INV unixlike/desktop-not-wsl — `home.desktop` is composed below into the
# Darwin home only; the WSL homes take `shared` and `wsl` and nothing
# graphical, and the headless guest's home takes `shared` alone.
# tool/checks/flake-test is the enforcement.
#
# INV unixlike/composition-in-one-place — this file is that place.
# tool/checks/composition refuses a feature file that names a host flavour
# or forces a class's decision.
#
# `home.agents` — the coding agents — is composed into the NixOS-WSL home
# only; the standalone Ubuntu home and the Darwin home are unchanged by it
# (modules/agents.nix).
#
# INV unixlike/nixos-host-inventory — every NixOS output is generated from
# `identity.nixosHosts`, named after its entry, and told about itself through
# `host` (modules/host/nixos.nix), so the output name, the inventory name and
# `networking.hostName` cannot drift (#191). `nixosCompositions` is the one
# table from a host's kind — for a `vm`, its hypervisor — to the classes it
# receives; a host whose kind has no row does not evaluate.
{
  lib,
  config,
  inputs,
  withSystem,
  ...
}: let
  inherit (lib) attrValues mapAttrs optionalAttrs;
  inherit (config.identity) wsl darwin nixosHosts;
  home = config.modules.homeManager;
  nixos = config.modules.nixos;

  nixosCompositions = {
    wsl = {
      system = [
        inputs.nixos-wsl.nixosModules.default
        nixos.wsl
      ];
      home = [
        home.shared
        home.wsl
        home.agents
      ];
    };

    # A guest that boots itself: what its hypervisor's machine is
    # (modules/host/utm.nix), what makes a headless host reachable, and the
    # shared home alone — nothing graphical, and the coding agents stay on
    # NixOS-WSL.
    utm = {
      system = [
        nixos.utm
        nixos.headless
      ];
      home = [home.shared];
    };

    # Declared and not yet installed (modules/host/placeholder.nix): the
    # kind's own class and no home, until the order that installs the host
    # composes one.
    vmware = {
      system = [nixos.vmware];
      home = [];
    };
    orbstack = {
      system = [nixos.orbstack];
      home = [];
    };
    desktop = {
      system = [nixos.desktop];
      home = [];
    };
  };

  nixosHost = name: host: let
    key =
      if host.kind == "vm"
      then host.hypervisor
      else host.kind;
    composition =
      nixosCompositions.${key}
      or (throw "identity.nixosHosts.${name}: no composition is written for ${key} in modules/flake/configurations.nix.");
  in
    inputs.nixpkgs.lib.nixosSystem {
      inherit (host) system;
      modules =
        composition.system
        ++ [
          inputs.home-manager.nixosModules.home-manager
          nixos.shared
          {
            host = host // {inherit name;};
            nixpkgs.config = config.nixpkgsConfig;
            nixpkgs.overlays = attrValues config.nixpkgsOverlays;
            home-manager = {
              useGlobalPkgs = true;
              useUserPackages = true;
              users = optionalAttrs (composition.home != []) {
                ${host.user}.imports = composition.home;
              };
            };
          }
        ];
    };
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

    nixosConfigurations = mapAttrs nixosHost nixosHosts;

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
