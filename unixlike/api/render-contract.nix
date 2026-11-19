# Render the contract to a separate file, then replace contract.json:
# nix eval --no-write-lock-file --impure --json --file unixlike/api/render-contract.nix | jq -S .
let
  base = import ./contract.nix;
  provider = builtins.getFlake "path:${toString ../.}";
  inherit (provider.inputs.nixpkgs) lib;
  catalog = provider.lib.programCatalog;
  groupNames = lib.unique (map (program: program.group) (builtins.attrValues catalog));
  selection = provider.homeConfigurations.example.options.providerTools;
  exampleId = builtins.head (builtins.attrNames catalog);
  programOptions = selection.programs.type.nestedTypes.elemType.getSubOptions ["providerTools" "programs" exampleId];
  optionType = option:
    {type = option.type.name;}
    // lib.optionalAttrs (option.type.name == "nullOr") {
      elementType = option.type.nestedTypes.elemType.name;
    };
  withDefault = option: optionType option // {inherit (option) default;};
  sorted = lib.sort builtins.lessThan;
in
  base
  // {
    programSelection = {
      moduleArgument = "homeModules";
      constructors = builtins.attrNames (lib.filterAttrs (_: entry: entry.inputs ? homeModules) base.entryPoints);
      optionsPrefix = "providerTools";
      catalog = "lib.programCatalog";
      inventory = "config.providerTools.inventory";
      precedence = ["program" "group" "profile"];
      agents.enable = withDefault selection.agents.enable;
      groups = lib.genAttrs groupNames (name: withDefault selection.groups.${name});
      programOptions = {
        enable = optionType programOptions.enable;
        provider = optionType programOptions.provider;
        version = withDefault programOptions.version // {supplier = "mise";};
      };
      programs = lib.mapAttrs (_: program:
        {
          inherit (program) group;
          profiles = sorted program.profiles;
          platforms = sorted program.platforms;
          requiredClasses = sorted program.requiredClasses;
          suppliers = builtins.attrNames program.providers;
          supplierPlatforms = lib.mapAttrs (_: supplier: sorted supplier.platforms) program.providers;
        }
        // lib.optionalAttrs (program.defaults != {}) {inherit (program) defaults;})
      catalog;
    };
  }
