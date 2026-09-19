id: repository/no-closing-keyword
statement: No commit message on its way to dev and no promotion pull request body carries a GitHub closing keyword before an issue reference.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/closing-keywords
enforced-by: fixture tool/version-control/test
decision: docs/policy/decisions/repository/work-planned-and-verified-in-documents.md § Work is planned and verified in documents, and a branch is one increment

GitHub closes a referenced issue when a closing keyword reaches the default
branch. Every pull request targets `dev`, so the keyword does nothing when
the work merges and then closes the issue at a promotion — an event that
accepts source history and certifies nothing, at a moment unrelated to the
work. An execution issue closes from what its report says, so a message
links with `Refs #<n>` and never closes.

Hooks are opt-in, so the commit-message hook is the early check and the merge
gate the complete one: it reads every commit message of a pull request whose
base is `dev`, merges included. A promotion's range is not read. `dev`
carried two commits with a closing keyword when the rule arrived, history is
not rewritten, and every later commit was read on its way into `dev`; the
promotion answers for its body instead, read as it stands when the job runs.

Accepted limits: a closing reference written as an issue URL is outside the
forms the rule lists; a pull request's own body is not read, because a pull
request into `dev` closes nothing; and a promotion body edited after the job
ran is judged only when the job runs again.
