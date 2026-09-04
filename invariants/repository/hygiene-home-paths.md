id: repository/hygiene-home-paths
statement: An absolute path into a home directory is never desired state, in any spelling a supported host writes; a declared value interpolated into a path is not one.
rationale: docs/architecture.md § Desired-state hygiene
enforced-by: tool tool/version-control/hygiene
enforced-by: fixture tool/version-control/test
decision: docs/decisions/hygiene-tool-owns-enforcement.md § The hygiene tool owns desired-state hygiene

Axis 1 of the hygiene scan: POSIX, Windows drive-letter, and WSL UNC forms,
including the JSON-escaped spelling a Windows payload carries.
