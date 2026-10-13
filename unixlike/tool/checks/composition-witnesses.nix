# INV unixlike/eval-covers-every-host: force the advertised constructor matrix,
# independently of which examples the provider exports.
{provider}: let
  lib = provider.inputs.nixpkgs.lib;
  contract = builtins.fromJSON (builtins.readFile (provider.outPath + "/api/contract.json"));
  scenarios = lib.concatMap (constructor:
    lib.concatMap (system:
      map (selection: {
        inherit constructor system;
        inherit (selection) environment;
        label = "${constructor}/${system}/${selection.name}";
      }) (
        [
          {
            name = "cli";
            environment = {
              wsl = false;
              graphical = false;
            };
          }
          {
            name = "graphical";
            environment = {
              wsl = false;
              graphical = true;
            };
          }
        ]
        ++ lib.optional (contract.constraints.${constructor}.wsl or true) {
          name = "wsl";
          environment = {
            wsl = true;
            graphical = false;
          };
        }
      ))
    contract.constraints.${constructor}.systems)
  (builtins.attrNames contract.entryPoints);
  arguments = scenario:
    {
      inherit (scenario) system environment;
      user = "example";
      git = {
        name = "Example";
        email = "example@example.invalid";
      };
    }
    // lib.optionalAttrs (scenario.constructor == "mkHome") {
      homeDirectory = "/home/" + "example";
    }
    // lib.optionalAttrs (scenario.constructor == "mkDarwin") {
      systemModules = [
        {
          system.primaryUser = "example";
          users.users.example.home = "/Users/" + "example";
        }
      ];
    }
    // lib.optionalAttrs (scenario.constructor == "mkNixos") {
      systemModules =
        [
          {
            boot.loader.grub.enable = false;
            users.users.example.isNormalUser = true;
            fileSystems."/" = {
              device = "/dev/disk/by-label/fixture";
              fsType = "ext4";
            };
          }
        ]
        ++ lib.optionals scenario.environment.wsl [
          provider.inputs.nixos-wsl.nixosModules.default
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
  witnesses = builtins.listToAttrs (map (scenario: {
      name = scenario.label;
      value = let
        args = arguments scenario;
      in
        scenario
        // {
          inherit args;
          configuration = provider.lib.${scenario.constructor} args;
        };
    })
    scenarios);
in {
  inherit witnesses;
  toplevels = lib.mapAttrs (_: witness:
    if witness.constructor == "mkHome"
    then witness.configuration.activationPackage.drvPath
    else witness.configuration.config.system.build.toplevel.drvPath)
  witnesses;
}
