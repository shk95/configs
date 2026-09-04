{
  # tool/checks/eval-coverage-test: one flavour exporting one configuration
  # that instantiates. It targets a platform no host in the inventory has, so
  # the check evaluates it and never builds it on any host this repository
  # runs on; a platform an inventory host shares would be built there, and
  # the builder below cannot succeed. tool/checks/test must report it and
  # exit 0.
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
