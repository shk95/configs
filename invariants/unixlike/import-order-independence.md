id: unixlike/import-order-independence
statement: No list-valued option depends on the order in which module files were collected.
rationale: docs/architecture.md § Unix-like domain
enforced-by: pending #128
owner: repository maintainer

Module files are gathered by a directory walk. A value that is correct only
because two files happen to sort a certain way breaks on a rename. The
order-sensitive places today are the PATH lines in the shell module's
`initContent` and the merged `home.packages` list; #128 owns a check.
