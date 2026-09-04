id: unixlike/import-order-independence
statement: No list-valued option depends on the order in which module files were collected.
rationale: docs/architecture.md § Unix-like domain
enforced-by: tool tool/checks/import-order
enforced-by: fixture tool/checks/import-order-test

Module files are gathered by a directory walk. A value that is correct only
because two files happen to sort a certain way breaks on a rename. The
structural half is the class merge: the fragments a class collects are
merged in the order of the files that define them, so a list two feature
files contribute to — `home.packages` was the case the check found — is
keyed by file rather than by the walk. The proof is by evaluation: every
host is composed twice, in walk order and reversed, and each toplevel
derivation path must be identical, because that path hashes everything that
reaches the host. The fixture adds a pair of files contributing to one
flake-level list at the same order and requires the check to refuse it. The
check evaluates every host twice, so the merge gate runs it and the local
gate does not (#128).
