# Packages with nothing to configure.
#
# INV unixlike/package-ownership — a package has one declaring module. A
# feature module owns it only when that module generates its configuration
# (`bat` moved out of here for exactly that reason, and `programs.bat`
# contributes the package itself); everything else is declared here once,
# whether or not Home Manager happens to offer a module for it. Enabling such
# a module for a package with nothing to configure is a behaviour change, not
# a tidy-up.
#
# The assertions at the end of this file are the schema half of that rule,
# and tool/checks/flake-test holds both directions. A home refuses a package
# name that two owners define, where an owner is a file of this repository or
# the evaluator's own modules taken together (Home Manager contributes `bat`
# on behalf of modules/bat.nix; that is one owner, and a second listing here
# would be the other). A system layer refuses a name this repository declares
# in both its system packages and the managed home, because installing the
# same interactive package into both is not a way to make it more available;
# the two evaluator-owned shells are the documented exception
# (docs/decisions/package-ownership-by-generating-module.md). Which packages
# a system module *should* hold is the reviewer's, not this check's.
#
# These are Home Manager packages rather than `environment.systemPackages`.
# That makes the same interactive tool set available to Darwin, NixOS-WSL, and
# standalone Home Manager on Ubuntu WSL. Under system-integrated Home Manager,
# `useUserPackages = true` still folds the packages into the host generation.
#
# Put a package in a system module only when a service, activation script, or
# root/system account needs it. Put macOS applications and tools whose behavior
# depends on Homebrew in `darwin-homebrew.nix`. Everything else belongs here so
# adding a system layer never removes it from the standalone configuration.
{
  config,
  inputs,
  ...
}: let
  wslUser = config.identity.wsl.user;
  darwinUser = config.identity.darwin.user;

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
        message = "INV unixlike/package-ownership: ${lib.concatStringsSep ", " shared} is declared both as a system package and in the managed home; a package belongs to one layer.";
      }
    ];
  };
in {
  modules = {
    homeManager.shared = {
      lib,
      pkgs,
      ...
    }: {
      # The home half of the ownership rule reaches every home through this
      # class; the system half reaches each system layer through its own class,
      # at the end of this file.
      imports = [homeRule];

      home.packages = with pkgs;
        [
          # search / text
          ripgrep
          fd
          fzf
          jq
          yq-go
          file
          gawk
          gnused
          pup

          # git tooling beyond programs.git — gh is modules/gh.nix, which also
          # generates the credential helper
          tig
          gitflow

          # the pre-commit hook's secret scan is a no-op without this, and on a
          # public repository CI only catches a leak after it is already published
          gitleaks
          bitwarden-cli

          # archives
          p7zip
          unzip
          zip
          xz
          zstd

          # network
          aria2
          caddy
          curl
          mkcert
          nmap
          rclone
          socat
          wget

          # languages / build tools
          go
          # Build tool only. JDKs are owned by SDKMAN, which shell.nix sources
          # optionally; do not add one here.
          gradle
          nodejs
          R

          # documents / media / data
          ghostscript
          glow
          gnutar
          monolith
          pocketbase
          poppler
          yt-dlp

          # session / monitoring
          tmux
          # btop is modules/btop.nix, which generates its configuration.
          pstree

          tree
          just
          gnupg
          which
        ]
        # The locked nixpkgs marks bettercap broken on Darwin. Homebrew owns the
        # macOS formula while Linux homes still receive the same command from Nix.
        ++ lib.optionals pkgs.stdenv.hostPlatform.isLinux [pkgs.bettercap];
    };

    nixos.wsl = systemRule wslUser;
    darwin.system = systemRule darwinUser;
  };
}
