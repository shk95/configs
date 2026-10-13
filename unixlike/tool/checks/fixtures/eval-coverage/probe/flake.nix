{
  # tool/checks/eval-coverage-test: one flavour exporting one configuration
  # that instantiates. It targets a foreign platform, so the check evaluates
  # but never builds its host closure.
  description = "eval-coverage fixture: one configuration";
  outputs = _: {
    homeConfigurations.probe = {
      activationPackage = derivation {
        name = "probe";
        system = "riscv64-linux";
        builder = "/bin/false";
      };
      pkgs.stdenv.hostPlatform.system = "riscv64-linux";
    };
  };
}
