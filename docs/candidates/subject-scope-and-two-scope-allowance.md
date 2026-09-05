# What a commit subject scope names, and which two-scope commits are allowed

kind: addition
scope: repository
first-observed: 2026-09-05
target: CONTRIBUTING.md § Branch and commit flow (what the scope names); § Add or change an invariant, the sentence calling the manual-entry pairing "the one accepted two-scope commit"; § Classify the change; the Classify step of the skill reduced to a pointer
promote-when: a reviewer or an author re-derives either rule wrongly once more, or CONTRIBUTING § Branch and commit flow is edited anyway
drop-when: no new occurrence by 2027-03-05

## Observation

Two facts are unwritten. The scope in a subject names the domain the change describes, not the classifier's verdict: `docs(windows)` commits that touch only `docs/status.md` (which classifies `repository`) are the precedent (6ea6748, 09a60d1, 9e0f9a1). And CONTRIBUTING calls the manual-entry-plus-evidence pairing "the one accepted two-scope commit" while the skill states a general allowance ("`repository` may accompany a domain only for supporting documentation or enforcement"); ee33884 (windows sources plus their decision record) passed under the skill's wording, so orchestration currently out-states policy. Open question for the maintainer: is the allowance supporting documentation only, or documentation and enforcement?

## Evidence

- `CONTRIBUTING.md § Add or change an invariant`, step 4; `.agents/skills/run-version-control-workflow/SKILL.md`, Classify.
- `.githooks/pre-commit` refuses only an unclassified path; `tool/dispatch/select` counts no scopes.

## Occurrences

- 2026-09-05: a plan reviewer rejected correct commit boundaries on both points; rejected on precedent.
