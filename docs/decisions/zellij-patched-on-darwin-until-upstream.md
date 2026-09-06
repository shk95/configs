# zellij is patched on Darwin until upstream ships the combining-mark fix

date: 2026-09-05
scope: unixlike
status: accepted
issue: #175
issue: #176
reopen-when: zellij-org/zellij#5500 is merged, or is closed unmerged.

## The defect

zellij's `Grid::add_character` drops every code point of zero width. The
medial vowel and final consonant of a decomposed Hangul syllable are zero
width — letters that conjoin with the leading consonant, not marks, which is
what the first Darwin reading found on 2026-09-06 (§ Evidence) — so a
syllable written as U+1112 U+1161 U+11AB arrives at a pane as its leading
consonant alone and composed Korean disappears while it is typed. Upstream
has the defect as zellij-org/zellij#1538, and #3667 is the same defect seen
through decomposed Latin `é` on WSL; the tracker holds no Korean report, a
correction the PR's author made on 2026-09-06 after this record had cited
#3667 as one. It is not an IME, font or locale problem, and WezTerm's
`normalize_output_to_unicode_nfc` cannot reach it because the jamo are dropped
before WezTerm ever renders them.

The symptom is reported from WezTerm on macOS in #175, on 2026-09-05. The same
reproduction runs in a bare pty on Linux against the same pinned zellij
0.45.0, which is the evidence recorded here, because the grid is not
platform-specific:

| Where the bytes are read back | Bytes between `NFD:[` and `]` | Jamo that survive |
|---|---|---|
| a pty with no zellij in it | `e1 84 92 e1 85 a1 e1 86 ab` | U+1112 U+1161 U+11AB |
| a zellij 0.45.0 pane, unpatched | `e1 84 92` | U+1112 |

The reproduction, verbatim — the first command is the control and the second
reads back what the grid kept:

```sh
script -qc 'printf "NFD:[\341\204\222\341\205\241\341\206\253]\n"' /dev/null |
  tr -d '\r' | grep -a 'NFD:\[' | hexdump -C

zellij attach --create-background repro
zellij -s repro action new-pane -- \
  sh -c 'printf "NFD:[\341\204\222\341\205\241\341\206\253]\n"; sleep 60'
timeout 6 script -q /tmp/repro.ts zellij attach repro </dev/null >/dev/null
grep -a -o 'NFD:\[[^]]*\]' /tmp/repro.ts | grep -av '…' | head -1 | hexdump -C
```

The first line is GNU `script`; macOS `script` takes no `-c`, so on the Mac the
control is `script -q /dev/null sh -c 'printf "NFD:[\341\204\222\341\205\241\341\206\253]\n"'`
and the attach capture is written as shown; on Linux it is
`script -q -c 'zellij attach repro' /tmp/repro.ts`.

The reading is taken from the bytes zellij sends an attached client, not from
`zellij action dump-screen`. The Linux row above was read through
`dump-screen`, and that was corrected on 2026-09-06: the `dump_screen!` macro
in `grid.rs` pushes only each cell's base character, so a dump answers
`e1 84 92` from a grid that attached the jamo and from one that dropped them
alike, and on the Mac it showed Thai marks absent that the same pane's client
stream showed attached. For an unpatched grid the two readings agree, because
a dropped code point reaches neither, so the Linux observation stands. Since
the range pin of 2026-09-06 the branch's readback fix makes `dump-screen`
keep the marks too, and the two readings agree again; the client stream
remains the reference because it is what the terminal renders.

A grid that attaches the jamo makes the capture's bytes equal the control's,
`4e 46 44 3a 5b e1 84 92 e1 85 a1 e1 86 ab 5d`. The patched Darwin build of
2026-09-06 did not (§ Evidence).

## The measure

