{
  # tool/checks/eval-coverage-test: two NixOS configurations for a platform no
  # host in the inventory has, one that instantiates and one that does not.
  # The broken toplevel is a derivation whose builder throws, the shape of a
  # missing package or a failed assertion: `nix flake check` sees a derivation
  # and passes, and only forcing `.drvPath` finds it. tool/checks/test must
  # report the second as `eval ✗` beside the first and fail: a host that is
  # only ever evaluated, as an aarch64 one is on an x86_64 machine, has no
  # other evidence to lose.
  description = "eval-coverage fixture: a host that fails to evaluate";
  #
  # `pkgs.stdenv.system` is there for a `nix flake check` that reads it to
  # learn a NixOS configuration's platform, as the merge gate's Nix does.
  outputs = _: let
    pkgs.stdenv = {
      system = "riscv64-linux";
      hostPlatform.system = "riscv64-linux";
    };
  in {
    nixosConfigurations = {
      sound = {
        inherit pkgs;
        config.system.build.toplevel = derivation {
          name = "sound";
          system = "riscv64-linux";
          builder = "/bin/false";
        };
      };
      broken = {
        inherit pkgs;
        config.system.build.toplevel = derivation {
          name = "broken";
          system = "riscv64-linux";
          builder = throw "the broken fixture host does not instantiate";
        };
      };
    };
  };
}
