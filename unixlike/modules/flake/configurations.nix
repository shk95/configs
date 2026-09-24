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
  inherit (lib) attrNames attrValues concatMap mapAttrs mkOption types unique;
  inherit (config.identity) wsl darwin nixosHosts;
  hostSelections = config.hostSelections.nixos;
  home = config.modules.homeManager;
  nixos = config.modules.nixos;
  contract = import ./_host-contract.nix {inherit lib;};

  gitType = types.submodule {
    options = {
      name = mkOption {type = types.str;};
      email = mkOption {type = types.str;};
    };
  };

  requireFields = label: fields: values:
    if !builtins.isAttrs values
    then throw "${label}: expected an attribute set."
    else
      lib.foldl' (acc: field:
        if builtins.hasAttr field acc
        then acc
        else throw "${label}: missing required field ${field}.")
      values
      fields;

  checkedInput = label: required: options: values: let
    checked = requireFields label required values;
    git = requireFields "${label}.git" ["name" "email"] checked.git;
  in
    (lib.evalModules {
      modules = [
        {
          inherit options;
          config = checked // {inherit git;};
        }
      ];
    }).config;

  homeIdentity = git: account: _: {
    options.providerIdentity = {
      user = mkOption {
        type = types.str;
        readOnly = true;
      };
      gitName = mkOption {
        type = types.str;
        readOnly = true;
      };
      gitEmail = mkOption {
        type = types.str;
        readOnly = true;
      };
    };
    config.providerIdentity = {
      user = account;
      gitName = git.name;
      gitEmail = git.email;
    };
  };

  darwinIdentity = host: _: {
    options.providerIdentity = {
      user = mkOption {
        type = types.str;
        readOnly = true;
      };
      hostName = mkOption {
        type = types.str;
        readOnly = true;
      };
    };
    config.providerIdentity = {
      inherit (host) user hostName;
    };
  };

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

  mkNixos = values: let
    spec =
      checkedInput "lib.mkNixos" ["name" "host" "profiles" "git"] {
        name = mkOption {type = types.str;};
        host = mkOption {type = contract.hostType;};
        profiles = mkOption {type = types.listOf (types.enum ["agents"]);};
        git = mkOption {type = gitType;};
        systemModules = mkOption {
          type = types.listOf types.deferredModule;
          default = [];
        };
        homeModules = mkOption {
          type = types.listOf types.deferredModule;
          default = [];
        };
      }
      values;
    inherit (spec) name host;
    checkedHost = contract.checkHost {
      inherit name host;
      wslUser = host.user;
    };
    key =
      if host.kind == "vm"
      then host.hypervisor
      else host.kind;
    composition =
      nixosCompositions.${key}
      or (throw "identity.nixosHosts.${name}: no composition is written for ${key} in modules/flake/configurations.nix.");
    profiles =
      if unique spec.profiles != spec.profiles
      then throw "hostSelections.nixos.${name}: profiles must not be repeated."
      else spec.profiles;
    selected = map (profile:
      composition.optional.${profile}
      or (throw "hostSelections.nixos.${name}: profile ${profile} is unavailable for ${key}."))
    profiles;
    systemModules = composition.required.system ++ concatMap (profile: profile.system) selected ++ spec.systemModules;
    homeModules = composition.required.home ++ concatMap (profile: profile.home) selected ++ spec.homeModules;
  in
    builtins.deepSeq spec (builtins.seq checkedHost (inputs.nixpkgs.lib.nixosSystem {
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
              users.${host.user}.imports = homeModules ++ [(homeIdentity spec.git host.user)];
            };
          }
        ];
    }));

  mkDarwin = values: let
    spec =
      checkedInput "lib.mkDarwin" ["host" "git"] {
        host = mkOption {
          type = types.submodule {
            options = {
              user = mkOption {type = types.str;};
              hostName = mkOption {type = types.str;};
              system = mkOption {type = types.enum ["aarch64-darwin" "x86_64-darwin"];};
            };
          };
        };
        git = mkOption {type = gitType;};
        systemModules = mkOption {
          type = types.listOf types.deferredModule;
          default = [];
        };
        homeModules = mkOption {
          type = types.listOf types.deferredModule;
          default = [];
        };
      }
      values;
  in
    builtins.deepSeq spec (inputs.nix-darwin.lib.darwinSystem {
      inherit (spec.host) system;
      modules =
        [
          inputs.home-manager.darwinModules.home-manager
          config.modules.darwin.system
          (darwinIdentity spec.host)
          {
            nixpkgs.config = config.nixpkgsConfig;
            nixpkgs.overlays = attrValues config.nixpkgsOverlays;
            home-manager = {
              useGlobalPkgs = true;
              useUserPackages = true;
              users.${spec.host.user}.imports =
                [
                  home.shared
                  home.desktop
                  home.darwin
                  (homeIdentity spec.git spec.host.user)
                ]
                ++ spec.homeModules;
            };
          }
        ]
        ++ spec.systemModules;
    });

  mkHome = values: let
    spec =
      checkedInput "lib.mkHome" ["system" "user" "git"] {
        system = mkOption {type = types.enum ["x86_64-linux"];};
        user = mkOption {type = types.str;};
        git = mkOption {type = gitType;};
        homeModules = mkOption {
          type = types.listOf types.deferredModule;
          default = [];
        };
      }
      values;
  in
    builtins.deepSeq spec (withSystem spec.system ({pkgs, ...}:
      inputs.home-manager.lib.homeManagerConfiguration {
        inherit pkgs;
        modules =
          [
            home.shared
            home.wsl
            home.wslStandalone
            (homeIdentity spec.git spec.user)
          ]
          ++ spec.homeModules;
      }));

  git = {
    name = config.identity.gitName;
    email = config.identity.gitEmail;
  };
in {
  flake = {
    lib = {inherit mkNixos mkDarwin mkHome;};
    homeConfigurations.${wsl.user} = mkHome {
      system = "x86_64-linux";
      inherit (wsl) user;
      inherit git;
    };
    nixosConfigurations = mapAttrs (name: host:
      mkNixos {
        inherit name host git;
        profiles = checkedSelections.${name}.profiles;
      })
    nixosHosts;
    darwinConfigurations.${darwin.hostName} = mkDarwin {
      host = darwin;
      inherit git;
    };
  };
}
