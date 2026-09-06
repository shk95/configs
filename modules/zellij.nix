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
  # zellij's `Grid::add_character` drops every zero-width code point, so the
  # conjoining jamo of a decomposed Hangul syllable never reach the pane and
  # composed Korean disappears inside zellij (zellij-org/zellij#3667, #1538).
  # Upstream PR zellij-org/zellij#5500 attaches combining marks instead of
  # dropping them; it is unmerged, so this overlay carries its commit until a
  # nixpkgs zellij already contains the fix. Darwin only: the symptom was
  # reported there and the Linux homes stay on the unpatched package, so
  # `optionalAttrs` yields `{}` for them.
  #
  # The patch adds the crate `unicode-properties` to `Cargo.lock`, so the
  # vendored dependency set changes with it. Pinned nixpkgs' `buildRustPackage`
  # computes `cargoDeps` at call time from `args.cargoHash`, which
  # `overrideAttrs` cannot reach; overriding `cargoDeps` itself with
  # `rustPlatform.fetchCargoVendor` — which takes `src` and `patches` — is what
  # takes effect. The `zellij` wrapper takes `zellij-unwrapped` as a function
  # argument, so overriding the unwrapped package propagates to it.
  #
  # The Mac observed on 2026-09-06 (#178) that the commit as pinned attaches
  # Unicode general category Mark only, and a decomposed syllable's medial
  # vowel and final consonant are letters (`Lo`) that `unicode-width` gives
  # zero width, so `add_character` still dropped them. `postPatch` below
  # carries the addition until zellij-org/zellij#5500 does: the jamo ranges are
  # accepted beside category Mark, and a Hangul grid test goes with them. The
  # substitution is `--replace-fail`, so a pinned commit that no longer has
  # that exact function fails the build at the patch phase instead of
  # silently building without the addition. The addition touches no
  # `Cargo.lock`, so the `cargoDeps` hash is unchanged by it.
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
      url = "https://github.com/zellij-org/zellij/commit/8e02033f0bb8bdb53acf1484cb81605d0f3671dc.patch";
      hash = "sha256-2l8tJEnvVnc18idfjIvXvCxw6sJ4rfX9Fk5q2F6HE74=";
    };
    patched = prev.zellij-unwrapped.overrideAttrs (old: {
      patches = (old.patches or []) ++ [patch];
      cargoDeps = prev.rustPlatform.fetchCargoVendor {
        inherit (old) pname version src;
        patches = [patch];
        hash = "sha256-YDlaeHEXGXExbJVB31A/QuYDQbsQ+c8T576h3DYb/gE=";
      };
      postPatch =
        (old.postPatch or "")
        + ''
          substituteInPlace zellij-server/src/panes/grid.rs \
            --replace-fail \
              'fn is_combining_mark(character: char) -> bool {
              matches!(
                  character.general_category_group(),
                  GeneralCategoryGroup::Mark
              )
          }' \
              'fn is_combining_mark(character: char) -> bool {
              matches!(
                  character.general_category_group(),
                  GeneralCategoryGroup::Mark
              ) || is_hangul_conjoining_jamo_vowel_or_final(character)
          }

          /// The medial vowels and final consonants of the Hangul Jamo block and its extensions.
          /// They are letters rather than marks, but they are zero width because they conjoin with
          /// the leading consonant before them: a decomposed syllable is one leading consonant
          /// followed by them, and dropping them is what turns Korean into its first jamo.
          fn is_hangul_conjoining_jamo_vowel_or_final(character: char) -> bool {
              matches!(
                  character,
                  '"'"'\u{1160}'"'"'..='"'"'\u{11FF}'"'"'
                      | '"'"'\u{D7B0}'"'"'..='"'"'\u{D7C6}'"'"'
                      | '"'"'\u{D7CB}'"'"'..='"'"'\u{D7FB}'"'"'
              )
          }'
          cat >>zellij-server/src/panes/unit/grid_tests.rs <<'RUST'

          #[test]
          fn hangul_conjoining_jamo_attach_to_the_leading_consonant() {
              // A decomposed syllable is a leading consonant followed by a medial vowel and a final
              // consonant. All three are letters rather than marks, and the vowel and the final are
              // zero width because they conjoin with the consonant before them, so they attach as
              // marks do: U+1112 U+1161 U+11AB is one wide cell, not one cell and two dropped
              // code points.
              let grid = create_grid_with_content("\u{1112}\u{1161}\u{11ab}a");

              assert_eq!(rendered_row(&grid, 0), "\u{1112}\u{1161}\u{11ab}a");
              assert_eq!(cursor_position(&grid), Some((3, 0)));
          }
          RUST
        '';
      cargoTestFlags = ["-p" "zellij-server"];
      checkFlags = ["combining_mark" "thai_vowels" "hangul_conjoining"];
    });
  in
    prev.lib.optionalAttrs prev.stdenv.hostPlatform.isDarwin {
      zellij-unwrapped =
        if prev.zellij-unwrapped.version == appliesTo
        then patched
        else throw "modules/zellij.nix: zellij ${prev.zellij-unwrapped.version} is not ${appliesTo}; re-check zellij-org/zellij#5500 (provisional/unixlike/zellij-combining-marks.md, CONTRIBUTING § zellij overlay)";
    };
}
