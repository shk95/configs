id: repository/private-history-acquisition-isolated
statement: Private operating history acquisition authenticates its selected source and repository, gives credentials only to isolated trusted transport, preserves complete original Git objects, and cannot grant retained code credentials or enable operation.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema tool/version-control/release-operating-history.py
enforced-by: fixture tool/version-control/test-release-operating-history
owner: repository maintainer
decision: docs/policy/decisions/repository/authenticated-release-transport.md § Original private Git acquisition

Only a disposable bare repository is returned. Original graph validation and fresh
remote head checks precede retained replay. Partial, poisoned or moving observations
refuse without exposing private diagnostics. Source fixtures are not live permission,
bootstrap or operating evidence.

Read-only initial proposals require successful complete empty ref advertisements,
stable selected identity/default/source/runtime and the exact complete transport
closure. Their private review digest binds original disabled record bytes and
source identities. Recomputed equality grants no approval or publication authority.
