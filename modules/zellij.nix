_: {
  windows = {
    packages.zellij = {
      name = "Zellij";
      id = "Zellij.Zellij";
      detection = "Command";
      command = "zellij.exe";
    };
    managedFiles.zellij = {
      source = "files/zellij/config.kdl";
      target = "{APPDATA}\\Zellij\\config\\config.kdl";
      parser = "Kdl";
      compare = "Text";
    };
  };
}
