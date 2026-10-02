# Deliberately names a host flavour from a feature file.
# tool/checks/composition-test requires this to be rejected.
{inputs, ...}: {
  flake.homeConfigurations.probe = inputs.home-manager.lib.homeManagerConfiguration {};
}
