# Gather the repository's documents under one tree classified by scope

kind: spec
date: 2026-09-19
scope: repository
status: approved
review-by: 2026-10-10
issue: #259

Agreed with the maintainer in the session of 2026-09-19 and revised the same
day after an independent review whose findings were reproduced before they
were applied. This is the first spec written in the `docs/work/` form;
`docs/work/repository/work-model/` defines that form and its checks, and its
checker is expected to accept this pair once it exists.

## Problem

1. **The documents sit in three root directories that form one system.**
   `docs/`, `invariants/` and `provisional/` are siblings at the root, while
   what they hold is one flow — observe (`docs/candidates/`), adopt
   (`docs/decisions/`), enforce (`invariants/`) — beside one code-side
   registry (`provisional/`), the model (`docs/architecture.md`), current
   state (`docs/status.md`) and design arguments (`docs/design/`). The split
   reads as "machine-read registries versus prose", but decision record
   headers are machine-read too, so that line does not hold.
2. **Everything under `docs/` classifies as `repository`**
   (`tool/version-control/classify`, the `docs/*` arm), although of the 42
   decision records 13 are `unixlike`, 14 are `windows` and one spans both,
   and `docs/status.md` and `docs/definition-of-done.md` already hold one
   section per domain. One scope per commit is policy
   (`CONTRIBUTING.md`, "Branch and commit flow"; no hook enforces it), so a
   domain change that records its state or its evidence item needs a second,
   `repository` change — #205 and #238 are that cost — and
   `CONTRIBUTING.md` carries one standing exception for it (an invariant
   entry together with its evidence item).
3. **Hand-maintained indexes turn every new record into a repository
   edit.** `docs/decisions/README.md` holds a 42-row table.
4. **`docs/work/` is about to hold spec and report pairs that belong in the
   same change as the domain work they describe.** Under problem 2 they
   could not be.

## Target tree

```
AGENTS.md  CONTRIBUTING.md  README.md        root, unchanged
docs/
  README.md                                  map of this tree
  policy/                                    observe → adopt → enforce
    architecture.md                          single, repository
    definition-of-done/<scope>.md
    candidates/README.md, <scope>/<slug>.md  observation; carries no authority
    decisions/README.md, <scope>/<slug>.md
    invariants/README.md, <scope>/<slug>.md
  provisional/README.md, <scope>/<slug>.md   temporary measures in code
  work/
    README.md
    <scope>/<slug>/<kind>.md
  status/<scope>.md
  reference/
    troubleshooting.md
    wsl-interop.md
```

No path carries a date. Where a document has a date it is a header, as
decision records and design documents already do.

## Classification rule

Each document area has one scope position, and the scope named there owns
the document: the directory directly under `docs/policy/candidates/`,
`docs/policy/decisions/`, `docs/policy/invariants/`, `docs/provisional/` and
`docs/work/`, and the file name under `docs/status/` and
`docs/policy/definition-of-done/`, for `<scope>` in `unixlike`, `windows`,
`repository`. Anything else inside those areas — a scope position that names
no domain, as an unknown scope under `invariants/` is today, a scope name in
another position, or a file beside an area's `README.md` (and, for
`docs/work/`, its `roadmap.md`) — is unclassified. A `docs/` file outside the
areas classifies as `repository`. A scope directory or file exists
only for a domain that exists; `common` has none, as today.

A document spanning scopes lives under `repository` and lists every scope in
its header. `docs/policy/architecture.md` stays single and `repository`: it
is the cross-domain model, and a domain invariant that needs a new rationale
still edits it. That cost is accepted as rare.

Classification decides ownership; check selection stays by effect
(`INV repository/local-gate-selects-by-effect`). `tool/dispatch/select`
selects no domain suite for a change confined to `docs/`. That changes one
behaviour: a Unix-like provisional entry used to select the Unix-like payload
check, which does not read the registry.

## Mapping

