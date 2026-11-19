# Unix-like Zellij configuration. This began as an explicit adoption of the
# Windows keymap; each domain owns its copy and may change it independently.
#
# Colours are no longer split by class. `programs.zellij` offers `themes` and
# `settings.theme`, but this module supplies the KDL payload as `extraConfig`.
# Home Manager renders it into config.kdl with its own header, and every class
# receives the same payload.
#
# That answer is a `theme_dark`/`theme_light` pair, which zellij switches
# between from the host terminal's own colour-scheme report (CSI 2031 /
# DSR 997), plus a static `theme "modus-operandi"` for the terminals that never
# send one. A static `theme` is authoritative only until a report arrives, so
# the two do not fight: Ghostty answers the query and drives its own palette
# through the pair, while WezTerm — which has no colour-scheme private mode in
# the pinned build — and Windows Terminal — probed silent on 2026-09-05 on
# build 1.23.20211.0 — render the static line. The probe, the terminal table
# and the palette derivation are recorded in the asset itself.
#
# Pinning light for every class rather than for one is honest because every
# home this repository composes renders in a terminal whose scheme the
# repository itself declares, the WSL homes included: Windows Terminal's
# desired state selects a light scheme in
# windows/desired/files/terminal/settings.json. The Windows domain names the
# family it adopts on its own schedule and has no obligation to move when
# this side does. Reading that file is a
# cross-domain read by a person and not by code; nothing here imports or opens
# it. The premise and the condition that would reopen it are recorded in
# docs/policy/decisions/unixlike/composed-homes-render-in-declared-terminals.md.
#
# INV unixlike/composition-in-one-place — this file contributes one definition
# of `programs.zellij.extraConfig` and the zsh function that sends a bare
# `zellij` to that payload's session. It forces no value and names no host;
# the composition file decides which classes a home gets. Home Manager adds
# a blank line and an `// extraConfig` marker before the KDL, while
# tool/checks/payloads parses the source payload.
#
_: let
  # A bare `zellij` starts the asset's `session_name` with
  # `attach_to_session`, and Zellij takes that path through
  # `attach_by_name`, which asks only whether a live session of that
  # name exists: an exited one is not consulted, so a new session starts under
  # the old name instead of resurrecting it. `zellij attach --create <name>`
  # also reads the serialised layout and resurrects before it creates, so the
  # shell sends a bare call there. Read the deployed KDL at invocation time so
  # editing its session_name does not require rebuilding the shell function.
  kdl = builtins.readFile ./config.kdl;
in {
  modules.homeManager.shared = {
    config,
    lib,
    pkgs,
    ...
  }: let
    sessionReader = pkgs.python3.withPackages (packages: [packages.kdl-py]);
  in {
    configs.editableFiles = lib.mkIf config.programs.zellij.enable {
      "${config.xdg.configHome}/zellij/config.kdl" = lib.mkDefault true;
    };
    programs.zellij = {
      enable = true;
      package = pkgs.zellij;
      extraConfig = kdl;
    };

    programs.zsh.initContent = ''
      zellij() {
        if (( $# == 0 )); then
          ${sessionReader}/bin/python3 ${../../../../tool/zellij-session} ${lib.escapeShellArg "${config.xdg.configHome}/zellij/config.kdl"}
        else
          command zellij "$@"
        fi
      }
    '';
  };
}
