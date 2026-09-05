# zellij is patched on Darwin until upstream ships the combining-mark fix

date: 2026-09-05
scope: unixlike
status: accepted
issue: #175
issue: #176
reopen-when: zellij-org/zellij#5500 is merged, or is closed unmerged.

## The defect

zellij's `Grid::add_character` drops every code point of zero width. The
conjoining jamo of a decomposed Hangul syllable are zero-width combining
marks, so a syllable written as U+1112 U+1161 U+11AB arrives at a pane as its
leading consonant alone and composed Korean disappears while it is typed.
Upstream has the defect twice over as zellij-org/zellij#3667 and #1538. It is
not an IME, font or locale problem, and WezTerm's
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

zellij -s repro action new-pane -- \
  sh -c 'printf "NFD:[\341\204\222\341\205\241\341\206\253]\n"; sleep 60'
zellij -s repro action dump-screen | grep -a 'NFD:\[' | head -1 | hexdump -C
```

A patched zellij should make the second command's output equal the first's,
`4e 46 44 3a 5b e1 84 92 e1 85 a1 e1 86 ab 5d`. That half is a prediction, not
an observation: no patched zellij has been built on either host yet, and #178
records the reading once the Darwin build exists.

## The measure

Upstream PR zellij-org/zellij#5500, "attach combining marks instead of
dropping them", was opened on 2026-08-20 and is unreviewed and unmerged. Its
code commit `8e02033f0bb8bdb53acf1484cb81605d0f3671dc` applies to the v0.45.0
and v0.45.1 tags without rejects (#175, 2026-09-05). `modules/zellij.nix`
carries that commit as an overlay contributed to `nixpkgsOverlays`
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
x86_64-linux and are sound there because the unpatched `src` and `cargoDeps`
fixed-output hashes are identical on x86_64-linux and aarch64-darwin.

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
`README.md` line, the `Justfile` recipe, the registry entry and the
`docs/status.md` open condition, and adds a dated line to this record and to
the `docs/troubleshooting.md` entry. `git grep zellij-combining-marks` then
finds only those two documents.

The refresh must come first, and the two commits must not be swapped or
merged, because of what happens when a patched source meets a fixed one. Three
mixing hazards decide it:

- Where upstream merged the PR's hunks unchanged, `patch` refuses them as
  already applied and the build fails at the patch phase.
- Where upstream merged them changed — a rebase, a review edit, a
  follow-up — the hunks either fail to apply or apply into code that no longer
  compiles.
- The PR carries its own grid tests, which run inside the build's `cargo test`,
  so a semantic mismatch that still compiles is caught there rather than on a
  Mac at runtime.

All three are build failures rather than silent breakage, which is why the
`appliesTo` `throw` is the guard that matters: it stops the evaluation before
any of them costs a compile.

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

Evaluation, the two fixed-output hashes and the reproduction above are from an
x86_64-linux host. The Darwin build (`just darwin-build`), the reproduction
against the built Darwin binary and the in-WezTerm observation on macOS are
owed to #178; no Mac evidence is claimed here. Activation is not performed.
