# Decision records

One file per decision that is expensive to reverse or that a reviewer will
ask about. `docs/status/` holds current state and links here;
`docs/policy/architecture.md` holds the model; a record holds one choice, why it
was made, what was rejected, and what it costs. A record is cited by path
(`docs/policy/decisions/<scope>/<slug>.md`, under the scope its `scope:` names, or `repository` for a record that spans scopes); a registry entry cites it as
`decision: docs/policy/decisions/<scope>/<slug>.md § <Title>`, which
`tool/version-control/invariants` checks (rule C4).

## Format

Line 1 is `# <Title>`, the text a registry pointer names. Then a header of
`key: value` lines up to the first blank line, parsed the way registry
entries are (`docs/policy/invariants/README.md`); a list is a repeated key. Then prose.

| Key | Count | Meaning |
|---|---|---|
| `date` | 1 | `YYYY-MM-DD` of the decision; later elaborations carry their own date in prose. |
| `scope` | 1+ | `unixlike`, `windows`, `repository` or `common`; repeated for a decision spanning domains, which then lives under `repository`. |
| `status` | 1 | `accepted` or `superseded`. |
| `issue` | 0+ | `#<n>`. |
| `reopen-when` | 0–1 | One sentence naming the condition under which the decision is revisited. |
| `supersedes`, `superseded-by` | 0–1 each | A record path. |
| `source` | 0+ | Where the record came from — the text it was extracted from, or the design document whose argument it adopts — as `<commit>:<path> § <heading>`; never checked. |

Extending or correcting a decision edits its record and appends a dated
paragraph. Reversing one creates a new record, sets the old one to
`status: superseded` with `superseded-by`, and moves every `decision:`
pointer in the same commit, because the checker cannot tell a superseded
record from a live one. Prose and code cite a record by path only; a quoted
heading is checked by nothing and rots. `CONTRIBUTING.md § Record a
decision` is the procedure.

## Index

The list is printed from the documents' headers, not kept here:
`tool/version-control/records --table decisions`
(`INV repository/document-index-generated`).
