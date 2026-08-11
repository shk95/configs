{lib, ...}: let
  inherit (lib) mkOption types;
  packageType = types.submodule ({name, ...}: {
    options = {
      name = mkOption {
        type = types.str;
        default = name;
      };
      id = mkOption {type = types.str;};
      detection = mkOption {
        type = types.enum ["Command" "Appx" "WinGet"];
      };
      command = mkOption {
        type = types.nullOr types.str;
        default = null;
      };
      appxName = mkOption {
        type = types.nullOr types.str;
        default = null;
      };
      bootstrap = mkOption {
        type = types.bool;
        default = false;
      };
    };
  });
  managedFileType = types.submodule ({name, ...}: {
    options = {
      id = mkOption {
        type = types.str;
        default = name;
      };
      source = mkOption {type = types.str;};
      target = mkOption {type = types.str;};
      parser = mkOption {
        type = types.enum ["Ini" "Json" "Kdl" "Lua" "PowerShell" "Text"];
      };
      compare = mkOption {
        type = types.enum ["Text" "ExactJson" "JsonSubset"];
      };
      group = mkOption {
        type = types.nullOr types.str;
        default = null;
      };
    };
  });
  fontFileType = types.submodule {
    options = {
      fileName = mkOption {type = types.str;};
      fullName = mkOption {type = types.str;};
      registryName = mkOption {type = types.str;};
      sha256 = mkOption {type = types.strMatching "^[0-9a-f]{64}$";};
    };
  };
in {
  options.windows = {
    schemaVersion = mkOption {
      type = types.int;
      default = 1;
      readOnly = true;
    };
    projectVersion = mkOption {
      type = types.str;
      default = "0.2.0";
      description = "Compatibility version for the Windows reconciliation engine.";
    };
    packages = mkOption {
      type = types.attrsOf packageType;
      default = {};
    };
    managedFiles = mkOption {
      type = types.attrsOf managedFileType;
      default = {};
    };
    font = {
      name = mkOption {type = types.str;};
      version = mkOption {type = types.str;};
      url = mkOption {type = types.str;};
      sha256 = mkOption {type = types.strMatching "^[0-9a-f]{64}$";};
      files = mkOption {
        type = types.listOf fontFileType;
        default = [];
      };
    };
    terminal = {
      defaultProfileGuid = mkOption {type = types.str;};
      zellijProfileGuid = mkOption {type = types.str;};
      delegationTerminal = mkOption {type = types.str;};
      delegationConsole = mkOption {type = types.str;};
    };
  };
}
