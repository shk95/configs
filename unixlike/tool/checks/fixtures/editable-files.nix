# INV unixlike/editable-file-generation-backup
{provider}: let
  lib = provider.inputs.nixpkgs.lib;
  git = {
    name = "Example";
    email = "example@example.invalid";
  };
  homePath = "/home/" + "example";
  macPath = "/Users/" + "example";
  homeArgs = {
    system = "x86_64-linux";
    user = "example";
    homeDirectory = homePath;
    inherit git;
    environment.graphical = true;
  };
  macArgs = {
    system = "aarch64-darwin";
    user = "example";
    inherit git;
    systemModules = [
      {
        system.primaryUser = "example";
        users.users.example.home = macPath;
        homebrew.casks = ["ghostty"];
      }
    ];
  };
  linux = (provider.lib.mkHome homeArgs).config;
  mac = (provider.lib.mkDarwin macArgs).config.home-manager.users.example;
  unmanagedNix = provider.lib.mkDarwin (macArgs
    // {
      homeModules = [
        {
          nix.enable = false;
          nix.package = lib.mkForce null;
        }
      ];
    });
  xdgMac = (provider.lib.mkDarwin (macArgs // {homeModules = [{xdg.enable = true;}];})).config.home-manager.users.example;
  future = (provider.lib.mkHome (homeArgs // {homeModules = [{xdg.configFile."wezterm/future.lua".text = "return {}";}];})).config;
  restored = (provider.lib.mkHome (homeArgs // {homeModules = [{configs.editableFiles."${homePath}/.config/zellij/config.kdl" = false;}];})).config;
  selected = home: lib.attrNames (lib.filterAttrs (_: enabled: enabled) home.configs.editableFiles);
  # Only provider-owned compositions are inspected here. Consumer extensions
  # are not restricted by an assertion in the reusable Home Manager module.
  ownershipConflicts = home:
    lib.concatMap (name: let
      target = home.home.file.${name}.target;
      overlaps = other: target == other || lib.hasPrefix "${target}/" other || lib.hasPrefix "${other}/" target;
    in
      map (other: "${name} <-> ${other}") (lib.attrNames (lib.filterAttrs
        (other: file: (file.enable || (other != name && (home.configs.editableFiles.${other} or false))) && overlaps file.target)
        home.home.file))) (selected home);
  providerHomes =
    lib.mapAttrsToList (name: home: {
      name = "homeConfigurations.${name}";
      inherit (home) config;
    })
    provider.homeConfigurations
    ++ lib.concatMap (family:
      lib.concatLists (lib.mapAttrsToList (name: system:
        lib.mapAttrsToList (account: home: {
          name = "${family}.${name}.${account}";
          config = home;
        }) (system.config.home-manager.users or {}))
      provider.${family})) ["nixosConfigurations" "darwinConfigurations"]
    ++ [
      {
        name = "Linux desktop";
        config = linux;
      }
      {
        name = "Darwin desktop";
        config = mac;
      }
      {
        name = "Darwin XDG";
        config = xdgMac;
      }
    ];
  # Small conflicting declarations exercise the checker itself without
  # treating a consumer's additional declarations as provider-owned policy.
  ownershipFixture = target: enable: {
    configs.editableFiles.editable = true;
    home.file = {
      editable = {
        target = ".config/example/config";
        enable = false;
      };
      ordinary = {inherit target enable;};
    };
  };
  weztermNames = [
    "wezterm.lua"
    "fonts.json"
    "config/appearance.lua"
    "config/behavior.lua"
    "config/bindings.lua"
    "config/fonts.lua"
    "config/startup.lua"
    "platform/darwin.lua"
    "platform/linux.lua"
    "platform/windows.lua"
  ];
  expected = root: paneru:
    lib.sort builtins.lessThan (
      ["${root}/.config/zellij/config.kdl" "${root}/.config/ghostty/config"]
      ++ map (name: "${root}/.config/wezterm/${name}") weztermNames
      ++ lib.optional paneru ".paneru.lua"
    );
  check = name: passed: {inherit name passed;};
  cases =
    [
      (check "Linux exact file selection" (selected linux == expected homePath false))
      (check "Darwin exact file selection" (selected mac == expected macPath true))
      (check "externally managed Nix package" (lib.hasSuffix ".drv" unmanagedNix.config.system.build.toplevel.drvPath))
      (check "XDG Paneru follows actual target" (builtins.elem "${macPath}/.config/paneru/init.lua" (selected xdgMac) && !(builtins.elem ".paneru.lua" (selected xdgMac))))
      (check "selected files bypass ordinary links" (builtins.all (name: !mac.home.file.${name}.enable) (selected mac)))
      (check "Ghostty theme retains normal link" mac.xdg.configFile."ghostty/themes/Bluegray Light".enable)
      (check "new WezTerm files retain normal links" (future.xdg.configFile."wezterm/future.lua".enable && !(builtins.elem "${homePath}/.config/wezterm/future.lua" (selected future))))
      (check "per-file opt-in to links" restored.xdg.configFile."zellij/config.kdl".enable)
      (check "preflight is before write boundary" (builtins.elem "writeBoundary" mac.home.activation.checkEditableFiles.before))
      (check "copy is after write boundary before links" (builtins.elem "writeBoundary" mac.home.activation.installEditableFiles.after && builtins.elem "linkGeneration" mac.home.activation.installEditableFiles.before))
      (check "callbacks follow installation and links" (builtins.elem "linkGeneration" mac.home.activation.onEditableFilesChange.after && builtins.elem "installEditableFiles" mac.home.activation.onEditableFilesChange.after))
      (check "dry-run uses Home Manager run" (lib.hasPrefix "run " mac.home.activation.installEditableFiles.data))
      (check "all constructors still evaluate" (builtins.all (path: lib.hasSuffix ".drv" path) [
        (provider.lib.mkHome homeArgs).activationPackage.drvPath
        (provider.lib.mkDarwin macArgs).config.system.build.toplevel.drvPath
      ]))
      (check "ownership accepts separate paths" (ownershipConflicts (ownershipFixture ".config/other/config" true) == []))
      (check "ownership rejects identical targets" (ownershipConflicts (ownershipFixture ".config/example/config" true) != []))
      (check "ownership rejects an editable entry still enabled for ordinary placement" (ownershipConflicts (lib.recursiveUpdate (ownershipFixture ".config/other/config" false) {home.file.editable.enable = true;}) != []))
      (check "ownership rejects duplicate editable targets" (ownershipConflicts ((ownershipFixture ".config/example/config" false)
        // {
          configs.editableFiles = {
            editable = true;
            ordinary = true;
          };
        })
      != []))
      (check "ownership rejects an ordinary ancestor" (ownershipConflicts (ownershipFixture ".config/example" true) != []))
      (check "ownership rejects an ordinary descendant" (ownershipConflicts (ownershipFixture ".config/example/config/child" true) != []))
      (check "ownership accepts a distinct sibling prefix" (ownershipConflicts (ownershipFixture ".config/example/config-other" true) == []))
      (check "ownership ignores disabled ordinary files" (ownershipConflicts (ownershipFixture ".config/example/config" false) == []))
    ]
    ++ map (home: let
      conflicts = ownershipConflicts home.config;
    in
      check "provider file ownership: ${home.name}${lib.optionalString (conflicts != []) " (${lib.concatStringsSep ", " conflicts})"}" (conflicts == []))
    providerHomes;
in {
  count = builtins.length cases;
  failures = map (item: item.name) (builtins.filter (item: !item.passed) cases);
}
