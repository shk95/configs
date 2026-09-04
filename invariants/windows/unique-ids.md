id: windows/unique-ids
statement: No two packages and no two managed files share an identifier.
rationale: docs/architecture.md § Windows domain
enforced-by: pending #134
owner: repository maintainer

Only feature ids are checked for duplicates today. A duplicated package or
managed-file id would let a plan or a state record name one item and mean
another; #134 owns the loader check and its fixture.
