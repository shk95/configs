# A sentence about mkForce, and about homeConfigurations, is prose rather than
# a use of either. tool/checks/composition-test requires this to be accepted.
_: {
  modules.homeManager.shared = {lib, ...}: {
    xdg.configFile."probe/config".text = lib.mkDefault "a default is not a force"; # not mkForce
  };
}
