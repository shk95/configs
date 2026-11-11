# PROV unixlike/paneru-unwrapped
{
  config,
  inputs,
  lib,
  ...
}: {
  perSystem = {
    pkgs,
    system,
    ...
  }:
    lib.optionalAttrs (lib.hasSuffix "-darwin" system) (let
      provider = {
        lib = config.flake.lib;
        inherit inputs;
        outPath = inputs.self.outPath;
      };
      witness = (import ../../../tool/checks/composition-witnesses.nix {inherit provider;})
        .witnesses."mkDarwin/${system}/graphical";
      home = witness.configuration.config.home-manager.users.example;
      package = home.services.paneru.finalPackage;
      program = home.launchd.agents.paneru.config.Program;
    in {
      checks.paneru-unwrapped = pkgs.runCommand "paneru-unwrapped" {} ''
        test '${program}' = '${lib.getExe package}'
        case "$(od -An -tx1 -N4 '${program}' | tr -d ' \n')" in
          cffaedfe|cefaedfe|feedfacf|feedface|cafebabe|bebafeca|cafebabf|bfbafeca) ;;
          *) echo 'Paneru launchd executable is not a native Mach-O' >&2; exit 1 ;;
        esac
        '${program}' --version | grep -F 'LuaJIT'
        touch "$out"
      '';
    });
}
