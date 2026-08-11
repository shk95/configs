_: {
  windows = {
    packages.windowsTerminal = {
      name = "Windows Terminal";
      id = "Microsoft.WindowsTerminal";
      detection = "Appx";
      appxName = "Microsoft.WindowsTerminal";
    };
    terminal = {
      defaultProfileGuid = "{574e775e-4f2a-5b96-ac1e-a2962a402336}";
      zellijProfileGuid = "{035bb70e-121b-521e-b4a8-d8bcbbb47434}";
      delegationTerminal = "{E12CFF52-A866-4C77-9A90-F570A7AA2C6B}";
      delegationConsole = "{2EACA947-7F5F-4CFA-BA87-8F7FBEEFBE69}";
    };
    managedFiles.windowsTerminal = {
      source = "files/terminal/settings.json";
      target = "{LOCALAPPDATA}\\Packages\\Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\settings.json";
      parser = "Json";
      compare = "ExactJson";
    };
  };
}
