id: repository/local-gate-selects-by-effect
statement: A local gate runs a check unit only for a change that can alter that unit's result, and the merge gate runs a domain's whole suite.
rationale: docs/architecture.md § Repository governance plane
enforced-by: tool tool/dispatch/select
enforced-by: fixture tool/version-control/test
decision: docs/decisions/local-gate-selects-by-effect.md § The local gate selects checks by effect

The selector is the local gate's answer to "which checks does this change
need"; ownership is a different question and stays with the classifier.
The version-control fixture suite copies the hooks, the dispatcher and the
version-control tools into throwaway repositories, copies and scans the
three governance scripts beside them (`tool/setup`, `tool/doctor.sh`,
`tool/worktree.sh`) and greps the CI workflow, so a change under any of
those paths selects it and nothing else does; the Unix-like arm has
narrowed the same way since payload edits stopped forcing a flake
evaluation. Its closing pass runs the real registry checker, which reads
`docs/` and `invariants/`, but that is the same check the pre-commit hook
runs unconditionally, so a documentation or registry change still meets
it. The pre-push audit is the history form: the clone's branches and tags
are state no push can alter, so judging them there would block a push over
nothing the push carries. The merge gate is outside the selector's rule and the suite holds that
too: the workflow runs the whole suite and never names the selector.
