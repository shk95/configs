# The Windows entry point is one script inside the domain

date: 2026-09-05
scope: windows
status: accepted
issue: #168
reopen-when: a caller outside the Windows domain needs a Windows verb without a path into windows/

The Unix-like domain has one entry point, the `Justfile`, whose verbs name
what a person does: `home-build`, `home-switch`. The Windows domain had five
scripts a person would run, in two directories, each with its own argument
convention, and one more nobody had documented. It read as a collection of
scripts rather than a tool.

`windows/win-env.ps1` is now the domain's entry point. Each verb runs
exactly one script under `windows/tools/` and returns that script's exit
status unchanged; the verb table is the whole policy the file holds
(`INV windows/entry-point-forwards-status`). With it, `bootstrap.ps1` and
`setup.ps1` moved from the domain root into `windows/tools/`, so the root
holds the entry point, the directories and `toolchain.json`; older records
name the two scripts at the root, which is where they were when those
records were written.

The target runs in the entry point's own process, so the status handed back
is what the script exits with, and a script that falls off its end leaves
that at whatever its last native call set. Every script the table names
therefore ends in an explicit `exit`, which the same fixture holds. No
target leaked when the rule was written; the fixture is what keeps a later
native call near the end of one from changing that. A command the script
refuses to bind ends the run at 1, by the entry point's own error preference
rather than by anything the script does.

Rejected:

- Recipes in the `Justfile`. `just` is the Nix development shell's tool and
  is not on a Windows host, and the Unix-like entry point calling Windows
  deployment is the implicit cross-domain dependency `AGENTS.md` forbids.
- A function in the managed PowerShell profile. It exists only after Apply,
  so it cannot bootstrap a host, and the profile is one marked block in a
  file other owners write. It may still be added on top of the entry point.
- The file at the repository root. The classifier would need an arm for it
  (a `repository` change landing first), and the Windows parse gate, the
  tree-isolation fixture and the domain-reads scan all read `windows/` only,
  so the file would belong to a domain whose gates never see it. It would
  save one directory in the typed path.

The usage status is 64 (`EX_USAGE`) rather than 2 or 69: 2 is drift and 69
is `EX_UNAVAILABLE`, both check outcomes a caller acts on, and "no such verb"
must never be read as either.
