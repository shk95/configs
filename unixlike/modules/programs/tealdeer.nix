_: {
  modules.homeManager.shared.programs.tealdeer = {
    enable = true;
    enableAutoUpdates = false;
    settings = {
      display = {
        compact = false;
        use_pager = true;
      };
      updates.auto_update = false;
    };
  };
}
