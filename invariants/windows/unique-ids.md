id: windows/unique-ids
statement: No two packages and no two managed files share an identifier.
rationale: docs/architecture.md § Windows domain
enforced-by: schema windows/src/WinEnv.psm1
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

A plan and a state record name a package or a managed file by its id, so a
second declaration of one would let the name mean either item. The loader
refuses a duplicate feature, package, or managed-file id and an item of
any of the three kinds that declares none. Each kind is its own namespace: a plan says "package" or
"managed file" before the id, so one spelling in both lists is unambiguous
and only the same spelling twice in one list is refused. Until #134 only
feature ids were checked.
