# INV unixlike/tool-supply-ownership: refuse declared duplicate Nix/mise owners.
# Definitions live with their owning concerns. This module resolves selection;
# native modules retain their own package and configuration declarations.
{
  lib,
  config,
  inputs,
  options,
  ...
}: let
  profileNames = ["shared" "desktop" "linuxGraphical" "darwin" "agents" "wsl" "system-common"];
  groupAt = id: owner: let
    location = builtins.match "modules/programs/([a-z][a-z0-9-]*)/.+" owner;
  in
    if location == null
    then throw "programCatalog: ${id} must be defined below modules/programs/<group>/"
    else builtins.head location;
  definitionsById = builtins.groupBy (entry: entry.id) (lib.concatMap (
      definition:
        map (id: {
          inherit id;
          owner = lib.removePrefix (toString inputs.self + "/") definition.file;
        }) (builtins.attrNames definition.value)
    )
    options.programCatalog.definitionsWithLocations);
  supplierSupportsSystem = provider: system: let
    host = lib.systems.elaborate system;
  in
    (provider != "homebrew" || host.isDarwin)
    && (provider != "mise" || host.isLinux);
  catalog = lib.mapAttrs (id: definition: let
    locations = map (entry: entry.owner) definitionsById.${id};
    owner = builtins.head locations;
    profiles = definition.profiles or [];
    platforms = definition.platforms or ["x86_64-linux" "aarch64-linux" "aarch64-darwin"];
  in
    if builtins.length locations != 1
    then throw "programCatalog: duplicate definition for ${id} in ${lib.concatStringsSep ", " locations}"
    else if !(definition ? profiles) || !(lib.all (name: builtins.elem name profileNames) profiles)
    then throw "programCatalog: ${id} must declare valid default profiles"
    else if (definition.providers or {}) == {}
    then throw "programCatalog: ${id} must declare at least one supplier"
    else
      {
        kind = "program";
        nativeEnable = null;
        requiredClasses = [];
        deployment = "home";
        defaults = {};
      }
      // definition
      // {
        inherit owner platforms;
        providers = lib.mapAttrs (provider: supply:
          supply
          // {
            platforms = builtins.filter (system:
              builtins.elem system (supply.platforms or platforms)
              && supplierSupportsSystem provider system)
            platforms;
          })
        definition.providers;
        group = groupAt id owner;
        area =
          if profiles == []
          then null
          else builtins.head profiles;
      })
  config.programCatalog;
  groupNames = lib.unique (map (entry: entry.group) (lib.attrValues catalog));
