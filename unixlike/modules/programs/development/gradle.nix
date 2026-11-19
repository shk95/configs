# Build tool. SDKMAN owns the JVM toolchain.
_: {
  programCatalog.gradle = {
    profiles = ["shared"];
    providers.nix = {
      identifier = "gradle";
      packageOnly = true;
    };
  };
}
