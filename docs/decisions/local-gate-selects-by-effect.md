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
pre-commit, the history audit at pre-push — are unchanged, so a documentation
or registry commit is still held to every rule that reads it. CI is unchanged
on purpose: the selector is the local gate's, and the merge gate runs a
selected domain's whole suite. The remaining local-versus-CI duplication —
a code change under those trees runs the suite at pre-push and again in
CI — is the "know before you push" lane and stays until the maintainer
decides otherwise. The first documentation-only commit after the change is
the proof: its pre-commit runs hygiene, the registry and the secret scan
and no suite.

2026-09-04: the pre-push audit is narrowed to `audit --history`, the form
the merge gate runs. The full form also judges the clone — a local branch
outside the name grammar — and blocked every push from a clone in that state
although no push can change it; a review of the promotion range proved it
with a throwaway clone. The clone-local half stays a read-only check by hand.

2026-09-14: two corrections to the paragraph above (#240). It first also
named a lightweight `*-v*` tag among what the narrowing stopped blocking; it
never did, because the history form reads every local tag with the same
checks as the full form, so a stray local release tag still fails a push.
That sentence is removed and the gap stays: judging only the tags a push
carries is not done. And the history form still read a local `dev` or
`master` before `origin/`; #240 records a Windows capture publish refused on
2026-09-06 and 2026-09-08 because two release tags were unreachable from a
local `master` that had not moved since the clone, while `origin/master`
contained them. The history form now resolves `dev` and `master` together to
`origin/<name>` when that ref exists, else to the local branch; the full form
stays local-first. Resolving only `master` was rejected because a fresh
`origin/master` against a stale local `dev` fails the traceability checks;
dropping tag reachability from the history form was rejected because CI does
not run on a tag push, so pre-push is the only check before a bad tag reaches
the remote. The costs accepted: a clone that has not fetched is judged
against old remote history, and a subject on an unpublished local `dev`
commit is left to the commit-message hook. `tool/version-control/plan-release`
stays on the local `master`, because it plans a tag the clone creates.
