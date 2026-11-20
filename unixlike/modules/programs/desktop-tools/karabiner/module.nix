# Provider settings use finite whole-unit ownership and explicit host documents.
# INV unixlike/host-written-payload-projected
# INV unixlike/composition-in-one-place
#
# This concern contributes only to modules.homeManager.darwin. App selection and
# lifecycle remain consumer-owned. The final selected-app/appSettings gates and
# each unit enable flag decide document loading and apply independently.
#
# One versioned units.json supplies ownership and bounded shape constraints to
# pure Nix consumption and the shared native adapter/capture engine. Disabled
# documents remain unread. Source=configs uses defaults with dormant data retained
# in the host document; source=host replaces the unit without merging defaults.
#
# Home Manager runs the permanent adapter as the home user after writeBoundary,
# with explicit locked Python, a pinned concern source and absolute native readers.
# Its run wrapper preserves dry-run behavior. Files are replaced atomically and
# symbolic hotkeys use individual defaults -dict-add writes, preserving siblings.
#
# The legacy concern-local tool remains exact project/marker compatibility for
# the separate capture-to-Git caller until its repository-owned retirement.
# It is not the host-document adapter or a dependency of the new capture command.
_: {
  programCatalog.karabiner-elements = {
    profiles = ["darwin"];
    requiredClasses = ["darwin"];
    platforms = ["aarch64-darwin"];
    providers = {
      homebrew = {
        identifier = "karabiner-elements";
        kind = "cask";
      };
    };
  };
  modules.homeManager.darwin = {
    pkgs,
    lib,
    config,
    ...
  }: let
    contract = builtins.fromJSON (builtins.readFile ./units.json);
    validation = import ../../../../tool/darwin-capture/validation.nix {inherit lib contract;};
    capture = config.providerDarwin.capture;
    selected =
      config.providerTools.programs.karabiner-elements.enable
      && builtins.elem "karabiner-elements" config.providerDarwin.homebrew.casks
      && config.providerDarwin.appSettings.enable
      && config.providerDarwin.appSettings.karabiner;
    effective = unit: selected && unit.enable;
    settings = unit: option: fallback:
      if option.settingsDocument == null
      then fallback
      else let
        doc = validation.document unit option.settingsDocument;
      in
        if doc.source == "configs"
        then fallback
        else pkgs.writeText "${unit}-host-settings.json" (builtins.toJSON doc.settings);
    karabiner = effective capture.karabiner;
    hotkeys = effective capture.symbolicHotkeys;
    unitOptions = key: name: {
      enable = lib.mkOption {
        type = lib.types.bool;
        default = capture.${key}.settingsDocument != null;
        defaultText = lib.literalExpression "settingsDocument != null";
        description = "Apply this unit when Karabiner settings are selected. An explicit enable without a document uses the public example.";
      };
      settingsDocument = lib.mkOption {
        type = lib.types.nullOr lib.types.path;
        default = null;
        description = "Explicit version-1 host/configs source document for ${name}. Disabled units do not read it.";
      };
    };
  in {
    options.providerDarwin.capture = {
      karabiner = unitOptions "karabiner" "Karabiner";
      symbolicHotkeys = unitOptions "symbolicHotkeys" "symbolic hotkeys 60/61";
    };
    config = {
      home.activation = lib.mkIf (karabiner || hotkeys) {
        karabinerDesiredState = lib.hm.dag.entryAfter ["writeBoundary"] ''
          CONFIGS_CAPTURE_CONCERN=${./.} run ${pkgs.python3}/bin/python3 \
            ${../../../../tool/darwin-capture}/adapter.py apply \
            ${lib.optionalString karabiner "--unit karabiner --settings ${settings "karabiner" capture.karabiner ./karabiner.json}"} \
            ${lib.optionalString hotkeys "--unit symbolic-hotkeys --settings ${settings "symbolic-hotkeys" capture.symbolicHotkeys ./symbolic-hotkeys.json}"}
        '';
      };
    };
  };
}
