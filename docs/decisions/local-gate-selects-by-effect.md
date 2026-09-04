# The local gate selects checks by effect

date: 2026-09-04
scope: repository
status: accepted
issue: #138
source: 9f1e8ce:docs/status.md § Local gate selection

Measured on 2026-09-04 over the two pruning pull requests (#137, #139):
four of eleven commits changed only `docs/` or `invariants/`, and each paid
`tool/version-control/test` — about 48 seconds — at pre-commit and again at
pre-push, because `tool/dispatch/select` emitted `repository:fixtures` for
any `repository`-scope path. The suite's own inputs are elsewhere: it copies
`.githooks`, `tool/dispatch` and `tool/version-control` into throwaway
repositories, copies and scans `tool/setup`, `tool/doctor.sh` and
`tool/worktree.sh`, and greps `.github/workflows/ci.yml`. Its closing pass
runs the real registry checker over `docs/` and `invariants/`, which is the
same check pre-commit runs unconditionally.

The decision (#138) is to select the suite only for a change under one of
those paths, the same narrowing the Unix-like arm has had since a payload
edit stopped forcing a flake evaluation. The policy checks the hooks run
unconditionally — hygiene, the invariant registry, the secret scan at
pre-commit, the audit at pre-push — are unchanged, so a documentation or
registry commit is still held to every rule that reads it. CI is unchanged
on purpose: the selector is the local gate's, and the merge gate runs a
selected domain's whole suite. The remaining local-versus-CI duplication —
a code change under those trees runs the suite at pre-push and again in
CI — is the "know before you push" lane and stays until the maintainer
decides otherwise. The first documentation-only commit after the change is
the proof: its pre-commit runs hygiene, the registry and the secret scan
and no suite.
