_: {
  windows.managedFiles.wslConfig = {
    source = "files/wsl/.wslconfig";
    target = "{USERPROFILE}\\.wslconfig";
    parser = "Ini";
    compare = "Text";
  };
}
