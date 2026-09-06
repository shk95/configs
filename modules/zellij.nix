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
# repository itself declares, the WSL homes included: their Windows Terminal is
# set to a light scheme by windows/desired/files/terminal/settings.json, in the
# Windows domain, which names the family it adopts on its own schedule and has
# no obligation to move when this side does. Reading that file is a
# cross-domain read by a person and not by code; nothing here imports or opens
# it. The premise and the condition that would reopen it are recorded in
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

  # PROV unixlike/zellij-combining-marks
  #
  # zellij's `Grid::add_character` drops every zero-width code point
  # (zellij-org/zellij#1538; #3667 is the same defect seen through decomposed
  # Latin), so the conjoining jamo of a decomposed Hangul syllable never reach
  # the pane and composed Korean disappears inside zellij. Upstream PR
  # zellij-org/zellij#5500 attaches combining marks — and, since 2026-09-06,
  # Hangul jungseong and jongseong, which are letters of zero width rather than
  # marks — instead of dropping them; it is unmerged, so this overlay carries
  # its commits until a nixpkgs zellij already contains the fix. Darwin only:
  # the symptom was reported there and the Linux homes stay on the unpatched
  # package, so `optionalAttrs` yields `{}` for them.
  #
  # The pin is the pull request's commit range, base...head, fetched as one
  # patch from the compare URL rather than commit by commit: the later
  # commits build on the first one's cells and the readback fix cannot apply
  # without the Hangul one before it, so the set is one unit. `excludes` drops
  # `CHANGELOG.md`, which the range rewrites four times and which does not
  # apply to the v0.45.1 tag; it is release notes, not code. The head commit
  # is what `just zellij-patch-check` and the watcher read as the pin.
  #
  # The patch adds the crate `unicode-properties` to `Cargo.lock`, so the
  # vendored dependency set changes with it. Pinned nixpkgs' `buildRustPackage`
  # computes `cargoDeps` at call time from `args.cargoHash`, which
  # `overrideAttrs` cannot reach; overriding `cargoDeps` itself with
  # `rustPlatform.fetchCargoVendor` — which takes `src` and `patches` — is what
  # takes effect. The `zellij` wrapper takes `zellij-unwrapped` as a function
  # argument, so overriding the unwrapped package propagates to it.
  #
  # Pinned nixpkgs' `buildRustPackage` runs `cargo test` in the root crate
  # alone, so the PR's grid tests never ran in the Darwin build
  # (docs/decisions/zellij-patched-on-darwin-until-upstream.md § Retiring the
  # overlay). `cargoTestFlags` and `checkFlags` point the check at
  # `zellij-server` and at the combining-mark tests by name, so the build
  # proves the grid behaviour it was built for, on the host it is built for.
  #
  # `appliesTo` is the zellij version the patch was verified against. A
  # different version is a `throw` rather than a silent passthrough because an
  # unpatched Darwin zellij is indistinguishable from a patched one until
  # someone types Korean into it; refusing to evaluate is the only signal that
  # arrives before that.
  nixpkgsOverlays.zellij = _final: prev: let
    appliesTo = "0.45.0";
    patch = prev.fetchpatch {
      name = "zellij-pr5500-combining-marks.patch";
      url = "https://github.com/zellij-org/zellij/compare/bf8d23a4f774abf27a108da2a1a2689e7d8d0d23...cbb7b1650fcd4aff79e54b31f31c5729c1391e90.patch";
      excludes = ["CHANGELOG.md"];
      hash = "sha256-nYFgAPk4sTTx7Vf2+J3k4G8DOTB0mfE3rocidlUS/L0=";
    };
    patched = prev.zellij-unwrapped.overrideAttrs (old: {
      patches = (old.patches or []) ++ [patch];
      cargoDeps = prev.rustPlatform.fetchCargoVendor {
        inherit (old) pname version src;
        patches = [patch];
        hash = "sha256-YDlaeHEXGXExbJVB31A/QuYDQbsQ+c8T576h3DYb/gE=";
      };
      cargoTestFlags = ["-p" "zellij-server"];
      checkFlags = [
        "combining_mark"
        "thai_vowels"
        "hangul_conjoining"
        "keeps_the_combining_marks"
        "is_not_trailing_whitespace"
      ];
    });
  in
    prev.lib.optionalAttrs prev.stdenv.hostPlatform.isDarwin {
      zellij-unwrapped =
        if prev.zellij-unwrapped.version == appliesTo
        then patched
        else throw "modules/zellij.nix: zellij ${prev.zellij-unwrapped.version} is not ${appliesTo}; re-check zellij-org/zellij#5500 (provisional/unixlike/zellij-combining-marks.md, CONTRIBUTING § zellij overlay)";
    };
}
