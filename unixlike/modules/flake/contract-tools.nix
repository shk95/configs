# Run a trusted, pinned reader against separate candidate source bytes. The
# reader does not evaluate the candidate flake; Nix is used only to verify a
# supplied source tree against its consumer lock's NAR hash.
_: {
  perSystem = {pkgs, ...}: let
    inspect = pkgs.writeShellApplication {
      name = "contract-inspect";
      runtimeInputs = [pkgs.python3 pkgs.nix];
      text = ''
        exec ${pkgs.python3}/bin/python3 ${../../tool/contract-inspect} "$@"
      '';
    };
    readiness = pkgs.writeShellApplication {
      name = "standalone-readiness";
      runtimeInputs = [pkgs.python3];
      text = ''
        export CONFIGS_UNIXLIKE_CONTRACT=${../../api/contract.json}
        exec ${pkgs.python3}/bin/python3 ${../../tool/standalone-readiness} "$@"
      '';
    };
  in {
    packages = {
      contract-inspect = inspect;
      standalone-readiness = readiness;
    };
    apps = {
      contract-inspect = {
        type = "app";
        program = "${inspect}/bin/contract-inspect";
        meta.description = "Inspect a separate Unix-like provider contract without candidate evaluation";
      };
      standalone-readiness = {
        type = "app";
        program = "${readiness}/bin/standalone-readiness";
        meta.description = "Read selected standalone Home Manager system prerequisites";
      };
    };
  };
}
