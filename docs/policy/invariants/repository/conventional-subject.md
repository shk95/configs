id: repository/conventional-subject
statement: A non-merge commit subject is a Conventional Commit of at most seventy-two characters.
rationale: docs/policy/architecture.md § Version control and releases
enforced-by: tool .githooks/commit-msg
enforced-by: tool tool/version-control/audit
enforced-by: fixture tool/version-control/test

The commit-message hook is the owner of the grammar, including which
subjects Git writes itself and are exempt. `tool/version-control/audit`
asks the hook rather than keeping a pattern of its own, so history audit and
the commit gate cannot disagree.

CI names the commit under test; pre-push names the transmitted range instead
of unrelated checked-out work. Current audit uses master and explicit
revisions, without a dev dependency. Optional PR titles and generated merge
subjects are outside the ordinary source-subject grammar.
