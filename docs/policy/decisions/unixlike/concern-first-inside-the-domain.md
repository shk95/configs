# Inside the Unix-like domain the concern is the directory and the class is the file

date: 2026-09-12
scope: unixlike
status: accepted
reopen-when: most feature files write into exactly one platform class and no concern spans two, so that a class has become the larger grouping.
source: 959db15:docs/design/unixlike-restructure-study.md § Why the Unix-like domain's shape costs what it does

Once the domain has a tree (`docs/policy/decisions/unixlike/unixlike-domain-owns-its-tree.md`)
the question is what its first level says. Two orderings were on the table
(`docs/work/repository/unixlike-restructure-study/study.md`, which also weighs the third
reading, concerns at the repository root): by class, `{darwin, nixos, hm}`
or one directory per fragment, and by concern, one directory per feature.
The tree already answers, in its file
names: of 42 feature files, eight are `darwin-*` and six `wsl*`, each named
for a concern first and a platform second, and every one writes fragments
into `config.modules.<class>.<name>`, where the class is a value in the file
rather than a place in the tree
(`docs/policy/decisions/unixlike/home-manager-platform-classes.md`).

The module tree keeps one root, `unixlike/modules/`. Its first level groups
concerns for navigation as `flake`, `machines`, `platforms`, `foundation`,
`desktop`, and `programs`; the concern is the file or directory inside a
group. The class a fragment reaches is read in the file that writes it and
never from a directory. A concern that is one fragment stays one file, such
as `modules/programs/bat.nix`; a directory is for a concern with more than
one fragment or with material beside its module.
What a concern owns sits beside its module: the payload the module
delivers and the script it interpolates. Karabiner's earlier three-directory
join under `modules/`, `assets/` and `tool/darwin/` became one concern
directory. Composition keeps a directory of its own, `modules/flake/`,
which `tool/checks/composition` already exempts as the composition file's
home.

The root is fixed here rather than left to the move because three
mechanisms already assume a `modules/` beside the flake: `flake.nix`
hands `import-tree ./modules` a directory and receives every `.nix` file
under it, `tool/checks/composition` scans every `.nix` file under the
directory it is given, and `tool/checks/import-order` gathers
`<flake>/modules` by name. Concern directories directly beside `flake.nix`
would put the flake file itself, and the check fixtures that deliberately
break the rules, inside all three walks, and each would need a filter to
keep them out; one segment keeps them out by construction. For the same
reason a check that reads fixtures lives under the domain's checks
directory, outside the module tree, rather than beside the module it
proves.

Measured on 2026-09-12 against the current tree:

- `homeManager.shared` is written by 20 of the 42 feature files. A
  class-first tree cannot hold its largest group, because "shared" is not
  a platform.
- `homeManager` is an evaluator, not a flavour. Its classes are composed by
  the Darwin flavour and by both WSL flavours, so `hm` is not exclusive
  with `darwin` or `nixos`, and `homeManager.wsl` belongs to two flavours
  at once.
- Five files write into two classes: `darwin-host.nix` (`darwin.system`
  and `homeManager.darwin`), `ghostty.nix`, `git.nix`, `nix-conf.nix`
  (`homeManager.wslStandalone` and `nixos.wsl`) and `state-version.nix`.
  One feature across every class that needs it is the pattern the domain
  follows; a class-first tree splits those five.
- A class in a directory name says twice what the fragment already says,
  and only the fragment is checked. `tool/checks/composition` reads the
  file body and never the path, so a `darwin/` directory holding a
  `homeManager.shared` fragment passes, and the tree would tell a reader
  something no evaluator enforces.

Rejected:

- `{darwin, nixos, hm}` at the first level. Above.
- Eight directories, one per class. The same defect with more of it, and
  the five two-class files have no home.
- Concern directories at the repository root, the literal reading of
  "flatten". It puts the Unix-like and Windows copies of zellij, WezTerm
  and PowerShell side by side. They are deliberate copies
  (`docs/policy/decisions/repository/powershell-copied-per-domain.md`), and part of what
  keeps them safely apart is distance; the scope segment comes first.

What it costs. The original decision established the concern-first domain
tree; the 2026-09-24 grouping changed its first-level placement without
changing composition. `import-tree` walks recursively and the class merge is
keyed by defining file (`INV unixlike/import-order-independence`), so depth
changes no derivation; a concern directory must not begin with `_`, which
`import-tree` skips, and a payload or script beside a module is ignored by
the walk because only `.nix` files are collected. The class merge uses the
pre-grouping concern path as its stable sort key so the seven existing host
derivations do not change when physical paths change. `packages.nix`, the
shared package list, is a one-file concern and stays one. The `_file`
attribution `modules.<class>.<name>` stays as it is. The Windows domain
groups the same way by declaration, in `windows/desired/manifest.json`, and
stays as it is: two local implementations, not one abstraction
(`AGENTS.md § Domain boundaries`).
