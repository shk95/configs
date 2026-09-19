# Documents

Everything this repository writes about itself, other than the three root
files (`AGENTS.md`, `CONTRIBUTING.md`, `README.md`). Each area's `README.md`
is its format contract.

```
docs/
  policy/                        what binds: observe → adopt → enforce
    architecture.md              the model and every rationale
    definition-of-done/<scope>.md  the evidence a change owes
    candidates/<scope>/          observed rules and deletions; no authority
    decisions/<scope>/           adopted choices and why
    invariants/<scope>/          what must remain true, and what enforces it
  provisional/<scope>/           temporary measures that must become false
  work/<scope>/<slug>/           arguments and plans for a direction
  status/<scope>.md              what is true today
  reference/                     recurring symptoms and their causes
```

Ownership. A scope directory, or a file named for a scope, owns what it
holds: `docs/policy/decisions/unixlike/…` and `docs/status/windows.md` are
changes of that domain. A scope position that names no domain is refused; any
other file here is `repository`'s
(`docs/policy/decisions/repository/documents-classified-by-scope.md`).

Indexes are printed, not kept: `tool/version-control/invariants --table`,
`tool/version-control/provisional --table`, and
`tool/version-control/records --table decisions|candidates|work`.
