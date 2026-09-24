_: {
  modules.homeManager.shared = _: {
    # The alias is declarative; keys and known_hosts remain host-owned.
    programs.ssh = {
      enable = true;
      enableDefaultConfig = false;
      includes = [
        "~/.ssh/config.d/*.conf"
      ];
    };
  };
}
