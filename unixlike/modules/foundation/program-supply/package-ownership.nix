# Keep each package with the module that owns its installation.
# INV unixlike/package-ownership
{inputs, ...}: let
  # A definition made from an input's own tree is the evaluator's, whatever
  # the file; every other file, this repository's included, is its own owner.
  # A repository file is named by its path alone: flake-parts appends
  # ", via option modules.<class>.<name>" to the location, which says where
  # the definition was routed rather than who made it. A module given inline,
  # as the fixtures do, has no file and is named the way the module system
  # names it.
  frameworks = map toString [inputs.nixpkgs inputs.home-manager inputs.nix-darwin inputs.nixos-wsl];
  ownerOf = lib: file:
    if builtins.any (root: lib.hasPrefix root file) frameworks
    then "the evaluator's own modules"
    else builtins.head (lib.splitString ", via option " (lib.removePrefix (toString inputs.self + "/") file));

  # name -> owners, from an option's definitions with their locations.
  ownersByName = lib: definitions:
    lib.foldl' (
      acc: definition: let
        owner = ownerOf lib definition.file;
        names = map lib.getName (builtins.filter lib.isDerivation definition.value);
      in
        lib.foldl' (inner: name: inner // {${name} = lib.unique ((inner.${name} or []) ++ [owner]);}) acc names
    ) {}
    definitions;

  homeRule = {
    lib,
    options,
    ...
  }: let
    shared = lib.filterAttrs (_: owners: builtins.length owners > 1) (ownersByName lib options.home.packages.definitionsWithLocations);
  in {
    assertions = [
      {
        assertion = shared == {};
        message = "INV unixlike/package-ownership: a package has one declaring module, but ${
          lib.concatStringsSep "; " (lib.mapAttrsToList (name: owners: "${name} is declared by ${lib.concatMapStringsSep " and " (o: "'${o}'") owners}") shared)
        }.";
      }
    ];
  };

  # The system layer: a name this repository declares in both places, outside
  # the two shells the evaluators own. Today nix-darwin contributes those two
  # itself, so the framework filter already admits them; the list keeps the
  # decision's exception in force should a repository module ever declare
  # them, rather than leaving it to the filter to imply.
  systemRule = user: {
    lib,
    options,
    config,
    ...
  }: let
    evaluatorOwned = ["zsh" "nix-zsh-completions"];
    systemNames =
      builtins.attrNames (lib.filterAttrs (_: owners: builtins.any (o: o != "the evaluator's own modules") owners)
        (ownersByName lib options.environment.systemPackages.definitionsWithLocations));
    homeNames = map lib.getName (builtins.filter lib.isDerivation config.home-manager.users.${user}.home.packages);
    shared = builtins.filter (name: !(builtins.elem name evaluatorOwned)) (lib.intersectLists systemNames homeNames);
  in {
    assertions = [
      {
        assertion = shared == [];
        message = "INV unixlike/package-ownership: ${lib.concatStringsSep " " shared} is declared both as a system package and in the managed home; a package belongs to one layer.";
      }
    ];
  };
in {
  modules = {
    homeManager.shared = {lib, ...}: {
      imports = [homeRule];
      options.providerTools.excludedPackages = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        default = [];
        description = "Names of unconfigured provider packages omitted from this home.";
      };
    };
    nixos.environment = {config, ...}: {imports = [(systemRule config.providerIdentity.user)];};
    darwin.environment = {config, ...}: {imports = [(systemRule config.providerIdentity.user)];};
  };
}
