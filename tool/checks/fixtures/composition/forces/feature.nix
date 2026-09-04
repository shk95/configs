# Deliberately forces a value another class declares.
# tool/checks/composition-test requires this to be rejected.
_: {
  modules.homeManager.desktop = {lib, ...}: {
    xdg.configFile."probe/config".text = lib.mkForce "desktop wins";
  };
}