Upstream PR zellij-org/zellij#5500, "attach combining marks instead of
dropping them", was opened on 2026-08-20 and is unreviewed and unmerged. Its
first commit `8e02033f0bb8bdb53acf1484cb81605d0f3671dc` applied to the
v0.45.0 and v0.45.1 tags without rejects (#175, 2026-09-05) and was the pin
until 2026-09-06, when the branch gained the Hangul jamo ranges and a fix to
the readback paths (§ Evidence). The pin is now the branch's commit range,
`bf8d23a4…...cbb7b165…`, fetched as one patch from the compare URL with
`CHANGELOG.md` excluded: the later commits build on the first one's cells,
so the set is one unit, and the release notes are the one file in it that
does not apply to v0.45.1. `just zellij-patch-check` and the watcher read
the head of that range as the pin. `modules/zellij.nix`
carries that range as an overlay contributed to `nixpkgsOverlays`
(`docs/decisions/nixpkgs-overlays-declared-once.md`), and the measure is
registered as temporary in `provisional/unixlike/zellij-combining-marks.md`,
which names the condition that ends it.

The overlay is Darwin-only. The symptom is reported on the Mac, the Mac is the
host that has to carry a locally compiled zellij for it, and every Linux home
in this repository keeps the cached nixpkgs build: the overlay's body is
`lib.optionalAttrs prev.stdenv.hostPlatform.isDarwin`, so it yields `{}` on
Linux and every Linux toplevel derivation is byte-identical to the one before
it. Widening it to Linux would buy a fix nobody has asked for at the cost of
compiling zellij on every Linux host and, in CI, of a second platform whose
build could break the branch.

The patch is fetched with `fetchpatch` from the commit's own `.patch` URL
rather than vendored into `assets/`. `INV unixlike/payload-declared-and-parsed`
makes every source payload declare its format and be parsed by the tool that
consumes it, and the declaration and the tree agree in both directions; a
unified diff has no format in `assets/payloads.json` and no parser behind it,
so vendoring the patch would mean a new payload format and a new parser for a
file whose whole purpose is to be deleted. `fetchpatch` is a fixed-output
derivation, so nothing is fetched during evaluation and Linux CI can still
evaluate the Darwin configuration.

The patch adds the crate `unicode-properties` to `Cargo.lock`, so the vendored
dependency set changes with it. Pinned nixpkgs' `buildRustPackage` computes
`cargoDeps` at call time from `args.cargoHash`, which `overrideAttrs` cannot
reach; the overlay therefore overrides `cargoDeps` itself with
`rustPlatform.fetchCargoVendor`, which takes `src` and `patches` and
reproduces the same derivation name. The `zellij` wrapper takes
`zellij-unwrapped` as a function argument, so overriding the unwrapped package
is enough for the wrapper the home installs. Both hashes were discovered on
x86_64-linux and hold for aarch64-darwin because the unpatched `src` and
`cargoDeps` fixed-output hashes are identical on the two systems, which is the
direction that matters: the overlay only ever builds on Darwin.

The overlay pins `appliesTo` to the zellij version the patch was verified
against and `throw`s on any other version rather than warning or passing the
package through. A warning is the wrong shape here: an unpatched Darwin zellij
is indistinguishable from a patched one until someone types Korean into it, so
a signal that arrives at build time and is easy to scroll past is no signal.
Refusing to evaluate is the only report that arrives before the defect does,
and the cost of the refusal is bounded — it is one line to move, and the
procedure below says when.

## Bumping the pin

nixpkgs `nixos-unstable` already ships zellij 0.45.1 while `flake.lock` pins
0.45.0, so the first bump is expected at the next lock refresh; the watcher
`.github/workflows/zellij-upstream-5500.yml` (#176) reports it.
`INV repository/flake-lock-isolated` makes a lock refresh a commit of its own,
so the bump is two commits and their order is fixed:

1. `just zellij-patch-check v<ver>`. On a conflict, rebase the commit in a fork
   and repoint the overlay's `url` and `hash`.
2. Commit `chore(unixlike-deps): refresh flake.lock` with `flake.lock` alone
   (`tool/version-control/commit flake refresh`, without `--publish`). The
   Darwin configuration refuses to evaluate at this commit by design;
   `pre-commit` selects no evaluation for a lock-only change, so the refusal
   blocks nothing.
3. Commit `fix(unixlike): re-pin the zellij overlay to <ver>` with `appliesTo`,
   the `fetchpatch` hash if the commit was rebased, and the new `cargoDeps`
   hash.
4. `just darwin-build`, then the reproduction above against the built binary.
5. Push only after step 3; `pre-push` and CI evaluate the branch head. The
   helper's flags precede its command (`tool/version-control/commit --publish
   flake refresh`), and `--publish` would push straight after step 2, which is
   why it is not used there.

## Retiring the overlay

Once nixpkgs ships a zellij whose source already contains the merged fix:
commit `chore(unixlike-deps): refresh flake.lock` alone, then one commit that
deletes the overlay block, the workflow, the `CONTRIBUTING.md` subsection, the
`README.md` line, the `Justfile` recipe, the registry entry and all three of
`docs/status.md`'s mentions of the measure — the Unix-like paragraph, the
provisional registry count, and the tagged open condition — and adds a dated
line to this record and to the `docs/troubleshooting.md` entry. Only the open
condition carries the tag; the other two are current state, so they stop being
true at that same commit and go with it. `git grep zellij-combining-marks`
then finds only those two documents.

The refresh must come first, and the two commits must not be swapped or
merged, because of what happens when a patched source meets a fixed one. Three
mixing hazards decide it:

- Where upstream merged the PR's hunks unchanged, `patch` refuses them as
  already applied and the build fails at the patch phase.
- Where upstream merged them changed — a rebase, a review edit, a
  follow-up — the hunks either fail to apply or apply into code that no longer
  compiles.
- The PR carries its own grid tests. They do not run inside the build: pinned
  nixpkgs' `buildRustPackage` runs `cargo test` in the root crate alone (the
  Darwin log of 2026-09-06 shows 15 `tests::cli` cases and the ignored e2e
  cases, nothing from `zellij-server`), so a semantic mismatch that still
  compiles is caught only by the reproduction above on the Mac, which is why
  CONTRIBUTING § zellij overlay makes that reproduction part of every bump.

The first two are build failures rather than silent breakage, which is why the
`appliesTo` `throw` is the guard that matters: it stops the evaluation before
either of them costs a compile.

## Rejected alternatives

- `rustPlatform.importCargoLock` with a vendored `Cargo.lock`. It works, but it
  puts a second copy of zellij's lock file in this repository, to be kept in
  step with both nixpkgs and the PR by hand; `fetchCargoVendor` derives the
  same set from the patched source and needs one hash instead.
- A shell-level `iconv` or NFC-normalising pipe around zellij. It would have to
  sit between the pane's program and zellij for every pane and every program,
  it normalises output that was correct as well as output that was not, and it
  does not fix the grid — the next zero-width code point that is not a jamo is
  dropped just the same.
- Waiting for upstream with no local measure. The PR was unreviewed 16 days
  after it was opened and there is no released version to wait for; waiting is
  what the registry entry's `review-by` date makes an explicit decision rather
  than a default.

## Evidence

Evaluation, the two fixed-output hashes and the Linux row of the reproduction
above are from an x86_64-linux host, 2026-09-05.

2026-09-06, aarch64-darwin, #178. Build: `just darwin-build` on the Mac
completed with both fixed-output hashes as pinned — no `hash mismatch` at
`zellij-unwrapped-0.45.0-vendor-staging`, which is the platform-independence
claim under § The measure holding — and `just zellij-patch-check v0.45.1`
exited 0. The build's `checkPhase` ran 15 tests, all in the root crate, none
from `grid_tests.rs` (§ Retiring the overlay). Activation: generation 34 at
14:33; `/run/current-system` and the zellij server that the restarted WezTerm
started both run `zellij-unwrapped-0.45.0` from the patched derivation.
Native runtime: the reproduction, read from the client stream, answered
`4e 46 44 3a 5b e1 84 92 5d` for the NFD syllable, and `ls` of a directory
named with the same three jamo showed the leading consonant alone; the control
answered `4e 46 44 3a 5b e1 84 92 e1 85 a1 e1 86 ab 5d`. Thai `กั`
(U+0E01 U+0E31) printed in the same pane came back as `e0 b8 81 e0 b8 b1`, so
the patch attaches marks; it does not attach Hangul jamo.

The cause is in the patch, not the build. Its `is_combining_mark` accepts
Unicode general category Mark (Mn, Mc, Me) only. The medial vowels and final
consonants of a decomposed syllable — U+1160–U+11FF, with the extensions
U+D7B0–U+D7C6 and U+D7CB–U+D7FB — are general category Lo, letters that
`unicode-width` gives zero width because they conjoin with the leading
consonant before them, so `Grid::add_character` still drops them on the
zero-width path exactly as before the patch. The patch's own tests cover Latin
marks, Thai, the variation selector and a wide base character; none covers
Hangul, which was the symptom that motivated the measure. The measure
therefore stands and has not delivered its outcome on the host: the pinned
commit needs those jamo ranges accepted beside category Mark and a Hangul grid
test, first as an addition carried by the overlay and then proposed on
zellij-org/zellij#5500. Seen at the same time and not fixed by the PR as
pinned: `dump_screen!`, selection and `serialize` in `grid.rs` push only the
base character, so text read back out of a patched zellij loses the marks the
screen now keeps.

Later on 2026-09-06, aarch64-darwin, #178. The overlay gained a `postPatch`
that accepts the Hangul jamo ranges beside category Mark and appends a Hangul
grid test, and `cargoTestFlags` and `checkFlags` that point the build's check
at `zellij-server`'s combining-mark tests. `just darwin-build` completed with
the `cargoDeps` hash unchanged, and the check ran five tests — the PR's four
and the Hangul one — all passing, the first grid tests to run inside this
build. Against the built binary before activation, and again through the
installed one in a session created after generation 35 at 15:18, the
reproduction answered `4e 46 44 3a 5b e1 84 92 e1 85 a1 e1 86 ab 5d`, equal
to the control; `ls` of the jamo-named directory came back
`6e 66 64 2d e1 84 92 e1 85 a1 e1 86 ab`; Thai `กั` stayed
`e0 b8 81 e0 b8 b1`. A zellij server started before the switch keeps serving
the previous binary until its session ends, which is why the reading was
taken in a new session. The measure delivers its outcome on the host from
generation 35. The addition was carried by the overlay until
zellij-org/zellij#5500 included it, which happened the same day.

Later still on 2026-09-06, aarch64-darwin. The PR's author folded the Hangul
commit into the branch as `f9805a15` (with this repository's maintainer as
author), corrected the #3667 citation, and fixed the readback paths in
`c4d16579`; the branch head became `cbb7b165`. The overlay was re-pinned to
the commit range `bf8d23a4…...cbb7b165…` with `CHANGELOG.md` excluded and
the `postPatch` deleted; `just zellij-patch-check` passed against v0.45.0 and
v0.45.1 with the range. `just darwin-build` completed with the `cargoDeps`
hash unchanged, and the check ran nine tests — the PR's four, the Hangul one
and the four readback ones — all passing. Against the built binary, before
activation: the client stream answered `4e 46 44 3a 5b e1 84 92 e1 85 a1 e1
86 ab 5d`, and so did `dump-screen` for the first time; Thai
`e0 b8 81 e0 b8 b1` on both readings; the jamo-named directory listed whole.
Activated as generation 36 at 19:37 on the maintainer's request; in a session
created after the switch, served by the installed binary, both readings
answered the same bytes again, and `just karabiner-check` still exited 0
with the Karabiner file untouched.
