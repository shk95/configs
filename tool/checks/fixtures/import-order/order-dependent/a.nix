# Deliberately order-sensitive: two files contribute to one `lines` option at
# the same order, so the walk order decides the generated file.
# tool/checks/import-order-test requires this pair to be rejected.
_: {
  modules.homeManager.shared = {
    programs.zsh.initContent = "# import-order probe a";
  };
}
