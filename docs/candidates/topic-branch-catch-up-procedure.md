# How a topic branch catches up with a moved dev before its native lane runs

kind: addition
scope: repository
first-observed: 2026-09-05
target: CONTRIBUTING.md § Branch and commit flow (two sentences); the Integrate step of the version-control skill (one)
promote-when: a pull request is merged whose native evidence was taken from a tip that did not contain dev, or a second session asks how to catch up
drop-when: no new occurrence by 2027-03-05

## Observation

`dev` requires an up-to-date base and the repository forbids rebasing published work, but no document says how a topic branch catches up. `git merge-tree --write-tree HEAD origin/dev` shows conflicts read-only; a local `Merge branch 'dev' into <branch>` lets the hooks and the native lane run on the tree that would land, where `gh pr update-branch` makes GitHub author the merge outside both. History holds 23 such local merges done correctly without a document, which is evidence the procedure is known, not that it is missing.

## Evidence

- `grep -rn 'merge-tree\|update-branch'` over the tree is empty; `git log --grep="Merge branch 'dev' into"` lists 23 commits.
- `tool/version-control/commit` refuses a stale local dev at branch creation and names the fast-forward, but only there.

## Occurrences

- 2026-09-05: #170 needed it once (CONTRIBUTING conflict with #169), resolved locally.
