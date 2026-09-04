# Decision records

One file per decision that is expensive to reverse or that a reviewer will
ask about. `docs/status.md` holds current state and links here;
`docs/architecture.md` holds the model; a record holds one choice, why it
was made, what was rejected, and what it costs. A record is cited by path
(`docs/decisions/<slug>.md`); a registry entry cites it as
`decision: docs/decisions/<slug>.md § <Title>`, which
`tool/version-control/invariants` checks (rule C4).

## Format

Line 1 is `# <Title>`, the text a registry pointer names. Then a header of
`key: value` lines up to the first blank line, parsed the way registry
entries are (`invariants/README.md`); a list is a repeated key. Then prose.

| Key | Count | Meaning |
|---|---|---|
| `date` | 1 | `YYYY-MM-DD` of the decision; later elaborations carry their own date in prose. |
| `scope` | 1+ | `unixlike`, `windows`, `repository` or `common`; repeated for a decision spanning domains. |
| `status` | 1 | `accepted` or `superseded`. |
| `issue` | 0+ | `#<n>`. |
| `reopen-when` | 0–1 | One sentence naming the condition under which the decision is revisited. |
| `supersedes`, `superseded-by` | 0–1 each | A record path. |
| `source` | 0+ | Provenance of an extracted record, `<commit>:<path> § <heading>`; never checked. |

Extending or correcting a decision edits its record and appends a dated
paragraph. Reversing one creates a new record, sets the old one to
`status: superseded` with `superseded-by`, and moves every `decision:`
pointer in the same commit, because the checker cannot tell a superseded
record from a live one. Prose and code cite a record by path only; a quoted
heading is checked by nothing and rots. `CONTRIBUTING.md § Record a
decision` is the procedure.

## Index

| Date | Scope | Title | Status | Record |
|---|---|---|---|---|
| 2026-08-12 | unixlike | Home Manager platform classes are overlays | accepted | home-manager-platform-classes.md |
| 2026-08-12 | unixlike | Homebrew owns Mac App Store and macOS GUI applications | accepted | homebrew-owns-mac-apps.md |
| 2026-08-12 | unixlike | The identity contract and its values are separate | accepted | identity-contract-values-separated.md |
| 2026-08-16 | unixlike | SDKMAN is adopted but not owned | accepted | sdkman-adopted-not-owned.md |
| 2026-08-16 | unixlike | Every payload declares its format and is parsed | accepted | payloads-declared-and-parsed.md |
| 2026-09-03 | unixlike | A package is owned by the module that configures it | accepted | package-ownership-by-generating-module.md |
