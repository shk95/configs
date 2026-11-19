# Parse the same generated fragment with the locked, native mise executable.
# INV unixlike/generated-config-key-in-schema
{config, ...}: {
  perSystem = {pkgs, ...}: let
    sample = config.flake.homeConfigurations.example.config.xdg.configFile."mise/conf.d/10-provider.toml".source.drvAttrs.value;
    fragment = (pkgs.formats.toml {}).generate "provider-tools.toml" sample;
  in {
    checks.programs-mise-config =
      pkgs.runCommand "checked-provider-mise-config" {
        nativeBuildInputs = [pkgs.mise pkgs.jq];
      } ''
        export HOME="$TMPDIR/home"
        export XDG_CONFIG_HOME="$HOME/.config"
        export XDG_DATA_HOME="$HOME/.local/share"
        export XDG_CACHE_HOME="$HOME/.cache"
        export MISE_OFFLINE=true
        mkdir -p "$XDG_CONFIG_HOME/mise/conf.d"
        ln -s ${fragment} "$XDG_CONFIG_HOME/mise/conf.d/10-provider.toml"
        printf '[tools]\njq = "latest"\n' > "$XDG_CONFIG_HOME/mise/config.toml"
        cp "$XDG_CONFIG_HOME/mise/config.toml" before.toml
        mise settings ls --json > settings.json
        jq -e '.aqua.baked_registry == false and .lockfile == false and .upgrade.auto_prune == false and .self_update.auto == false and .tool_update.global_auto == false' settings.json
        mise config ls --json > configs.json
        grep -q '10-provider.toml' configs.json
        grep -q 'config.toml' configs.json
        cmp before.toml "$XDG_CONFIG_HOME/mise/config.toml"
        # Also start the parser a second time against the read-only store fragment.
        mise settings ls --json >/dev/null
        # A matching installed version must satisfy latest during application,
        # without consulting releases or replacing it with a new version.
        mkdir -p "$XDG_DATA_HOME/mise/installs/node/22.0.0/bin"
        printf '#!/bin/sh\necho fixture-node\n' > "$XDG_DATA_HOME/mise/installs/node/22.0.0/bin/node"
        chmod +x "$XDG_DATA_HOME/mise/installs/node/22.0.0/bin/node"
        printf '[tools]\nnode = "latest"\n' > reuse.toml
        touch empty-system.toml
        MISE_GLOBAL_CONFIG_FILE="$PWD/reuse.toml" MISE_SYSTEM_CONFIG_FILE="$PWD/empty-system.toml" mise install
        test -f "$XDG_DATA_HOME/mise/installs/node/22.0.0/bin/node"
        printf '[settings]\nlockfile = [\n' > malformed.toml
        if MISE_GLOBAL_CONFIG_FILE="$PWD/malformed.toml" mise config ls --json >diagnostic 2>&1; then
          echo "mise accepted malformed TOML" >&2
          exit 1
        fi
        mkdir "$out"
        cp settings.json configs.json "$out/"
      '';
  };
}
