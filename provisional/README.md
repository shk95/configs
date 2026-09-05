# Provisional registry

One file per temporary measure. A provisional measure is an experiment, a
workaround, or a patch the repository carries until upstream ships a fix;
this directory is the authority for which such measures exist, and each entry
declares the condition that ends it. `docs/architecture.md`, "Provisional
registry", records why the registry exists and how it relates to the other
documents.

This registry is the sibling of `invariants/`. That one records what must
remain true; this one records what must eventually become false. Without it a
temporary measure becomes permanent by neglect.

`tool/version-control/provisional` checks every entry and, in the other
direction, every `PROV <scope>/<slug>` tag in the tree. A failure names its
rule as `P1` to `P8`; the checker's header defines each. It runs on every
commit and in CI. It reads the index, like the hygiene scan, so stage a new
entry before running it by hand. `tool/version-control/provisional --table`
prints the registry as a table. An absent registry is zero entries and
passes: this directory exists to be emptied.

## Layout

```text
provisional/
  README.md          this contract (repository scope)
  repository/*.md    version-control policy, hooks, CI, hygiene
  unixlike/*.md      Nix, Home Manager, NixOS, nix-darwin, Unix-like payloads
  windows/*.md       manifest, payloads, PowerShell reconciliation
```

A scope directory exists only while that scope holds a measure; the entry
that needs it creates it and its retirement removes it again.

Each scope owns the entries under its directory. A Windows entry is a
`windows` change and can be written and checked without a Unix-like host.

## Entry format

```text
id: <scope>/<slug>
kind: experiment | workaround | upstream-pending
statement: <one sentence: what the measure is, naming no command output or model>
since: <YYYY-MM-DD the measure entered the tree>
exit-when: <one sentence: the condition that ends it>
watch: <a tracked path whose change is the signal, or `manual`>
review-by: <YYYY-MM-DD>
issue: #<n>
decision: <path> § <heading>
owner: <who decides>

<free prose: what it replaces, what it costs, what to check on review>

reviewed: <YYYY-MM-DD> <why the horizon moved>
```

The header is every line up to the first blank line, each `key: value`.
Keys are lowercase; a value runs to the end of its line. No other syntax is
parsed. A `reviewed:` line lives in the prose, one per extension.

| Key | Count | Meaning |
|---|---|---|
| `id` | 1 | Must equal `<scope>/<slug>` of the path. `<slug>` is lowercase words joined by single hyphens. |
| `kind` | 1 | `experiment` (kept while it is being judged), `workaround` (kept while the defect stands), or `upstream-pending` (kept until an upstream change lands). |
| `statement` | 1 | What the measure is, in one sentence. Reviewers hold it to that; the checker does not. |
| `since` | 1 | `YYYY-MM-DD` the measure entered the tree. |
| `exit-when` | 1 | The condition that ends the measure, in one sentence. It must be observable by someone other than its author. |
| `watch` | 0–1 | A tracked path whose change is the signal, or `manual` when only a person can tell. |
| `review-by` | 1 | `YYYY-MM-DD`, after `since` and at most 180 days after the later of `since` and the last `reviewed:` date. |
| `issue` | 1 | `#<n>`, where the measure and its exit are tracked. |
| `decision` | 1 | The decision record that accepted the measure, `<path> § <heading>`; the heading must exist. |
| `owner` | 1 | Who decides whether it is retired, extended or promoted. |

## Naming a measure from code, tests and documents

Every disposable line carries the literal `PROV <scope>/<slug>`, so deleting
the entry and deleting the measure are one change rather than two:

- Nix and shell headers: `# PROV <scope>/<slug>` above the block
- PowerShell: `# PROV <scope>/<slug>` above the block
- documents: `PROV <scope>/<slug>` in running text

The checker verifies both directions: an entry no tracked file outside this
directory names is a registration with no measure (`P6`), and a tag naming no
entry is a measure with no registration (`P7`). Whether a tagged line is
genuinely the whole measure is the reviewer's to confirm.

A document that mentions the tag writes the placeholder `PROV <scope>/<slug>`
rather than a literal id, so retiring an entry orphans no prose and the tag
scanner reads no explanation as a measure.

## Retirement, extension and promotion

| Outcome | What it means | What changes |
|---|---|---|
| Retirement | `exit-when` came true and the measure is no longer needed. | Delete the entry, the tagged lines, and the scope directory if it is now empty — all in one commit. |
| Extension | `exit-when` has not come true and the measure is still the best option. | Move `review-by` forward by at most 180 days and add a `reviewed:` line saying why. |
| Promotion | The measure turned out to be the answer and is no longer temporary. | Write a decision record, delete the entry and the tags, and keep the code. |

Retirement and promotion both empty the registry entry; the difference is
what survives in the tree. Extension is not free: the `reviewed:` lines are
the record of how long a measure has been about to end.

## Overdue entries

An entry whose `review-by` has passed is overdue. The checker fails an
overdue entry only for a commit or a pull request that touches its own scope,
and reports every other overdue entry in its summary, because `AGENTS.md`
forbids requiring an unrelated domain to pass in order to validate the
changed one. In CI the reference date is the date of the commit under test,
so re-running an old commit gives the same answer twice.

## Adding or changing an entry

`CONTRIBUTING.md`, "Register a provisional measure".
