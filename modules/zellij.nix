# Unix-like Zellij configuration. This began as an explicit adoption of the
# Windows keymap; each domain owns its copy and may change it independently.
#
# Colours are no longer split by class, and the asset is why. `programs.zellij`
# offers `themes` and `settings.theme`, but this module deliberately copies the
# KDL asset verbatim rather than letting Home Manager render one, so anything a
# class wanted to say about colour would have to be a per-class copy of that
# asset. Nothing wants to: the asset carries the whole answer and every class
# receives the same bytes.
#
# That answer is a `theme_dark`/`theme_light` pair, which zellij switches
# between from the host terminal's own colour-scheme report (CSI 2031 /
# DSR 997), plus a static `theme "flexoki-light"` for the terminals that never
# send one. A static `theme` is authoritative only until a report arrives, so
# the two do not fight: Ghostty answers the query and drives its own palette
# through the pair, while WezTerm — which has no colour-scheme private mode in
# the pinned build — and Windows Terminal — probed silent on 2026-09-05 on
# build 1.23.20211.0 — render the static line. The probe, the terminal table
# and the palette derivation are recorded in the asset itself.
#
# Pinning light for every class rather than for one is honest because every
# home this repository composes renders in a terminal whose scheme the
# repository itself declares, the WSL homes included: their Windows Terminal is
# set to Flexoki Light by windows/desired/files/terminal/settings.json, in the
# Windows domain. Reading that file is a cross-domain read by a person and not
# by code; nothing here imports or opens it. The premise and the condition that
# would reopen it are recorded in
# docs/decisions/composed-homes-render-in-declared-terminals.md.
#
# INV unixlike/composition-in-one-place — this file contributes one definition
# of one Home Manager option, `programs.zellij.extraConfig`, which Home Manager
# renders into config.kdl. It forces no value and names no host, so it decides
# nothing about which class wins; the composition file decides which classes a
# home gets. The keymap stays in exactly one place and no second payload
# appears under assets/; the file a host receives is Home Manager's rendering —
# a blank line and an `// extraConfig` marker, then the asset — rather than a
# link to the asset byte for byte, and tool/checks/payloads parses the asset,
# which is what every rendering is built from.
_: {
  modules.homeManager.shared = {pkgs, ...}: {
    programs.zellij = {
      enable = true;
      package = pkgs.zellij;
      extraConfig = builtins.readFile ../assets/zellij/config.kdl;
    };
  };
}
