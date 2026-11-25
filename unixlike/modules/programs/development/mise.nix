# Nix owns mise and this one fragment. config.toml and other local fragments
# remain writable and are never copied, deleted or pruned by this module.
_: {
  programCatalog.mise = {
    profiles = ["shared"];
    platforms = ["x86_64-linux" "aarch64-linux"];
    providers.nix.identifier = "mise";
  };
  modules.homeManager.shared = {
    config,
    lib,
    pkgs,
    ...
  }: let
    linux = pkgs.stdenv.hostPlatform.isLinux;
    tools = config.providerTools.mise.tools;
    emptySystem = pkgs.writeText "provider-empty-mise-system.toml" "";
    fragment = (pkgs.formats.toml {}).generate "provider-tools.toml" {
      inherit tools;
      settings = {
        # External release layouts evolve independently of the Nix-supplied
        # mise binary. Resolve these explicit aqua IDs from current metadata.
        aqua.baked_registry = false;
        experimental = false;
        lockfile = false;
        self_update.auto = false;
        tool_update.global_auto = false;
        upgrade.auto_prune = false;
      };
    };
  in {
    config = lib.mkMerge [
      {
        assertions = [
          {
            assertion = config.providerTools.programs.mise.enable || tools == {};
            message = "providerTools: mise-selected programs require mise";
          }
        ];
      }
      (lib.mkIf (linux && config.providerTools.programs.mise.enable) {
        home.packages = [pkgs.mise];
        xdg.configFile."mise/conf.d/10-provider.toml".source = fragment;
        # Append shims; don't install a prompt hook that prepends mutable tools.
        programs.zsh.initContent = lib.mkOrder 1100 ''
          path=("''${(@)path:#${config.xdg.dataHome}/mise/shims}" "${config.xdg.dataHome}/mise/shims")
        '';
        home.activation.providerMiseInstall = lib.mkIf (tools != {}) (lib.hm.dag.entryAfter ["writeBoundary" "linkGeneration"] ''
          if [ -z "''${DRY_RUN_CMD:-}" ]; then
            # Only declared tools: ignore project/local configs during this step.
            # With no explicit tool@latest, install reuses matching installations.
            if ! MISE_GLOBAL_CONFIG_FILE=${fragment} MISE_SYSTEM_CONFIG_FILE=${emptySystem} MISE_LOCKFILE=false \
              ${lib.getExe pkgs.mise} --cd / install; then
              echo ${lib.escapeShellArg "mise: failed to install declared tools: ${lib.concatStringsSep ", " (builtins.attrNames tools)}"} >&2
              exit 1
            fi
          fi
        '');
      })
    ];
  };
}
