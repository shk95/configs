id: repository/hygiene-exclusion-symmetry
statement: Whatever forgives a hygiene finding is declared with its reason, forgives one string at one path, and is removed once the text it forgave is gone.
rationale: docs/architecture.md § Desired-state hygiene
enforced-by: tool tool/version-control/hygiene
enforced-by: fixture tool/version-control/test
decision: docs/status.md § Desired-state hygiene had no enforcement owner

An allow entry is the one place a violation can be forgiven, so it is held
to the same standard as the scan: a stale entry is a failure, and an entry
that forgives more than the single occurrence it was written for is a
whole-file exemption wearing an exclusion's clothes.
