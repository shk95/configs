id: repository/fixture-git-isolation
statement: The version-control fixture suite and its child commands own their disposable repositories and local transports without inheriting caller repository context or external routing configuration.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: fixture tool/version-control/fixture-git-isolation-test

Fixture mutations are authorized only in their synthetic repositories, not
in the caller's checkout or its remote. The test-only environment boundary
removes inherited repository and command configuration, ignores system/user
configuration and templates, and permits only local file transport.
Positive cases retain local clone, push and fetch. Negative cases inject
command and ambient push URLs, rewrite rules, repository context and a
network transport request, using only disposable local receivers.
Production hooks and operator commands retain their caller configuration.
This entry covers the version-control suite entry and inherited child
commands, not independent fixture entry points that do not use that boundary.
