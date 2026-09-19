# Report: gather the repository's documents under one tree classified by scope

kind: report
spec: docs/work/repository/docs-layout/spec.md
status: pending

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Step 1, on `feature/repository-docs-layout` before commit: `git ls-files` over every old location (`invariants`, `provisional`, `docs/design`, `docs/decisions`, `docs/candidates`, and the five root documents) lists 0 files. The staged change holds 123 renames and 5 delete/add pairs whose content moved too far for rename detection (the two area READMEs that lost their index, two candidates, and the split status file). |
| AC2 | verified | `tool/version-control/test` passes with fixtures for each area's scope position in each scope, `repository` for the other documents, and `unclassified` for a scope position naming no domain (`docs/work/linux/…`, `docs/status/linux.md`, `docs/policy/invariants/common/…`), a scope name in another position (`docs/work/unixlike.md`, `docs/policy/decisions/windows.md`, `docs/status/unixlike/…`) and a file beside an area's contract; a scope name as a slug or outside the areas is `repository`. |
| AC3 | verified | `invariants`: 60 registered (the 59, ids unchanged, plus `repository/document-index-generated`), 0 pending, 0 untagged. `provisional`: 1 registered, 0 overdue, which is the moved entry (the second, added the same day, is AC12's). The fixture "P6 the entry does not carry its own tag" fails the suite when the P6 exclusion is set back to the old literal `provisional/` (mutation run, restored). An independent review found the first version of that fixture wrote a live `PROV` tag and failed `provisional` on the tree; the id now reaches it through a variable, and `provisional` passes on the tree. |
| AC4 | pending | After step 1, outside `unixlike/`, `windows/` and `docs/work/`, the search finds only exempt hits: the tree drawing in `docs/README.md`, the decision record's account of the old layout, and the classifier's transitional arms and their fixtures. Three more hits are dated accounts that name the new path beside the old one, exempt since the amendment of 2026-09-19: `docs/status/repository.md` ("`docs/design/` (since 2026-09-19 `docs/work/`)") and two lines of `docs/policy/candidates/repository/citation-by-section-not-line.md`. The two citations of the deleted candidate are pinned to `64a2a85`. 22 files in the domain trees remain for steps 2 and 3. |
| AC5 | pending | Line comparison of the old files against the split ones: every line not found verbatim is a rewritten path, a heading, the intro, the removed "Pending invariants" section, or one of three facts in `docs/status/repository.md` this change made stale (the registry count 56 → 60, the scan count seven → eight, and the design area's new place). Re-run on 2026-09-19 at 790ca6c word by word with paths normalised: 77 checklist lines before and after, all eight open conditions placed as the mapping says. Awaits review. |
| AC6 | pending | Fixtures: `docs/policy/invariants/unixlike/…` and `docs/policy/definition-of-done/unixlike.md` both classify `unixlike`; C5 reads the entry's scope file, proved by a fixture that refuses a Unix-like manual entry listed only in the repository file and accepts it listed in the Unix-like one. The exception is gone from `CONTRIBUTING.md` and the skill. Awaits review. |
| AC7 | verified | `tool/version-control/records` passes on the tree (3 area READMEs); its fixtures refuse a README row naming a document, accept a README with only a slug template, list in `--table` a record nothing names, and refuse an unknown area. The three hand-kept index tables are removed. |
| AC8 | pending | `docs/policy/decisions/repository/documents-classified-by-scope.md` states the rule and the step 1 exception. Awaits review. |
| AC9 | verified | `tool/dispatch/select` fixtures: a Unix-like provisional entry, a Unix-like invariant, a Windows decision, the two domain status files and a Unix-like work item select nothing at commit or push; deleting from the registries' old roots selects nothing; a misplaced document still selects `unclassified`. |
| AC10 | pending | |
| AC11 | pending | `docs/README.md` added; `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, the skill and the architecture document updated. Awaits review. |
| AC12 | verified | The entry `repository/classify-registry-old-roots` under `docs/provisional/` registers the classifier's old-root arms, the selector's filter and their fixtures, exit condition the moving commit being an ancestor of `master`. `provisional`: 2 registered, 0 overdue. Mutation runs on the staged tree, each restored: with the entry out of the index the four tagged places fail P7 (`tool/version-control/classify`, `tool/dispatch/select`, two in `tool/version-control/test`); with the tags removed the entry fails P6. |

## Steps

| Step | Pull request | Notes |
| --- | --- | --- |
| 1 move | #260, merged into `dev` as bfe7d8b | Local checks before commit: `tool/version-control/test` passed; `invariants`, `provisional`, `records`, `design-citations`, `hygiene`, `domain-reads` pass; `audit` 0 failures. An independent review of the staged change raised 16 findings; each was reproduced, and all but two were fixed before commit. Accepted as they stand: `design-citations` exempts all of `classify` rather than only its case arms, and the candidate and work READMEs still list `common` as a scope although no `common` directory classifies until that domain exists. |
| 2 unixlike citations | | |
| 3 windows citations | | |
