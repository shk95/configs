# The only place that decides which feature fragments reach each Unix-like
# configuration. Feature files contribute modules; they do not name hosts.
#
# INV unixlike/desktop-not-wsl — `home.desktop` is composed below into the
# Darwin, physical-desktop and graphical-guest homes; the WSL homes take
# `shared` and `wsl` and nothing graphical.
# tool/checks/flake-test is the enforcement.
#
# INV unixlike/composition-in-one-place — this file is that place.
# tool/checks/composition refuses a feature file that names a host flavour
# or forces a class's decision.
#
# `home.agents` — the coding agents — is offered to WSL NixOS hosts and
# selected by `hostSelections.nixos.nixos`; the standalone Ubuntu home and
# the Darwin home are unchanged by it (modules/agents.nix).
#
# INV unixlike/nixos-host-inventory — every NixOS output is generated from
# `identity.nixosHosts`, named after its entry, and told about itself through
# `host` (modules/host/nixos.nix), so the output name, the inventory name and
# `networking.hostName` cannot drift (#191). `nixosCompositions` is the one
# table from a host's kind — for a `vm`, its hypervisor — to required classes
# and offered profiles. A host whose kind has no row does not evaluate.
{
  lib,
  config,
  inputs,
  withSystem,
  ...
}: let
  inherit (lib) attrNames attrValues concatMap mapAttrs optionalAttrs unique;
  inherit (config.identity) wsl darwin nixosHosts;
  hostSelections = config.hostSelections.nixos;
  home = config.modules.homeManager;
  nixos = config.modules.nixos;

  nixosCompositions = {
    wsl = {
      required.system = [
        inputs.nixos-wsl.nixosModules.default
        nixos.wsl
      ];
      required.home = [
        home.shared
        home.wsl
      ];
      optional.agents = {
        system = [];
        home = [home.agents];
      };
    };

    # The aarch64 graphical guest: its UTM machine and serial recovery path,
    # the headless account/SSH layer, and the shared Niri/Noctalia classes.
    # The coding agents stay on NixOS-WSL.
    utm = {
      required.system = [
        nixos.utm
        nixos.installExt4
        nixos.headless
        nixos.graphical
      ];
      required.home = [
        home.shared
        home.desktop
        home.linuxGraphical
      ];
      optional = {};
    };

    # An OrbStack machine: what OrbStack needs from the guest
    # (modules/host/orbstack.nix) — its own account, no sshd and no headless
    # class, because OrbStack's agent is the way in — and the shared home
    # alone.
    orbstack = {
      required = {
        system = [nixos.orbstack];
        home = [home.shared];
      };
      optional = {};
    };

    # The x86_64 graphical guest under VMware Workstation, with the same
    # headless recovery and shared graphical layers as the UTM guest.
    vmware = {
      required.system = [
        nixos.vmware
        nixos.installExt4
        nixos.headless
        nixos.graphical
      ];
      required.home = [
        home.shared
        home.desktop
        home.linuxGraphical
      ];
      optional = {};
    };

    # The physical AMD APU desktop. The headless class remains its account,
    # SSH and recovery path; the shared graphical classes supply Niri and
    # Noctalia. Installation and physical runtime evidence remain separate.
    desktop = {
      required.system = [
        nixos.desktop
        nixos.installLuksBtrfs
        nixos.headless
        nixos.graphical
      ];
      required.home = [
        home.shared
        home.desktop
        home.linuxGraphical
      ];
      optional = {};
    };
  };

  # Every inventory host makes a choice, even when it selects no optional
  # profile. Extra selection entries are rejected rather than silently unused.
  checkedSelections =
    if attrNames hostSelections != attrNames nixosHosts
    then throw "hostSelections.nixos must name exactly the hosts in identity.nixosHosts."
    else hostSelections;

  nixosHost = name: host: let
    key =
      if host.kind == "vm"
      then host.hypervisor
      else host.kind;
    composition =
      nixosCompositions.${key}
      or (throw "identity.nixosHosts.${name}: no composition is written for ${key} in modules/flake/configurations.nix.");
    profiles = let
      chosen = checkedSelections.${name}.profiles;
    in
      if unique chosen != chosen
      then throw "hostSelections.nixos.${name}: profiles must not be repeated."
      else chosen;
    selected = map (profile:
      composition.optional.${profile}
      or (throw "hostSelections.nixos.${name}: profile ${profile} is unavailable for ${key}."))
    profiles;
    systemModules = composition.required.system ++ concatMap (profile: profile.system) selected;
    homeModules = composition.required.home ++ concatMap (profile: profile.home) selected;
  in
    inputs.nixpkgs.lib.nixosSystem {
      inherit (host) system;
      modules =
        systemModules
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
              users = optionalAttrs (homeModules != []) {
                ${host.user}.imports = homeModules;
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