in {
  options = {
    programCatalog = lib.mkOption {
      type = lib.types.lazyAttrsOf lib.types.attrs;
      default = {};
    };
    resolvedProgramCatalog = lib.mkOption {
      type = lib.types.attrs;
      readOnly = true;
      internal = true;
    };
  };
  config = {
    resolvedProgramCatalog = catalog;
    modules = {
      homeManager = {
        shared = {
          config,
          lib,
          pkgs,
          options,
          osConfig ? null,
          ...
        }: let
          cfg = config.providerTools;
          system = pkgs.stdenv.hostPlatform.system;
          platform =
            if pkgs.stdenv.hostPlatform.isDarwin
            then "darwin"
            else "linux";
          supported = entry: builtins.elem system entry.platforms;
          available = entry:
            entry.requiredClasses == [] || lib.any (name: builtins.elem name cfg.areas) entry.requiredClasses;
          nativeConfig = entry:
            if entry.deployment == "system"
            then osConfig
            else config;
          supplierSupported = entry: provider: builtins.elem system entry.providers.${provider}.platforms;
          defaultProvider = id: entry:
            entry.defaults.${
              platform
            } or (
              if builtins.length (builtins.attrNames entry.providers) == 1
              then builtins.head (builtins.attrNames entry.providers)
              else throw "programCatalog: ${id} has multiple suppliers; declare a default for ${platform}"
            );
          packageFor = entry: lib.attrByPath (lib.splitString "." entry.providers.nix.identifier) null pkgs;
          excluded = entry:
            entry.providers.nix.packageOnly or false
            && packageFor entry != null
            && builtins.elem (lib.getName (packageFor entry)) cfg.excludedPackages;
          requested = id: entry: let
            choice = cfg.programs.${id};
          in
            choice.enable
            && supported entry
            && available entry
            && supplierSupported entry choice.provider
            && !(excluded entry);
          # Homebrew declarations depend only on the request. Applied supply is
          # read back after the system module merges the host's Homebrew options.
          brewSupplies = lib.mapAttrsToList (_: entry: entry.providers.homebrew) (
            lib.filterAttrs (id: entry: cfg.programs.${id}.provider == "homebrew" && requested id entry) catalog
          );
          rows =
            lib.mapAttrsToList (id: entry: let
              choice = cfg.programs.${id};
              inherit (choice) provider;
              supply = entry.providers.${provider} or {};
              package =
                if provider == "nix" && (entry.deployment != "system" || available entry)
                then
                  if entry.nativeEnable == null
                  then packageFor entry
                  else let
                    optionsPath = lib.init entry.nativeEnable;
                    native = nativeConfig entry;
                    package = lib.attrByPath (optionsPath ++ ["package"]) (packageFor entry) native;
                  in
                    lib.attrByPath (optionsPath ++ ["finalPackage"]) package native
                else null;
            in {
              inherit id provider;
              inherit (entry) area kind owner group profiles;
              deployment =
                if provider == "homebrew"
                then "system"
                else entry.deployment;
              supported = supported entry && supplierSupported entry provider;
              available = available entry;
              selected =
                requested id entry
                && (
                  if provider == "nix"
                  then package != null && (entry.nativeEnable == null || lib.attrByPath entry.nativeEnable false (nativeConfig entry))
                  else if provider == "homebrew"
                  then
                    builtins.elem supply.identifier
                    config.providerDarwin.homebrew.${
                      if supply.kind == "cask"
                      then "casks"
                      else "brews"
                    }
                  else true
                );
              identifier = supply.identifier or null;
              requestedVersion =
                if provider == "mise" && choice.version == null
                then "latest"
                else choice.version;
              packageName =
                if package == null
                then null
                else lib.getName package;
              lockedVersion =
                if package == null
                then null
                else package.version or null;
              installedVersion = null;
              source = "catalog";
            })
            catalog;
          selectedRows = provider: builtins.filter (row: row.provider == provider && row.selected) rows;
          nixRows = selectedRows "nix";
          # Inspect the supplier before selection so mise can depend on this list.
          miseRows = selectedRows "mise";
          standalonePackages =
            lib.filterAttrs (
              _: entry:
                entry.profiles == ["shared"] && eligiblePackage entry
            )
            catalog;
          excludableNames = lib.mapAttrsToList (_: entry: lib.getName (packageFor entry)) standalonePackages;
          unknownExclusions = builtins.filter (name: !(builtins.elem name excludableNames)) cfg.excludedPackages;
          eligiblePackage = entry:
            entry.providers.nix.packageOnly or false
            && supplierSupported entry "nix"
            && packageFor entry != null;
          knownNames =
            map (r: r.packageName)
            (builtins.filter (r: r.deployment == "home") nixRows);
          extras = lib.concatMap (definition:
            map (package: {
              id = lib.getName package;
              area = "native";
              kind = "program";
              deployment = "home";
              supported = true;
              selected = true;
              provider = "nix";
              identifier = lib.getName package;
              requestedVersion = null;
              lockedVersion = package.version or null;
              installedVersion = null;
              owner = definition.file;
              source = "native-home";
            }) (builtins.filter (p: lib.isDerivation p && !(builtins.elem (lib.getName p) knownNames)) definition.value))
          options.home.packages.definitionsWithLocations;
          nativeIds = map (row: row.id) extras;
          nixNames = map lib.getName (builtins.filter lib.isDerivation config.home.packages);
          profileEnabled = name: builtins.elem name cfg.areas && (name != "agents" || cfg.agents.enable);
          groupDefault = entry: let
            override = cfg.groups.${entry.group};
          in
            if override == null
            then lib.any profileEnabled entry.profiles
            else override;
        in {
          options.providerTools = {
            agents.enable = lib.mkOption {
              type = lib.types.bool;
              default = true;
              description = "Enable the default coding-agent profile.";
            };
            groups = lib.genAttrs groupNames (name:
              lib.mkOption {
                type = lib.types.nullOr lib.types.bool;
                default = null;
                description = "Override selection for programs in the ${name} directory.";
              });
            areas = lib.mkOption {
              type = lib.types.listOf lib.types.str;
              internal = true;
              default = [];
            };
            programs = lib.mkOption {
              default = {};
              type = lib.types.attrsOf (lib.types.submodule ({name, ...}: let
                entry = catalog.${name} or (throw "providerTools.programs: unknown program ID ${name}");
              in {
                options = {
                  enable = lib.mkOption {
                    type = lib.types.bool;
                    default =
                      supported entry
                      && available entry
                      && (groupDefault entry || (name == "mise" && miseRows != []))
                      && !(excluded entry);
                  };
                  provider = lib.mkOption {
                    type = lib.types.enum (builtins.attrNames entry.providers);
                    default = defaultProvider name entry;
                  };
                  version = lib.mkOption {
                    type = lib.types.nullOr lib.types.nonEmptyStr;
                    default = null;
                  };
                };
              }));
            };
            inventory = lib.mkOption {
              type = lib.types.listOf lib.types.attrs;
              readOnly = true;
            };
            homebrew = lib.mkOption {
              type = lib.types.attrs;
              readOnly = true;
              internal = true;
            };
            mise.tools = lib.mkOption {
              type = lib.types.attrsOf lib.types.str;
              readOnly = true;
            };
          };
          config = {
            home.packages = lib.concatMap (row: let
              entry = catalog.${row.id};
            in
              lib.optional (entry.providers.nix.packageOnly or false) (packageFor entry))
            (builtins.filter (row: row.deployment == "home") nixRows);
            providerTools = {
              areas = ["shared"];
              programs = lib.mapAttrs (_: _: {}) catalog;
              inventory =
                builtins.filter (row: row.selected || !(builtins.elem row.id nativeIds)) rows
                ++ lib.unique extras;
              homebrew = {
                brews = map (supply: supply.identifier) (builtins.filter (supply: supply.kind == "formula") brewSupplies);
                casks = map (supply: supply.identifier) (builtins.filter (supply: supply.kind == "cask") brewSupplies);
              };
              mise.tools = builtins.listToAttrs (map (r: {
                  name = r.identifier;
                  value = r.requestedVersion;
                })
                miseRows);
            };
            assertions =
              [
                {
                  assertion = lib.all (id: builtins.hasAttr id catalog) (builtins.attrNames cfg.programs);
                  message = "providerTools.programs: unknown program ID";
                }
                {
                  assertion = unknownExclusions == [];
                  message = "providerTools.excludedPackages names no provider package: ${lib.concatStringsSep " " unknownExclusions}";
                }
              ]
              ++ lib.concatLists (lib.mapAttrsToList (id: entry: let
                  choice = cfg.programs.${id};
                  nixPackage =
                    if entry.providers ? nix
                    then packageFor entry
                    else null;
                  nixName =
                    if nixPackage == null
                    then id
                    else lib.getName nixPackage;
                in [
                  {
                    assertion = !choice.enable || supported entry;
                    message = "providerTools: unsupported platform for ${id}";
                  }
                  {
                    assertion = !choice.enable || available entry;
                    message = "providerTools: ${id} requires a host class from ${lib.concatStringsSep ", " entry.requiredClasses}";
                  }
                  {
                    assertion = !choice.enable || choice.version == null || choice.provider == "mise";
                    message = "providerTools: version constraints require mise for ${id}; Nix versions come from the lock";
                  }
                  {
                    assertion = !(choice.enable && choice.provider == "mise" && builtins.elem nixName nixNames);
                    message = "providerTools: duplicate Nix/mise ownership for ${id}";
                  }
                  {
                    assertion = !choice.enable || choice.provider != "nix" || !(entry.providers.nix.packageOnly or false) || packageFor entry != null;
                    message = "providerTools: Nix package for ${id} is missing";
                  }
                  {
                    assertion = !choice.enable || supplierSupported entry choice.provider;
                    message = "providerTools: unsupported supplier platform for ${id}";
                  }
                ])
                catalog);
          };
        };
        desktop.providerTools.areas = ["desktop"];
        linuxGraphical.providerTools.areas = ["linuxGraphical"];
        darwin.providerTools.areas = ["darwin"];
        agents.providerTools.areas = ["agents"];
        wsl.providerTools.areas = ["wsl"];
      };
    };
  };
}
