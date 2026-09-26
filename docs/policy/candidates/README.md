# Candidates

A candidate is an observation, never a rule. Nothing cites a candidate as
authority, and an agent does not follow one as a rule. This directory is the
observation stage a sentence passes through before it is added to a policy
document, and the stage an existing document, script or sentence passes
through before it is removed. `CONTRIBUTING.md § Observe before adding or
removing` is the procedure; `docs/policy/decisions/repository/candidates-observed-before-adoption.md`
records why the stage exists.

What does not wait here: a change that is fatal on a host and invisible to
every gate, and the correction of tracked text that is false today.

## Format

One file per candidate, `docs/policy/candidates/<scope>/<slug>.md`, under the scope its `scope:` names. Line 1 is `# <Title>`;
then a header of `key: value` lines up to the first blank line, parsed the
way decision records are; then three sections, `Observation`, `Evidence`,
`Occurrences`. The observation says what was met and where, not the rule
someone would like to exist.

| Key | Meaning |
|---|---|
| `kind` | `addition` (text or a check that does not exist yet) or `deletion` (text, a script or a sentence judged stale). |
| `scope` | `unixlike`, `windows`, `repository` or `common`: the scope the promoted change would classify as. |
| `first-observed` | `YYYY-MM-DD`. |
| `target` | Where the change would land, or what would be removed. |
| `promote-when` | The criterion that turns the observation into a change. |
| `drop-when` | The date or event after which the candidate is deleted unpromoted. |

Each later occurrence is one dated line under `Occurrences` with its
evidence. Promotion makes the change through its owning scope's flow and
deletes the file in the same pull request; dropping deletes the file.
History is the record either way. There is no checker for this directory
on purpose.

## Index

The list is printed from the documents' headers, not kept here:
`tool/configs records --table candidates`
(`INV repository/document-index-generated`).
