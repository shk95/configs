id: unixlike/generated-config-key-in-schema
statement: A key written into a generated configuration exists in the pinned tool's schema at the locked version, and a tool that migrates its own configuration in place is started once against the rendered file before the change is accepted.
rationale: docs/architecture.md § Unix-like domain
enforced-by: manual the reviewer reads each new or changed key against the pinned tool's source or documentation at the locked version, starts a tool that migrates its own configuration once against the rendered file, and reports both beside the evaluation and build evidence
owner: repository maintainer

Evaluation and `tool/checks/payloads` stop at syntax; a key can parse and
still be one the pinned tool no longer accepts. Such a tool migrates the key
by rewriting its own file, and under Home Manager that file is a symlink
into the read-only store, so the write-back fails closed and the tool never
starts (`git.paging` in `modules/lazygit.nix`, found by review before #161
merged, not by any check). A wrong default cited in a comment for the same
tool family (full-border.yazi) came from the same gap. The evidence is the
reviewer's reading and one start of the built binary against the rendered
home, required by `docs/definition-of-done.md`. Enforcement by a check is
not funded: it would need a declaration per generated file, a pty and a
per-tool pass condition, and fixtures — a project the size of
`tool/checks/payloads`.