| Now | Target | Rule |
| --- | --- | --- |
| `docs/architecture.md` | `docs/policy/architecture.md` | |
| `docs/definition-of-done.md` | `docs/policy/definition-of-done/{repository,unixlike,windows}.md` | "Unix-like domain" → unixlike; "Windows domain" → windows; every other section, "Common domain" included, → repository |
| `docs/decisions/README.md` | `docs/policy/decisions/README.md` | format contract only; the index table is removed |
| `docs/decisions/*.md` (42) | `docs/policy/decisions/<scope>/` | the record's `scope:`; a record with more than one (`powershell-copied-per-domain.md`) → repository |
| `docs/candidates/README.md` | `docs/policy/candidates/README.md` | |
| `docs/candidates/*.md` (12) | `docs/policy/candidates/<scope>/` | the candidate's `scope:` |
| `invariants/README.md` | `docs/policy/invariants/README.md` | |
| `invariants/<scope>/*.md` (59) | `docs/policy/invariants/<scope>/` | ids unchanged |
| `provisional/README.md` | `docs/provisional/README.md` | |
| `provisional/<scope>/*.md` (1) | `docs/provisional/<scope>/` | ids unchanged |
| the design area's `README.md` | `docs/work/README.md` | carried as it stands; `work-model` rewrites it |
| `docs/design/*.md` (4) | `docs/work/repository/<slug>/<kind>.md` | each is `repository` or spans scopes; `kind:` names the file (`study.md`, `plan.md`, `map.md`) |
| `docs/status.md` | `docs/status/{repository,unixlike,windows}.md` | "Unix-like" → unixlike; "Windows" → windows; "Repository" and "Common" → repository; each "Open conditions" item → the scope that owns its subject; "Pending invariants" is removed, because `tool/version-control/invariants --table` is its source |
| `docs/troubleshooting.md`, `docs/wsl-interop.md` | `docs/reference/` | |

Open conditions by owner: the CI runner decision, the PowerShell copy, the
milestone review, the hygiene tool and the annotated tag → repository; the
Windows 10 support boundary and the resumed `capture -Publish` → windows;
the Darwin zellij overlay → unixlike.

## Generated indexes

No area keeps a hand-maintained list of its own files. A new invariant,
`document-index-generated`, states it; `tool/version-control/records`
refuses an area README that names one of the area's documents and, with
`--table decisions|candidates|work`, prints the index from their headers, the
way `tool/version-control/invariants --table` and
`tool/version-control/provisional --table` already do for theirs. It runs in
the pre-commit hook and the CI scan job.

## Sequence

A move of a document into a domain's scope directory touches two scopes, and
so does the rewriting of the pointers the checkers validate: 55 invariant
entries carry `rationale: docs/architecture.md § …`, the invariant checker
hard-codes that path (C9) and the definition-of-done path (C5), the
provisional entry's `decision:` names a decision record, and
`tool/version-control/hygiene.allow` names `docs/troubleshooting.md`. A
rename alone fails those checks, so each move and the pointers into it land
together.

Two-scope commits are refused by policy, not by a hook. A decision record
landing in step 1 makes the one exception this move needs: the step 1
commit touches `repository`, `unixlike` and `windows` paths because it moves
documents between them, and it creates no configuration output. CI selects
every lane a change touches (the `classify` job), so the exception loses no
evidence. A provisional measure that classified the whole new tree as
`repository` for the migration was considered and rejected: it needs its own
decision record and issue in any case, it withholds the domain suites for
its duration, and it adds two steps.

