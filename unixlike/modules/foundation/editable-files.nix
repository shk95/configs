# INV unixlike/editable-file-generation-backup
_: {
  modules.homeManager.shared = {
    config,
    lib,
    pkgs,
    ...
  }: let
    selected = lib.filterAttrs (_: enabled: enabled) config.configs.editableFiles;
    files = map (name: config.home.file.${name}) (lib.attrNames selected);
    manifest = pkgs.writeText "editable-files.json" (builtins.toJSON {
      schemaVersion = 1;
      home = config.home.homeDirectory;
      inherit (builtins) storeDir;
      lock = "${config.xdg.stateHome}/configs/editable-files.lock";
      files =
        map (file: {
          target = "${config.home.homeDirectory}/${file.target}";
          source = toString (config.lib.file.sourceStorePath file);
          executable = file.executable == true;
        })
        files;
    });
    command = lib.escapeShellArgs [
      "${pkgs.python3}/bin/python3"
      "${../../tool/editable-files}"
      "--manifest"
      manifest
      "--diff"
      "${pkgs.diffutils}/bin/diff"
      "--nix-store"
      "${pkgs.nix}/bin/nix-store"
    ];
  in {
    options.configs.editableFiles = lib.mkOption {
      type = lib.types.attrsOf lib.types.bool;
      default = {};
      description = ''
        Explicit home.file keys opting individual text configuration files out
        of store symlinks. Each activation backs up the previous contents as a
        diff against the incoming source, then installs a writable regular file.
        XDG entries use their absolute configHome/name key. False retains normal
        Home Manager deployment; directory selection is unsupported.
      '';
    };

    config = lib.mkIf (selected != {}) {
      # Keep generated sources available, but leave placement to this writer.
      xdg.configFile = lib.mapAttrs' (name: _:
        lib.nameValuePair
        (lib.removePrefix "${config.xdg.configHome}/" name) {enable = false;})
      (lib.filterAttrs (name: _: lib.hasPrefix "${config.xdg.configHome}/" name) selected);
      home.file = lib.mapAttrs (_: _: {enable = false;}) selected;
      assertions =
        map (file: {
          assertion = !file.recursive && !file.force;
          message = "INV unixlike/editable-file-generation-backup: editable files cannot use recursive or force placement (${file.target}).";
        })
        files;
      home.activation = {
        checkEditableFiles = lib.hm.dag.entryBefore ["writeBoundary"] ''
          ${command} --check
        '';
        installEditableFiles = lib.hm.dag.entryBetween ["linkGeneration"] ["writeBoundary"] ''
          run ${command} --generation "$newGenPath"
        '';
        onEditableFilesChange = lib.hm.dag.entryAfter ["linkGeneration" "installEditableFiles"] (
          lib.concatMapStrings (file:
            lib.optionalString (file.onChange != "") ''
              if [[ ! -v DRY_RUN ]]; then
                ${file.onChange}
              fi
            '')
          files
        );
      };
    };
  };
}
