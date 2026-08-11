_: {
  windows = {
    packages.powerToys = {
      name = "PowerToys";
      id = "Microsoft.PowerToys";
      detection = "WinGet";
    };

    managedFiles = {
      powerToysRoot = {
        source = "files/powertoys/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      advancedPaste = {
        source = "files/powertoys/AdvancedPaste/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\AdvancedPaste\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      awake = {
        source = "files/powertoys/Awake/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\Awake\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      commandPalette = {
        source = "files/powertoys/CmdPal/settings.json";
        target = "{LOCALAPPDATA}\\Packages\\Microsoft.CommandPalette_8wekyb3d8bbwe\\LocalState\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      fancyZones = {
        source = "files/powertoys/FancyZones/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\FancyZones\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      fancyZonesCustomLayouts = {
        source = "files/powertoys/FancyZones/custom-layouts.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\FancyZones\\custom-layouts.json";
        parser = "Json";
        compare = "ExactJson";
        group = "PowerToys";
      };
      fancyZonesDefaultLayouts = {
        source = "files/powertoys/FancyZones/default-layouts.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\FancyZones\\default-layouts.json";
        parser = "Json";
        compare = "ExactJson";
        group = "PowerToys";
      };
      fancyZonesLayoutHotkeys = {
        source = "files/powertoys/FancyZones/layout-hotkeys.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\FancyZones\\layout-hotkeys.json";
        parser = "Json";
        compare = "ExactJson";
        group = "PowerToys";
      };
      fileExplorer = {
        source = "files/powertoys/File Explorer/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\File Explorer\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      fileLocksmith = {
        source = "files/powertoys/File Locksmith/file-locksmith-settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\File Locksmith\\file-locksmith-settings.json";
        parser = "Json";
        compare = "ExactJson";
        group = "PowerToys";
      };
      findMyMouse = {
        source = "files/powertoys/FindMyMouse/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\FindMyMouse\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      keyboardManager = {
        source = "files/powertoys/Keyboard Manager/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\Keyboard Manager\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      keyboardManagerMapping = {
        source = "files/powertoys/Keyboard Manager/default.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\Keyboard Manager\\default.json";
        parser = "Json";
        compare = "ExactJson";
        group = "PowerToys";
      };
      newPlus = {
        source = "files/powertoys/NewPlus/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\NewPlus\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      peek = {
        source = "files/powertoys/Peek/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\Peek\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
      peekPreview = {
        source = "files/powertoys/Peek/preview-settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\Peek\\preview-settings.json";
        parser = "Json";
        compare = "ExactJson";
        group = "PowerToys";
      };
      powerRename = {
        source = "files/powertoys/PowerRename/power-rename-settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\PowerRename\\power-rename-settings.json";
        parser = "Json";
        compare = "ExactJson";
        group = "PowerToys";
      };
      workspaces = {
        source = "files/powertoys/Workspaces/settings.json";
        target = "{LOCALAPPDATA}\\Microsoft\\PowerToys\\Workspaces\\settings.json";
        parser = "Json";
        compare = "JsonSubset";
        group = "PowerToys";
      };
    };
  };
}
