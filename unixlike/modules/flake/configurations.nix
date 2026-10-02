# Public Unix-like constructors and synthetic output examples. This is the
# only place that maps environment selections to deferred module classes.
# Machine realization is supplied by consumer systemModules and homeModules.
# INV unixlike/typed-identity: every public identity input is validated here.
{
  lib,
  config,
  inputs,
  withSystem,
  ...
}: let
  inherit (lib) attrNames attrValues mkOption types unique;
  home = config.modules.homeManager;
  nixos = config.modules.nixos;
  providerConfig = config;
  apiContract = import ../../api/contract.nix;

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

  darwinUserIdentity = account: _: {
    options.providerIdentity.user = mkOption {
      type = types.str;
      readOnly = true;
    };
    config.providerIdentity.user = account;
  };

  nixosUserIdentity = account: _: {
    options.providerIdentity.user = mkOption {
      type = types.str;
      readOnly = true;
    };
    config.providerIdentity.user = account;
  };

  selectedDarwinApps = brew: let
    nameOf = value:
      if builtins.isString value
      then value
      else value.name;
    normalize = value: lib.toLower (builtins.baseNameOf (nameOf value));
  in
    unique (
      map normalize (brew.casks ++ brew.brews)
      ++ map lib.toLower (attrNames brew.masApps)
    );

  # Public environment selection is independent of the host's hardware,
  # account creation and access policy. Synthetic fixtures exercise the
  # public constructors without claiming real host ownership.
  mkNixos = values: let
    retired = builtins.filter (name: builtins.hasAttr name values) ["name" "host" "profiles"];
    spec =
      checkedInput "lib.mkNixos" ["system" "user" "git"] {
        system = mkOption {type = types.enum ["x86_64-linux" "aarch64-linux"];};
        user = mkOption {type = types.str;};
        git = mkOption {type = gitType;};
        environment = mkOption {
          default = {};
          type = types.submodule ({config, ...}: {
            options = {
              wsl = mkOption {
                type = types.bool;
                default = false;
              };
              graphical = mkOption {
                type = types.bool;
                default = !config.wsl;
              };
            };
          });
        };
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
    selected = spec.environment;
    homeModules =
      [home.shared]
      ++ lib.optionals selected.wsl [home.wsl]
      ++ lib.optionals selected.graphical [home.desktop home.linuxGraphical]
      ++ [home.agents (homeIdentity spec.git spec.user)]
      ++ spec.homeModules;
  in
    if retired != []
    then throw "lib.mkNixos: retired input ${lib.concatStringsSep ", " retired}; pass system, user and environment, and put machine settings in systemModules."
    else
      builtins.deepSeq spec (
        if selected.wsl && selected.graphical
        then throw "lib.mkNixos: environment.graphical cannot be true when environment.wsl is true."
        else
          inputs.nixpkgs.lib.nixosSystem {
            inherit (spec) system;
            modules =
              spec.systemModules
              ++ [
                inputs.home-manager.nixosModules.home-manager
                nixos.environment
                (nixosUserIdentity spec.user)
              ]
              ++ lib.optionals selected.graphical [nixos.graphical]
              ++ [
                ({
                  config,
                  lib,
                  options,
                  ...
                }: let
                  account = config.users.users.${spec.user} or null;
                  accountHome =
                    if account == null
                    then "/home/${spec.user}"
                    else account.home;
                  wslEnabled =
                    if options ? wsl.enable
                    then config.wsl.enable
                    else false;
                in {
                  nixpkgs.config = providerConfig.nixpkgsConfig;
                  nixpkgs.overlays = attrValues providerConfig.nixpkgsOverlays;
                  home-manager = {
                    useGlobalPkgs = true;
                    useUserPackages = true;
                    users.${spec.user}.imports =
                      homeModules
                      ++ [
                        {
                          home.username = lib.mkDefault spec.user;
                          home.homeDirectory = lib.mkDefault accountHome;
                        }
                      ];
                  };
                  assertions = [
                    {
                      assertion = account != null;
                      message = "lib.mkNixos: systemModules must create the selected user ${spec.user}.";
                    }
                    {
                      assertion = account != null && config.home-manager.users.${spec.user}.home.homeDirectory == account.home;
                      message = "lib.mkNixos: the managed home directory must match the selected system account.";
                    }
                    {
                      assertion = selected.wsl == wslEnabled;
                      message = "lib.mkNixos: environment.wsl must match the host-supplied NixOS-WSL integration.";
                    }
                    {
                      assertion = !selected.wsl || !wslEnabled || (!config.wsl.useWindowsDriver && !config.wsl.startMenuLaunchers);
                      message = "INV unixlike/desktop-not-wsl: WSL graphics-driver and Start Menu launcher integration must stay disabled.";
                    }
                  ];
                })
              ];
          }
      );

  mkDarwin = values: let
    retired = builtins.filter (name: builtins.hasAttr name values) ["host"];
    spec =
      checkedInput "lib.mkDarwin" ["system" "user" "git"] {
        system = mkOption {type = types.enum ["aarch64-darwin"];};
        user = mkOption {type = types.str;};
        git = mkOption {type = gitType;};
        environment = mkOption {
          default = {};
          type = types.submodule {
            options = {
              wsl = mkOption {
                type = types.bool;
                default = false;
              };
              graphical = mkOption {
                type = types.bool;
                default = true;
              };
            };
          };
        };
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
    homeModules =
      [home.shared home.darwin]
      ++ lib.optionals spec.environment.graphical [home.desktop]
      ++ [home.agents (homeIdentity spec.git spec.user)]
      ++ spec.homeModules;
  in
    if retired != []
    then throw "lib.mkDarwin: retired host input; pass system and user, and put hostname and account settings in systemModules."
    else
      builtins.deepSeq spec (
        if spec.environment.wsl
        then throw "lib.mkDarwin: environment.wsl is unavailable on Darwin."
        else
          inputs.nix-darwin.lib.darwinSystem {
            inherit (spec) system;
            modules =
              spec.systemModules
              ++ [
                inputs.home-manager.darwinModules.home-manager
                config.modules.darwin.environment
                (darwinUserIdentity spec.user)
                ({
                  config,
                  lib,
                  ...
                }: let
                  account = config.users.users.${spec.user} or null;
                in {
                  nixpkgs.config = providerConfig.nixpkgsConfig;
                  nixpkgs.overlays = attrValues providerConfig.nixpkgsOverlays;
                  home-manager = {
                    useGlobalPkgs = true;
                    useUserPackages = true;
                    users.${spec.user}.imports =
                      homeModules
                      ++ [
                        {providerDarwin.selectedApps = selectedDarwinApps config.homebrew;}
                        {
                          home.username = lib.mkDefault spec.user;
                          home.homeDirectory = lib.mkDefault (
                            if account == null
                            then "/Users/${spec.user}"
                            else account.home
                          );
                        }
                      ];
                  };
                  assertions = [
                    {
                      assertion = account != null;
                      message = "lib.mkDarwin: systemModules must supply the selected account ${spec.user}.";
                    }
                    {
                      assertion = account != null && config.home-manager.users.${spec.user}.home.homeDirectory == account.home;
                      message = "lib.mkDarwin: the managed home directory must match the selected system account.";
                    }
                  ];
                })
              ];
          }
      );

  mkHome = values: let
    required = attrNames (lib.filterAttrs (_: input: input.required) apiContract.entryPoints.mkHome.inputs);
    spec =
      checkedInput "lib.mkHome" required {
        system = mkOption {type = types.enum apiContract.constraints.mkHome.systems;};
        user = mkOption {type = types.str;};
        homeDirectory = mkOption {type = types.strMatching "^/.*";};
        git = mkOption {type = gitType;};
        environment = mkOption {
          default = {};
          type = types.submodule ({config, ...}: {
            options = {
              wsl = mkOption {
                type = types.bool;
                default = apiContract.entryPoints.mkHome.inputs.environment.defaults.wsl;
              };
              graphical = mkOption {
                type = types.bool;
                default =
                  if config.wsl
                  then apiContract.entryPoints.mkHome.inputs.environment.defaults.graphicalWhenWsl
                  else apiContract.entryPoints.mkHome.inputs.environment.defaults.graphicalOtherwise;
              };
            };
          });
        };
        homeModules = mkOption {
          type = types.listOf types.deferredModule;
          default = [];
        };
      }
      values;
    selected = spec.environment;
    homeModules =
      [home.shared]
      ++ lib.optionals selected.wsl [home.wsl]
      ++ lib.optionals selected.graphical [home.desktop home.linuxGraphical]
      ++ [
        home.agents
        home.standalone
        (homeIdentity spec.git spec.user)
        {
          home.homeDirectory = lib.mkDefault spec.homeDirectory;
        }
      ]
      ++ spec.homeModules;
  in
    builtins.deepSeq spec (
      if selected.wsl && selected.graphical
      then throw "lib.mkHome: environment.graphical cannot be true when environment.wsl is true."
      else
        withSystem spec.system ({pkgs, ...}:
          inputs.home-manager.lib.homeManagerConfiguration {
            inherit pkgs;
            modules = homeModules;
          })
    );

  fixtureUser = "example";
  fixtureGit = {
    name = "Example";
    email = "example@example.invalid";
  };
  fixtureSystem = name: {
    networking.hostName = name;
    boot.loader.grub.enable = false;
    users.users.example.isNormalUser = true;
    fileSystems."/" = {
      device = "/dev/disk/by-label/fixture";
      fsType = "ext4";
    };
  };
in {
  flake = {
    lib = {inherit mkNixos mkDarwin mkHome;};
    nixosConfigurations = {
      fixture-cli = mkNixos {
        system = "x86_64-linux";
        user = "example";
        git = fixtureGit;
        environment.graphical = false;
        systemModules = [(fixtureSystem "fixture-cli")];
      };
      fixture-graphical = mkNixos {
        system = "x86_64-linux";
        user = "example";
        git = fixtureGit;
        systemModules = [(fixtureSystem "fixture-graphical")];
      };
      fixture-arm-cli = mkNixos {
        system = "aarch64-linux";
        user = "example";
        git = fixtureGit;
        environment.graphical = false;
        systemModules = [(fixtureSystem "fixture-arm-cli")];
      };
      fixture-wsl = mkNixos {
        system = "x86_64-linux";
        user = "example";
        git = fixtureGit;
        environment.wsl = true;
        systemModules = [
          inputs.nixos-wsl.nixosModules.default
          (fixtureSystem "fixture-wsl")
          {
            wsl = {
              enable = true;
              defaultUser = "example";
              useWindowsDriver = false;
              startMenuLaunchers = false;
            };
          }
        ];
      };
    };
    darwinConfigurations.fixture-mac = mkDarwin {
      system = "aarch64-darwin";
      user = "example";
      git = fixtureGit;
      systemModules = [
        {
          networking.hostName = "fixture-mac";
          system.primaryUser = "example";
          users.users.example.home = "/Users/${fixtureUser}";
        }
      ];
    };
    homeConfigurations = {
      example = mkHome {
        system = "x86_64-linux";
        user = "example";
        homeDirectory = "/home/${fixtureUser}";
        environment.graphical = false;
        git = fixtureGit;
      };
      example-wsl = mkHome {
        system = "x86_64-linux";
        user = "example";
        homeDirectory = "/home/${fixtureUser}";
        environment.wsl = true;
        git = fixtureGit;
      };
    };
  };
}
