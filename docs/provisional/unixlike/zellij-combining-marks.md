id: unixlike/zellij-combining-marks
kind: upstream-pending
statement: Darwin builds zellij with upstream PR zellij-org/zellij#5500 applied with no fuzz through a nixpkgs overlay, at whatever zellij version flake.lock brings in, so combining marks are attached to the cell before them instead of being dropped; every system's flake checks refuse a lock whose zellij the patch no longer applies to.
since: 2026-09-05
exit-when: A nixpkgs zellij whose source already contains the merged fix reaches flake.lock.
watch: .github/workflows/zellij-upstream-5500.yml
review-by: 2026-12-04
issue: #175
decision: docs/policy/decisions/unixlike/zellij-patched-on-darwin-until-upstream.md § zellij is patched on Darwin until upstream ships the combining-mark fix
owner: repository maintainer

The overlay replaces nothing: without it Darwin's zellij is the cached nixpkgs
build, which drops the conjoining jamo of a decomposed Hangul syllable, so
composed Korean vanishes as it is typed. It costs a locally compiled zellij on
the Mac and one `fetchpatch` hash to keep current. The one crate the patch adds
is fetched by the checksum the patch's own `Cargo.lock` hunk carries, and the
rest of the vendored set is nixpkgs' own for the lock's zellij, so a
`flake.lock` refresh that moves zellij needs no second commit. What it needs
instead is the flake checks `zellij-combining-marks`,
`zellij-combining-marks-refuses-a-patched-tree` and
`zellij-combining-marks-refuses-a-stale-vendor` passing, which
`unixlike/tool/checks/test` builds on every system; when the first fails, the
range is rebased in a fork before the refresh can merge. The Linux homes are
unaffected: the overlay yields `{}` there, and the checks build sources, not a
Linux zellij.

Every disposable line carries `PROV unixlike/zellij-combining-marks`. The set
is the overlay block in `unixlike/modules/zellij/module.nix` — the shared
builder, the overlay and the three flake checks — the watcher
`.github/workflows/zellij-upstream-5500.yml`, the `zellij-patch-check` recipe
in the `Justfile`, the "zellij overlay" subsection in `CONTRIBUTING.md`, the
open condition in `docs/status/unixlike.md`, and this entry. `README.md` lists the
recipe without a `PROV` tag because the line is one item in a list.

Retirement is two commits and their order is fixed by
`INV repository/flake-lock-isolated`: `chore(unixlike-deps): refresh
flake.lock` alone, then one commit that deletes the whole set above, the
`README.md` line, and all three status mentions of the
measure — the Unix-like paragraph and the tagged open condition in
`docs/status/unixlike.md`, and the provisional registry count in
`docs/status/repository.md` — and adds a dated line to
`docs/policy/decisions/unixlike/zellij-patched-on-darwin-until-upstream.md` and to the
`docs/reference/troubleshooting.md` entry, which both outlive the patch. Only the open
condition carries the tag; the other two are current state, so they stop being
true at that same commit and go with it. `git grep zellij-combining-marks`
then finds only those two documents. The decision record carries the same
order and the reason a patched source must never meet a fixed one. The
refresh commit is the one exception to the checks above: against a source
that already carries the fix, `zellij-combining-marks` fails by design, so
that refresh is pushed together with the retirement commit, never alone.

On review, rerun the evidence rather than reading it: `just
zellij-patch-check` for whether the range still applies to the lock's zellij,
the three flavours' toplevel derivation paths for whether anything but Darwin
moved, and the reproduction in the decision record against the built Darwin
binary. The Darwin build and its reproduction were observed on 2026-09-06
(#178): generation 35 renders a decomposed syllable whole. The Hangul jamo
ranges that generation carried as a local addition are on the pull request's
branch since the same day, and the overlay pins the branch's commit range.
