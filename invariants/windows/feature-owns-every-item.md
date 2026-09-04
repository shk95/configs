id: windows/feature-owns-every-item
statement: Every package, managed file, font, and delegation names exactly one declared feature.
rationale: docs/architecture.md § Windows domain
enforced-by: schema windows/src/WinEnv.psm1
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

An item without a feature could never be selected, and one naming an
undeclared feature would be dropped from every plan without saying so. The
loader refuses both when the manifest is read, so setup, the check tool and
the suite all see one validated model.
