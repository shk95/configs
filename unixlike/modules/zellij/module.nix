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
# of `programs.zellij.extraConfig`, which Home Manager renders into
# config.kdl, and the zsh function that sends a bare `zellij` to that asset's
# session. It forces no value and names no host, so it decides
# nothing about which class wins; the composition file decides which classes a
# home gets. The keymap stays in exactly one place and no second payload
# appears under assets/; the file a host receives is Home Manager's rendering —
# a blank line and an `// extraConfig` marker, then the asset — rather than a
# link to the asset byte for byte, and tool/checks/payloads parses the asset,
# which is what every rendering is built from.
#
# PROV unixlike/zellij-combining-marks
#
# zellij's `Grid::add_character` drops every zero-width code point
# (zellij-org/zellij#1538; #3667 is the same defect seen through decomposed
# Latin), so the conjoining jamo of a decomposed Hangul syllable never reach
# the pane and composed Korean disappears inside zellij. Upstream PR
# zellij-org/zellij#5500 attaches combining marks — and Hangul jungseong and
# jongseong, which are letters of zero width rather than marks — instead of
# dropping them; it is unmerged, so this file carries its commits until a
# nixpkgs zellij already contains the fix. Darwin only: the symptom was
# reported there and the Linux homes stay on the unpatched package, so the
# overlay yields `{}` for them.
#
# `combiningMarks` builds everything from one nixpkgs package set and is read
# twice: by the Darwin overlay, and by the flake checks at the end of this
# file on every system. The checks are how a Linux pre-push or the merge gate
# learns that the patch no longer applies to the lock's zellij before the Mac
# does, since both only evaluate the Darwin configuration.
#
# The pin is the pull request's commit range, base...head, fetched as one
# patch from the compare URL rather than commit by commit: the later commits
# build on the first one's cells and the readback fix cannot apply without the
# Hangul one before it, so the set is one unit. `excludes` drops
# `CHANGELOG.md`, which the range rewrites four times and which does not apply
# to the v0.45.1 tag; it is release notes, not code. The head commit is what
# the watcher reads as the pin.
#
# Nothing here names a zellij version. What once had to was the vendored
# dependency set: `fetchCargoVendor` over the patched source hashes that
# version's whole set, so every lock refresh that moved zellij needed a new
# hash. The patch changes the set by exactly one crate — its `Cargo.lock` hunk
# adds `unicode-properties` 0.1.4 — so the vendor directory is nixpkgs' own
# `cargoDeps` for whatever zellij the lock brings, with that hunk applied to
# its `Cargo.lock` and that one crate added in the shape
# `fetch-cargo-vendor-util.py` writes. `cargoSetupHook` accepts any directory
# and diffs its `Cargo.lock` against the patched source's, so no second
# fixed-output hash is needed. If upstream ever carries the crate itself, the
# hunk fails here and in the patch phase alike. The directory's name is
# anything but `source`, which is where the source unpacks beside it.
#
# The patch applies with `-F0`. At stdenv's default fuzz of 2, a tree that
# already carries the range had a hunk re-applied with fuzz 1, so a partially
# merged upstream could compile into code nobody wrote; with no fuzz it fails
# the patch phase loudly. That failure, not an evaluation-time version
# comparison, is what keeps an unpatched Darwin zellij from installing: either
# the patch applies or the build stops.
#
# Pinned nixpkgs' `buildRustPackage` runs `cargo test` in the root crate
# alone, so the PR's grid tests never ran in the Darwin build
# (docs/decisions/zellij-patched-on-darwin-until-upstream.md § Retiring the
# overlay). `cargoTestFlags` and `checkFlags` point the check at
# `zellij-server` and at the combining-mark tests by name. A filter that
# matches nothing still exits 0, and `-p zellij-server` runs a second test
# binary that reports `running 0 tests` on every build, so `postCheck` lists
# what the filters select and requires the nine tests the range carries. The
# listing repeats the flags and environment `cargoCheckHook` passes, so it
# compiles nothing.
_: let
  # PROV unixlike/zellij-combining-marks
  combiningMarks = pkgs: let
    inherit (pkgs) lib;
    upstream = pkgs.zellij-unwrapped;

    patch = pkgs.fetchpatch {
      name = "zellij-pr5500-combining-marks.patch";
      url = "https://github.com/zellij-org/zellij/compare/bf8d23a4f774abf27a108da2a1a2689e7d8d0d23...cbb7b1650fcd4aff79e54b31f31c5729c1391e90.patch";
      excludes = ["CHANGELOG.md"];
      hash = "sha256-nYFgAPk4sTTx7Vf2+J3k4G8DOTB0mfE3rocidlUS/L0=";
    };
    patchFlags = ["-p1" "-F0"];

    # The one crate the patch's `Cargo.lock` hunk adds, with the checksum that
    # hunk carries.
    crate = {
      name = "unicode-properties";
      version = "0.1.4";
      checksum = "7df058c713841ad818f1dc5d3fd88063241cc61f49f5fbea4b951e8cf5a8d71d";
    };
    crateTarball = pkgs.fetchurl {
      name = "${crate.name}-${crate.version}.tar.gz";
      url = "https://static.crates.io/crates/${crate.name}/${crate.version}/download";
      sha256 = crate.checksum;
    };

    cargoDeps =
      pkgs.runCommand "${upstream.pname}-${upstream.version}-vendor-pr5500" {
        nativeBuildInputs = [pkgs.patchutils];
      } ''
        cp -r --no-preserve=mode ${upstream.cargoDeps} "$out"
        filterdiff -p1 -i Cargo.lock ${patch} | patch -d "$out" -p1 -F0 --forward
        dir="$out/source-registry-0/${crate.name}-${crate.version}"
        if [ -e "$dir" ]; then
          echo "nixpkgs' vendor set already carries ${crate.name} ${crate.version}; re-check zellij-org/zellij#5500" >&2
          exit 1
        fi
        mkdir "$dir"
        tar xf ${crateTarball} -C "$dir" --strip-components=1
        printf '{"files": {}, "package": "%s"}' ${crate.checksum} >"$dir/.cargo-checksum.json"
      '';

    tests = [
      "combining_mark"
      "thai_vowels"
      "hangul_conjoining"
      "keeps_the_combining_marks"
      "is_not_trailing_whitespace"
    ];
    expectedTests = 9;

    package = upstream.overrideAttrs (old: {
      patches = (old.patches or []) ++ [patch];
      inherit patchFlags cargoDeps;
      cargoTestFlags = ["-p" "zellij-server"];
      checkFlags = tests;
      postCheck =
        (old.postCheck or "")
        + ''
          listed=$(${pkgs.rust.envVars.setEnv} cargo test -j "$NIX_BUILD_CORES" \
            ${lib.optionalString (old.cargoCheckType != "debug") "--profile ${old.cargoCheckType}"} \
            --target ${pkgs.stdenv.targetPlatform.rust.rustcTargetSpec} --offline \
            -p zellij-server -- --list ${lib.escapeShellArgs tests})
          printf '%s\n' "$listed" | grep ': test$' || true
          selected=$(printf '%s\n' "$listed" | grep -c ': test$' || true)
          if [ "$selected" -ne ${toString expectedTests} ]; then
            echo "the combining-mark filters selected $selected tests, not ${toString expectedTests}; re-check zellij-org/zellij#5500" >&2
            exit 1
          fi
        '';
    });

    # Everything the build does before it compiles: nixpkgs' source and
    # patches with the range appended, applied by stdenv's own patch phase
    # with the same flags, then `cargoSetupHook`'s `Cargo.lock` comparison
    # against the vendor directory above. It fetches only fixed-output sources
    # and compiles nothing, so every system can build it.
    applies = pkgs.stdenvNoCC.mkDerivation {
      name = "zellij-combining-marks-applies-${upstream.version}";
      inherit (upstream) src postPatch;
      patches = (upstream.patches or []) ++ [patch];
      inherit patchFlags cargoDeps;
      nativeBuildInputs = [pkgs.rustPlatform.cargoSetupHook];
      dontConfigure = true;
      dontBuild = true;
      installPhase = "touch $out";
      passthru = {
        inherit patch;
        inherit (upstream) version;
      };
    };

    # The same derivation over a tree that already carries the range, which is
    # how a merged upstream looks to it: stdenv's patch phase must refuse the
    # second copy. Reaching the last `applying patch` line shows the refusal
    # came from that copy and not from an earlier patch.
    refuses = applies.overrideAttrs (old: {
      name = "zellij-combining-marks-refuses-a-patched-tree-${upstream.version}";
      patches = old.patches ++ [patch];
      patchPhase = ''
        set +e
        (set -e; patchPhase) >"$TMPDIR/patch.log" 2>&1
        status=$?
        set -e
        reached=$(grep -c '^applying patch ' "$TMPDIR/patch.log" || true)
        if [ "$status" -eq 0 ]; then
          cat "$TMPDIR/patch.log"
          echo "the range applied a second time over itself" >&2
          exit 1
        fi
        if [ "$reached" -ne ${toString (lib.length old.patches + 1)} ]; then
          cat "$TMPDIR/patch.log"
          echo "the patch phase failed before it reached the second copy of the range" >&2
          exit 1
        fi
        tail -n 4 "$TMPDIR/patch.log"
      '';
      passthru = {};
    });

    # PROV unixlike/zellij-combining-marks
    # The same derivation over nixpkgs' own vendor set, which has neither the
    # range's `Cargo.lock` hunk nor its crate: every patch applies, and
    # `cargoSetupHook`'s post-patch comparison must refuse the vendor set.
    # Without it, `applies` would still pass if the hook were dropped from it
    # or its `cargoDeps` stopped carrying the hunk. Reaching the last `applying
    # patch` line and the hook's own `Cargo.lock is not the same in` line show
    # the refusal came from that comparison and not from a patch.
    refusesStaleVendor = applies.overrideAttrs (old: {
      name = "zellij-combining-marks-refuses-a-stale-vendor-${upstream.version}";
      inherit (upstream) cargoDeps;
      patchPhase = ''
        set +e
        (set -e; patchPhase) >"$TMPDIR/patch.log" 2>&1
        status=$?
        set -e
        reached=$(grep -c '^applying patch ' "$TMPDIR/patch.log" || true)
        if [ "$status" -eq 0 ]; then
          cat "$TMPDIR/patch.log"
          echo "the patch check accepted a vendor set without the range's Cargo.lock hunk" >&2
          exit 1
        fi
        if [ "$reached" -ne ${toString (lib.length old.patches)} ] \
          || ! grep -q '^Cargo.lock is not the same in ' "$TMPDIR/patch.log"; then
          cat "$TMPDIR/patch.log"
          echo "the check failed, but not in cargoSetupHook's Cargo.lock comparison" >&2
          exit 1
        fi
        grep '^Cargo.lock is not the same in ' "$TMPDIR/patch.log"
      '';
      passthru = {};
    });
  in {
    inherit package applies refuses refusesStaleVendor;
  };

  # A bare `zellij` starts the asset's `session_name` with
  # `attach_to_session`, and zellij 0.45.1 takes that path through
  # `attach_with_session_name`, which asks only whether a live session of that
  # name exists: an exited one is not consulted, so a new session starts under
  # the old name instead of resurrecting it. `zellij attach --create <name>`
  # also reads the serialised layout and resurrects before it creates, so the
  # shell sends a bare call there. The name is read from the asset rather than
  # restated, so the two cannot drift.
  kdl = builtins.readFile ./config.kdl;
  sessionMatch = builtins.match "(.*\n)?session_name \"([^\"]+)\"\n.*" kdl;
  sessionName =
    if sessionMatch == null
    then throw "modules/zellij: config.kdl declares no session_name for the bare zellij call to attach to."
    else builtins.elemAt sessionMatch 1;
in {
  modules.homeManager.shared = {pkgs, ...}: {
    programs.zellij = {
      enable = true;
      package = pkgs.zellij;
      extraConfig = kdl;
    };

    programs.zsh.initContent = ''
      zellij() {
        if (( $# == 0 )); then
          command zellij attach --create ${sessionName}
        else
          command zellij "$@"
        fi
      }
    '';
  };

  # PROV unixlike/zellij-combining-marks
  nixpkgsOverlays.zellij = _final: prev:
    prev.lib.optionalAttrs prev.stdenv.hostPlatform.isDarwin {
      zellij-unwrapped = (combiningMarks prev).package;
    };

  # PROV unixlike/zellij-combining-marks
  # Read from the flake's nixpkgs without this repository's overlays, so on
  # Darwin the checks patch nixpkgs' zellij and not the overlay's.
  perSystem = {inputs', ...}: let
    carried = combiningMarks inputs'.nixpkgs.legacyPackages;
  in {
    checks = {
      zellij-combining-marks = carried.applies;
      zellij-combining-marks-refuses-a-patched-tree = carried.refuses;
      zellij-combining-marks-refuses-a-stale-vendor = carried.refusesStaleVendor;
    };
  };
}
