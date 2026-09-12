# Karabiner's configuration file is desired state; the application is not.
#
# INV unixlike/host-written-payload-projected
#
# Karabiner-Elements is a Homebrew cask, declared once in
# `modules/darwin-homebrew.nix`, and stays there: this file declares no
# package and no service. `docs/decisions/homebrew-owns-mac-apps.md` is the
# rule, and nothing about managing the configuration changes who owns the
# application.
#
# The file is delivered by an activation script rather than by
# `xdg.configFile`, because Karabiner unlinks and rewrites
# `~/.config/karabiner/karabiner.json` on every save. A link into the Nix
# store would survive exactly until the first change made in the user
# interface, and the store path is read-only, so the save would either fail or
# replace the link with a plain file that no longer tracks the payload.
# `tool/darwin/karabiner apply` writes a copy instead, restricted to the
# top-level keys the payload declares, and leaves the host's own runtime keys
# in place. `docs/decisions/karabiner-desired-state-by-projection.md` records
# that choice and what was rejected.
#
# The same script writes the two macOS symbolic hotkeys the Korean
# input-source toggle depends on, so one activation entry covers both halves
# of one behaviour rather than splitting them across two.
#
# INV unixlike/composition-in-one-place: this file writes into
# `modules.homeManager.darwin` and stops there. It defines one activation
# entry that no other module defines, so no priority is overridden and
# nothing is forced; it names no host, and which hosts receive
# `homeManager.darwin` stays `modules/flake/configurations.nix`'s decision.
#
# `run` is Home Manager's own wrapper, so `--dry-run` reports the command
# instead of running it, and under nix-darwin the activation runs as the user
# whose Karabiner file this is. `JQ` hands the script the jq it already has,
# so the activation resolves nothing from PATH.
#
# That matters beyond jq. The PATH an activation script runs under is Home
# Manager's own inputs — bash, coreutils, diffutils, findutils, gettext,
# gnugrep, gnused, jq, ncurses and Nix — and the caller's PATH is appended only
# when `home.emptyActivationPath` is false, which on this home it is not. So
# /usr/bin is absent, and `defaults`, `plutil` and `activateSettings` would not
# resolve by name. Nothing is added to PATH here: `tool/darwin/karabiner`
# resolves those three itself, from PATH first and from their absolute macOS
# location second, so the fixtures can still shim them and the activation still
# finds them.
_: {
  modules.homeManager.darwin = {
    pkgs,
    lib,
    ...
  }: {
    home.activation.karabinerDesiredState = lib.hm.dag.entryAfter ["writeBoundary"] ''
      JQ=${pkgs.jq}/bin/jq run sh ${../tool/darwin/karabiner} apply \
        --payload ${../assets/karabiner/karabiner.json} \
        --hotkeys ${../assets/karabiner/symbolic-hotkeys.json}
    '';
  };
}
