# Candidates

A candidate is an observation, never a rule. Nothing cites a candidate as
authority, and an agent does not follow one as a rule. This directory is the
observation stage a sentence passes through before it is added to a policy
document, and the stage an existing document, script or sentence passes
through before it is removed. `CONTRIBUTING.md § Observe before adding or
removing` is the procedure; `docs/decisions/candidates-observed-before-adoption.md`
records why the stage exists.

What does not wait here: a change that is fatal on a host and invisible to
every gate, and the correction of tracked text that is false today.

## Format

One file per candidate, `docs/candidates/<slug>.md`. Line 1 is `# <Title>`;
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

| Kind | Scope | Title | Record |
|---|---|---|---|
| addition | repository | A review finding is reproduced in its framework before it is written into history | review-finding-reproduced-before-history.md |
| addition | repository | CI runs the Windows checks through the entry point rather than the scripts directly | ci-windows-checks-through-the-entry-point.md |
| addition | repository | Index the Git for Windows error from fetching a linked worktree by symptom | troubleshooting-worktree-fetch-symptom.md |
| addition | repository | Index `file` reporting a PowerShell script as "Windows setup INFormation" | troubleshooting-file-misreads-ps1.md |
| addition | repository | How a topic branch catches up with a moved dev before its native lane runs | topic-branch-catch-up-procedure.md |
| addition | repository | What a commit subject scope names, and which two-scope commits are allowed | subject-scope-and-two-scope-allowance.md |
| addition | repository | A registry entry's rationale section is read to confirm it justifies the statement | rationale-fit-evidence-item.md |
| addition | windows | Fixture tags are checked at Describe granularity; several tags name invariants their case cannot fail on | fixture-tag-fit-below-describe.md |
| addition | repository | A domain's executable entry point lives under the domain's path; the Justfile is an unannotated exception | domain-tool-placement-and-justfile-exception.md |
| addition | windows | Name the older-shell lane and its two scripts in the Windows procedure and evidence list | windows-older-shell-lane-in-procedure.md |
| deletion | windows | windows/tools/check-powershell.ps1 is referenced by nothing | delete-check-powershell-script.md |
| deletion | repository | The registry entry count in docs/status.md rots | drop-registry-count-from-status.md |
| deletion | repository | The sentence that CI and the hooks call the Windows scripts directly | drop-ci-calls-scripts-directly-sentence.md |
