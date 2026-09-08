id: windows/capture-source-policy
statement: Capturing a build-selected host configuration validates its modelled key, section and application prerequisites before accepting unchanged content, preserves the selected source's network policy, and refuses unsupported or undetermined prerequisites without writing either source.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WslConfig.Tests.ps1
decision: docs/decisions/wslconfig-selected-by-windows-build.md § `.wslconfig` content is selected by the host's Windows build

Selecting a destination by build does not prove that host content belongs in
it. The selected payload owns its network policy; changing that policy is a
reviewed desired-state edit, not a side effect of capturing host tuning.
Unmodelled keys are reported separately and preserved; a documented inactive
dependency is explained without deleting content or claiming runtime evidence.
