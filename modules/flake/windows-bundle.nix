{
  config,
  lib,
  ...
}: let
  omitNull = lib.filterAttrs (_: value: value != null);
  package = value:
    omitNull {
      Name = value.name;
      Id = value.id;
      Detection = value.detection;
      Command = value.command;
      AppxName = value.appxName;
      Bootstrap = value.bootstrap;
    };
  managedFile = value:
    omitNull {
      Id = value.id;
      Source = value.source;
      Target = value.target;
      Parser = value.parser;
      Compare = value.compare;
      Group = value.group;
    };
  fontFile = value: {
    FileName = value.fileName;
    FullName = value.fullName;
    RegistryName = value.registryName;
    Sha256 = value.sha256;
  };
  manifest = {
    SchemaVersion = config.windows.schemaVersion;
    ProjectVersion = config.windows.projectVersion;
    Packages = lib.mapAttrsToList (_: package) config.windows.packages;
    Font = {
      Name = config.windows.font.name;
      Version = config.windows.font.version;
      Url = config.windows.font.url;
      Sha256 = config.windows.font.sha256;
      Files = map fontFile config.windows.font.files;
    };
    Terminal = {
      DefaultProfileGuid = config.windows.terminal.defaultProfileGuid;
      ZellijProfileGuid = config.windows.terminal.zellijProfileGuid;
      DelegationTerminal = config.windows.terminal.delegationTerminal;
      DelegationConsole = config.windows.terminal.delegationConsole;
    };
    ManagedFiles = lib.mapAttrsToList (_: managedFile) config.windows.managedFiles;
  };
in {
  perSystem = {
    config,
    pkgs,
    ...
  }: {
    packages.windows-bundle =
      pkgs.runCommand "configs-windows-bundle" {
        nativeBuildInputs = [
          pkgs.jq
          pkgs.lua5_4
        ];
      } ''
        find ${../../assets/windows} -name '*.json' -type f -exec jq empty '{}' \;
        find ${../../assets/wezterm} -name '*.json' -type f -exec jq empty '{}' \;
        find ${../../assets/wezterm} -name '*.lua' -type f -exec luac -p '{}' \;
        mkdir -p "$out/files"
        cp -R ${../../assets/windows}/. "$out/files/"
        cp -R ${../../assets/wezterm} "$out/files/wezterm"
        printf '%s' '${builtins.toJSON manifest}' | jq --sort-keys . > "$out/manifest.json"
      '';

    checks.windows-bundle = config.packages.windows-bundle;
  };
}
