_: {
  windows = {
    packages.powershell = {
      name = "PowerShell 7";
      id = "Microsoft.PowerShell";
      detection = "Command";
      command = "pwsh.exe";
      bootstrap = true;
    };
    managedFiles.powershellProfile = {
      source = "files/powershell/profile.ps1";
      target = "{LOCALAPPDATA}\\win-env\\powershell\\profile.ps1";
      parser = "PowerShell";
      compare = "Text";
    };
  };
}
