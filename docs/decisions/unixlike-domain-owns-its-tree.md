# The Unix-like domain owns its tree

date: 2026-09-12
scope: unixlike
status: accepted
reopen-when: a path the classifier answers `unixlike` for must sit outside `unixlike/` for a reason other than a tool outside the repository reading it at the root.
source: 959db15:docs/design/unixlike-restructure-study.md § Why the Unix-like domain's shape costs what it does

The Windows domain has lived under `windows/` since the monorepo began: one
path, one classifier arm, and every Windows gate reads that tree and nothing
else. The Unix-like domain is the flake's, and the flake grew at the
repository root, so what the domain owns is spread over `flake.nix`,
`flake.lock`, `modules/`, `assets/`, `tool/checks/`, `tool/darwin/`,
`.envrc` and the `Justfile`. `tool/version-control/classify` names those
eight patterns where `windows/` needs one, and `tool/dispatch/select` and
`tool/version-control/domain-reads` each repeat the list, so a new Unix-like
location is edited into three tools, then CI and the documents that describe
them (`docs/candidates/domain-tool-placement-and-justfile-exception.md`
holds the occurrences). The boundary is right; its physical form lags it,
and the enforcement plane pays the difference on every new location.

The Unix-like domain owns one tree, `unixlike/`, and every path the
classifier answers `unixlike` for lives under it unless a tool outside the
repository reads that path at the root. That includes `tool/darwin/`:
`modules/karabiner.nix` interpolates `${../tool/darwin/karabiner}` into a
Home Manager activation, so the script is domain material that runs on the
host, and an executable the domain owns belongs in the domain's tree, as
`windows/tools/` holds the Windows scripts
(`docs/decisions/windows-entry-point-in-domain.md`). It includes
`tool/checks/` on the same ground, with the fixtures those checks read:
the checks evaluate the flake and are classified `unixlike` today, and a
rule that left them out would keep, as its one exception, the directory
`docs/candidates/domain-tool-placement-and-justfile-exception.md` was
opened to question. `tool/` then holds repository tooling and nothing else,
which is what the classifier's `repository` arm already says of everything
under it except those two directories. The exceptions the
rule allows are `.envrc`, which direnv reads at the root, and the
`Justfile`, whose place is a separate decision; both keep their arms until
it is made.

Moving the tree changes no derivation. A spike on 2026-09-10, in a worktree
restored afterwards, found the three toplevel derivation paths
byte-identical to the baseline in every layout that evaluated, because a
path literal is content-addressed and the layout never reaches the
derivation; `docs/design/unixlike-restructure-study.md` holds the spike, the
layouts it rejected and the caveat on comparing the numbers across clones.
The source root the flake copies shrinks from the repository, 2.3M, to the
domain, 340K, and `path:./unixlike` becomes a valid flakeref; both are side
effects, not the reason.

Rejected:

- Layout A, the flake in the subdirectory and `modules/` left at the root.
  It evaluates, but `flake.nix` and `tool/checks/import-order` both gather
  `<flake>/modules`, so the check fails, `path:./unixlike` is impossible,
  and the classifier loses nothing.
- A `src/` wrapper, `src/unixlike/` beside `src/windows/`. Every path
  reference in the tree changes and the segment tells a reader nothing; the
  classifier gains a prefix instead of losing arms.
- Layout B, `tool/darwin/` left in `tool/`. The Karabiner reference becomes
  `../../tool/darwin/karabiner`, which escapes the domain, so the flake must
  be spelled `path:.?dir=unixlike` and copies the whole repository. The
  rebuild cost first attributed to that copy was withdrawn the same day:
  eleven unrelated commits left the Darwin toplevel unchanged. What B costs
  is copy time and the flakeref; what decides against it is ownership. A
  script the domain runs on a host is not repository tooling.
- Leaving the tree as it is. Three edits per new location, without end.

What it costs. Nothing moves in this change. The move is a later change
and is three single-scope commits rather than one, because the classifier
answers `unclassified` for a moved path and the hooks refuse that
(`INV repository/scope-ownership`): first the three tools accept both trees
(`repository`, registered under `provisional/` with `PROV` tags because the
tolerance must become false), then the tree moves (`unixlike`), then the
old arms go (`repository`), the last only after the move has reached `dev`,
because a path nothing classifies cannot be pushed and that includes its
own removal (`docs/architecture.md § Common domain`). Until the move,
`docs/architecture.md § Unix-like domain` and `AGENTS.md § Goal and
authority` name `modules/` and stay true; the migrating change rewrites
them. The `Justfile`'s fourteen `path:.` flakerefs, the default paths in
the checks, and `.envrc` change with the move, and `.envrc` must say
`use flake ./unixlike` rather than the `path:` form, which nix-direnv
accepts while silently ceasing to watch the flake files. Every caller of
the checks is edited once: the `Justfile`, the CI workflow, the two hooks,
`tool/dispatch/select`, and the `enforced-by` line of each Unix-like
invariant that names a check, which `tool/version-control/invariants`
refuses when the locator is not a tracked executable, so the invariant
entries move in the same commit as the checks. `flake.lock` moves
with the flake, and `nix flake update` given the subdirectory writes it
there and creates none at the root, measured on a fixture. The milestone
rule splits the move into a `repository` milestone and a `unixlike` one,
linked, neither with a visible result alone.
