id: unixlike/zellij-combining-marks
kind: upstream-pending
statement: Darwin builds zellij with upstream PR zellij-org/zellij#5500 applied through a nixpkgs overlay, so combining marks are attached to the cell before them instead of being dropped.
since: 2026-09-05
exit-when: A nixpkgs zellij whose source already contains the merged fix reaches flake.lock.
watch: .github/workflows/zellij-upstream-5500.yml
review-by: 2026-12-04
issue: #175
decision: docs/decisions/zellij-patched-on-darwin-until-upstream.md § zellij is patched on Darwin until upstream ships the combining-mark fix
owner: repository maintainer

The overlay replaces nothing: without it Darwin's zellij is the cached nixpkgs
build, which drops the conjoining jamo of a decomposed Hangul syllable, so
composed Korean vanishes as it is typed. It costs a locally compiled zellij on
the Mac, one `fetchpatch` and one `fetchCargoVendor` hash to keep current, and
a Darwin evaluation that refuses outright whenever `flake.lock` moves zellij
off the pinned version. The Linux homes are unaffected: the overlay yields
`{}` there.

Every disposable line carries `PROV unixlike/zellij-combining-marks`. The set
is the overlay block in `modules/zellij.nix`, the watcher
`.github/workflows/zellij-upstream-5500.yml`, the `zellij-patch-check` recipe
in the `Justfile`, the "zellij overlay" subsection in `CONTRIBUTING.md`, the
open condition in `docs/status.md`, and this entry. `README.md` lists the
recipe without a tag because the line is one item in a list.

Retirement is two commits and their order is fixed by
`INV repository/flake-lock-isolated`: `chore(unixlike-deps): refresh
flake.lock` alone, then one commit that deletes the whole set above, the
`README.md` line, and all three of `docs/status.md`'s mentions of the
measure — the Unix-like paragraph, the provisional registry count, and the
tagged open condition — and adds a dated line to
`docs/decisions/zellij-patched-on-darwin-until-upstream.md` and to the
`docs/troubleshooting.md` entry, which both outlive the patch. Only the open
condition carries the tag; the other two are current state, so they stop being
true at that same commit and go with it. `git grep zellij-combining-marks`
then finds only those two documents. The decision record carries the same
order and the reason a patched source must never meet a fixed one.

On review, rerun the evidence rather than reading it: `just zellij-patch-check
v<the lock's zellij version>` for whether the commit still applies, the three
flavours' toplevel derivation paths for whether anything but Darwin moved, and
the reproduction in the decision record against the built Darwin binary. The
Darwin build and its reproduction were observed on 2026-09-06 (#178):
generation 35 renders a decomposed syllable whole. The Hangul jamo ranges
that generation carried as a local addition are on the pull request's branch
since the same day, and the overlay pins the branch's commit range.
