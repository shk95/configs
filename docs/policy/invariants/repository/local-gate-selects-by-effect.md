id: repository/local-gate-selects-by-effect
statement: Gates select checks by change effect independently of ownership, with conservative coverage for executable inputs and failure on unknown CI inputs.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/dispatch/select
enforced-by: tool tool/dispatch/ci-base
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/local-gate-selects-by-effect.md § The local gate selects checks by effect

The selector is each gate's answer to "which checks does this change
need"; ownership is a different question and stays with the classifier.
The version-control fixture suite copies the hooks, the dispatcher and the
version-control tools into throwaway repositories, copies and scans the
three governance scripts beside them (`tool/setup`, `tool/doctor.sh`,
`tool/worktree.sh`) and greps the CI workflow, so a change under any of
those paths selects it and nothing else does; the Unix-like arm has
narrowed the same way since payload edits stopped forcing a flake
evaluation. Its closing pass runs the real registry checker, which reads
`docs/` and `docs/policy/invariants/`, but that is the same check the pre-commit hook
runs unconditionally, so a documentation or registry change still meets
it. The pre-push audit is the history form: the clone's branches are state
no push can alter, so judging them there would block a push over nothing
the push carries. It judges `dev`, `master` and release-tag reachability
against `origin/dev` and `origin/master` where those refs exist, not against
local branches that may lag them; it still reads every local tag, a gap the
decision record names.

The 2026-09-26 decision amendment extends this selector to CI: document paths
select no domain suite, platform inputs select the complete native suite, and
shared selection machinery selects every suite. Ownership remains separate for
repository-wide scans. Unknown input or an unsupported event is a failure.
