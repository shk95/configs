# The hygiene tool owns desired-state hygiene

date: 2026-08-30
scope: repository
status: accepted
reopen-when: This implementation is superseded when the same four axes are decided from a typed declaration rather than from text.
source: 9f1e8ce:docs/status.md § Desired-state hygiene had no enforcement owner

`AGENTS.md` has asked since the three-domain split that secrets, undeclared
usernames, absolute home paths, and snapshots of runtime state stay out of
every domain's committed desired state. Only the first quarter of that sentence
was enforced. `gitleaks` covers secrets from the pre-commit hook and the CI
secret job; one Pester assertion covered a single literal user path inside one
directory of the Windows payloads. Nothing looked at the rest, and the
2026-08-29 audit found the gap had already been used: two absolute home paths
sat in `docs/reference/troubleshooting.md` for the document's whole history. A rule with a
policy owner and no enforcement owner is exactly what the governance
decomposition says must not exist.

`tool/version-control/hygiene` is that enforcement owner now. It scans the
index along four axes — absolute home paths, undeclared user and host names,
tracked runtime state, and machine-unique identifiers — needs nothing beyond a
POSIX shell and Git, and runs unconditionally beside the secret scan instead of
through `tool/dispatch/select`, because it is repository-wide and
domain-agnostic in the same way the secret scan is. Routing it through dispatch
would also have pulled an unrelated domain's checks into a governance-only
commit. Its fixtures are folded into `tool/version-control/test` rather than
given a runner of their own, because that script is the only thing the
`repository:fixtures` unit and the CI repository job invoke, and a check whose
fixtures nothing runs is not enforced.

Amended 2026-09-25 for the host-provider transition: Axis 2 reads
`tool/version-control/hygiene.names` from the Git index. Its one-name-per-line
declaration replaces the old Unix-like inventory as the scan's input, so the
repository-wide check does not depend on one configuration domain. It still
needs only a POSIX shell and Git and fails closed when the declaration is
absent or empty. The initial set preserves the names the old inventory
admitted; entries leave as their desired state moves to the private consumer.

The condition for removing it is the one the payload declaration already sets:
coverage enforced in both directions, positive and negative fixtures for every
axis, and no host prerequisite beyond those the governance plane already has.