| Step | Scopes | Content |
| --- | --- | --- |
| 1 move | repository, unixlike, windows | One commit and one pull request. The decision record for the classification rule and this exception. `git mv` of every file per the mapping; the split of status and definition of done; every pointer the checkers validate, rewritten; every tool at its new roots (`classify` at the final rule, `invariants` C1/C4/C5/C9, `provisional` roots and the P6 exclusion of the registry's own directory, `design-citations` roots and exclusions, `hygiene` and `hygiene.allow`, `tool/dispatch/select`, `tool/version-control/test` fixtures, `.githooks/pre-commit` hints); the index generator; `docs/README.md`; `AGENTS.md`, `CONTRIBUTING.md` (the two-scope exception removed), `README.md`, the skill, `docs/policy/architecture.md`, the zellij watch workflow's issue text, and the help text `Get-Help` shows (the `.LINK` in `windows/tools/setup.ps1`, a `.DESCRIPTION` in `windows/src/WinEnv.psm1`). The three spec and report pairs written on 2026-09-19 land here. |
| 2 | unixlike | The citations of moved paths in `unixlike/` (20 files; `unixlike/modules/lazygit.nix` cites upstream's `docs/Config.md` and stays). Two are payloads (`zellij/config.kdl`, `karabiner/tool`), so the home derivations change hash; no activation is needed for a comment. |
| 3 | windows | The remaining citations in `windows/` comments. |

Between steps 1 and 3, comments in the domain trees name paths that no
longer exist. Nothing reads them as code (`domain-reads` strips comments),
and the text a user sees — the `.LINK` in `windows/tools/setup.ps1` and the
`.DESCRIPTION` of `Test-WinEnvWslConfigSupport` in `windows/src/WinEnv.psm1`,
both shown by `Get-Help` — moves in step 1.

The classifier keeps arms for the registries' old roots
(`invariants/`, `provisional/`) until the move has reached `master`: their
deletion sits inside every pull-request and promotion range that spans it,
and an unclassified path cannot be pushed. Removing those arms is a
repository change after the promotion.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | The tracked tree matches the target: no tracked file remains under `invariants/`, `provisional/`, `docs/design/`, `docs/decisions/`, `docs/candidates/`, or at `docs/{architecture,definition-of-done,status,troubleshooting,wsl-interop}.md`. | policy checks |
| AC2 | `classify` places a document in the scope its area's scope position names and a document outside the areas in `repository`, and refuses anything else inside an area, proved by fixtures in both directions, including a scope name that is not a domain and a scope name in the wrong position. | fixtures |
| AC3 | The invariant and provisional checks pass at the new roots with the same entries — the 59 invariants, every id unchanged, plus `document-index-generated`, and 1 provisional measure — and a fixture proves the provisional entry's own tag line does not satisfy P6 at the new root. | fixtures, policy checks |
| AC4 | Outside `docs/work/`, no tracked file cites a moved path in its old form, read by a search over the tree after step 3 and recorded here. Commit-pinned citations (`<sha>:<path>`), upstream paths, a decision record's account of the old layout, and the classifier's transitional arms and their fixtures are exempt; the pre-existing references to the missing `domain-tool-placement-and-justfile-exception.md` candidate are corrected or recorded. | policy checks |
| AC5 | Every paragraph of `docs/status.md` and every checklist line of `docs/definition-of-done.md` lands in exactly one scope file; nothing is dropped except the "Pending invariants" section. | review |
| AC6 | An invariant entry and its evidence item in the same domain classify as one scope, and `CONTRIBUTING.md` no longer carries the two-scope commit exception. | fixtures, review |
| AC7 | No hand-maintained index remains; the generator prints the decision, candidate and work indexes from headers, and a fixture proves it lists a file it was not told about. | fixtures |
| AC8 | The decision record states the classification rule and the step 1 exception, and nothing else in `CONTRIBUTING.md` or `AGENTS.md` contradicts it. | review |
| AC9 | A change confined to `docs/**/unixlike/` or `docs/**/windows/` selects no domain suite at commit or push, proved by a `tool/dispatch/select` fixture. | fixtures |
| AC10 | Every step's pull request passes `Required checks`, and the hooks ran on every commit. | affected dispatch |
| AC11 | `docs/README.md` maps the tree, and `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, the skill and the architecture document describe the new layout. | review |

## Out of scope

- The work model — the spec and report rules, their checker, issue roles,
  retiring milestones, and the restated authority boundary — is
  `docs/work/repository/work-model/`. This spec carries the design area to
  its new place; `design-citations` treats `docs/work/` as it treats
  `docs/design/` today.
- Any change to what a moved document says, beyond paths, the status and
  definition-of-done split, and the removed index.
- Splitting `docs/policy/architecture.md` or `docs/reference/`.

## Risks

- About 600 path references move. The previous migration counted three
  tools and met fourteen planes; the step 1 commit cannot pass its own hooks
  until every reader of an old path is found, which is where the unexpected
  ones surface.
- The step 1 diff is large. Rename detection keeps blame where content
  similarity holds; the split files are new files.
- CI's job selection follows classification, so after the move a
  status-only change in a domain runs that domain's full CI job. The local
  gate does not (AC9); the CI cost is accepted.
- Parallel sessions push to `dev`; fetch `origin/dev` before each step.
