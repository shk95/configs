# Invariant registry

One file per invariant. An invariant is a statement about committed desired
state or repository tooling that must remain true; this directory is the
authority for what those statements are, and each entry declares how it is
enforced. `docs/architecture.md`, "Invariant registry", records why the
registry exists and how it relates to the other documents.

`tool/version-control/invariants` checks every entry and, in the other
direction, every `INV <scope>/<slug>` tag in the tree. It runs on every commit
and in CI. It reads the index, like the hygiene scan, so stage a new entry
before running it by hand. `tool/version-control/invariants --table` prints
the registry as a table; it still reports any failure on stderr but exits 0
either way.

## Layout

```text
invariants/
  README.md          this contract (repository scope)
  repository/*.md    version-control policy, hooks, CI, hygiene
  unixlike/*.md      Nix, Home Manager, NixOS, nix-darwin, Unix-like payloads
  windows/*.md       manifest, payloads, PowerShell reconciliation
  common/            empty until a common component exists
```

Each scope owns the entries under its directory. A Windows entry is a
`windows` change and can be written and checked without a Unix-like host.

## Entry format

```text
id: <scope>/<slug>
statement: <one sentence: what must remain true, naming no command, product or model>
rationale: <AGENTS.md | docs/architecture.md> § <heading>
enforced-by: <kind> <locator>
enforced-by: <kind> <locator>
owner: <who decides, required for manual and pending>
decision: <path> § <heading>

<free prose: why, exceptions, history>
```

The header is every line up to the first blank line, each `key: value`.
Keys are lowercase; a value runs to the end of its line; a list is a
repeated key. No other syntax is parsed.

| Key | Count | Meaning |
|---|---|---|
| `id` | 1 | Must equal `<scope>/<slug>` of the path. `<slug>` is lowercase words joined by single hyphens. |
| `statement` | 1 | The rule, tool-independent. Reviewers hold it to that; the checker does not. |
| `rationale` | 1 | Where layer 2 justifies it. Only `AGENTS.md` or `docs/architecture.md`; the heading must exist. |
| `enforced-by` | 1+ | How it is kept. See kinds. |
| `owner` | 0–1 | Required for `manual` and `pending`. |
| `decision` | 0+ | A decision record the entry rests on; the heading must exist. |

## Kinds of enforcement

| Kind | Locator | The checker requires |
|---|---|---|
| `schema` | a tracked file whose evaluator or loader refuses the violation | the file contains `INV <id>` |
| `tool` | a tracked executable that exits non-zero on the violation | index mode `100755`; the file contains `INV <id>` |
| `fixture` | a tracked test file with a positive and a negative case | the file contains `INV <id>` |
| `manual` | the evidence item a reviewer produces, in words | `docs/definition-of-done.md` contains `INV <id>`; `owner` |
| `pending` | `#<issue>` | the only `enforced-by` on the entry; `owner` |

A `schema` or `tool` entry must also declare a `fixture`: an enforcement with
no fixture is a convention written as a control. A `pending` entry is a
declared gap, reported in the checker's summary and never failed; the issue
is its enforcement owner until a check exists.

## Naming an invariant from code, tests and documents

Write the literal `INV <scope>/<slug>`:

- Pester: `It 'INV windows/<slug>: refuses …' { … }`
- shell fixtures: a comment `# INV <scope>/<slug>` above the case
- loader and evaluator messages: `throw "INV <scope>/<slug>: …"`
- Nix and shell headers: `# INV <scope>/<slug>` in the header comment
- documents: `INV <scope>/<slug>` in running text

The checker verifies that a declared locator contains the tag and that every
tag in the tree is registered. Whether a tagged case genuinely exercises the
statement is the reviewer's to confirm; `docs/definition-of-done.md` says so.

## Example

`invariants/repository/registry-coverage.md` is the registry's own entry and
the shape to copy: `INV repository/registry-coverage` is named by the checker
that enforces it and by the fixture group that proves it.

## Adding or changing an entry

`CONTRIBUTING.md`, "Add or change an invariant".
