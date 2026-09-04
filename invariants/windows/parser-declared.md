id: windows/parser-declared
statement: A managed file's parser names a validator the domain has, and an unknown value is refused at load.
rationale: docs/architecture.md § Windows domain
enforced-by: pending #135
owner: repository maintainer

The comparison mode is validated against a declared list; the parser is
not, and the validator's switch has no default arm, so an unknown parser
falls through and the source counts as parsed. That is a silent acceptance,
not merely a missing check; #135 owns the refusal and its fixture.
