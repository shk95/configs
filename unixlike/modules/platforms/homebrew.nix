{lib, ...}: {
  # App selection and Homebrew lifecycle are host-owned. This provider
  # preference is overridable by the consumer's systemModules.
  modules.darwin.environment.homebrew.enableZshIntegration = lib.mkDefault true;
}
