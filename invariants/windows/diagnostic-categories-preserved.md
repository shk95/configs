id: windows/diagnostic-categories-preserved
statement: Windows check and verification output labels an unavailable Appx or terminal-support observation separately from a known terminal-delegation support limit, carries each such reason once into the status count and each categorized reason list used by normal and REQUIRE_NATIVE presentation, and does not change their shared unverified evidence rank.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/decisions/terminal-delegation-unverified-below-boundary.md § Terminal delegation is unverified below the documented boundary

The terminal support result supplies the category from its typed Supported
state: false is a known limit, null is an unavailable observation and true has
no unverified reason. Formatting never classifies localized reason text. Appx
query failures, unreadable terminal-support inputs and below-boundary terminal
results remain unverified evidence, but only failed observations are described
as undecided. Other Windows prerequisite presentation is outside this rule.
