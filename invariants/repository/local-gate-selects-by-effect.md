id: repository/local-gate-selects-by-effect
statement: A local gate runs a check unit only for a change that can alter that unit's result, and the merge gate runs a domain's whole suite.
rationale: docs/architecture.md § Repository governance plane
enforced-by: tool tool/dispatch/select
enforced-by: fixture tool/version-control/test
decision: docs/status.md § Local gate selection

The selector is the local gate's answer to "which checks does this change
need"; ownership is a different question and stays with the classifier.
The version-control fixture suite copies the hooks, the dispatcher and the
version-control tools into throwaway repositories and greps the CI
workflow, so a change under those four trees selects it and nothing else
does; the Unix-like arm has narrowed the same way since payload edits
stopped forcing a flake evaluation. The policy checks the hooks run
unconditionally — hygiene, the registry, the secret scan, the audit — are
not units the selector decides, so a documentation or registry change still
meets them. The merge gate is deliberately outside this rule: it runs each
selected domain's whole suite because it optimises for completeness.
