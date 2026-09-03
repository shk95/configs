id: repository/hygiene-prose-account-name
statement: A bare account name in free prose does not reach committed desired state.
rationale: docs/architecture.md § Desired-state hygiene
enforced-by: manual the reviewer reads the prose in the diff for a bare account name and reports that reading
owner: repository maintainer

No scanner decides this: a name in prose has no naming context to recognise
it by. The evidence is the reviewer's reading, required by
`docs/definition-of-done.md`.
