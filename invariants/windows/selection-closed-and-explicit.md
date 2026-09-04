id: windows/selection-closed-and-explicit
statement: A host's feature selection is closed over the dependencies the manifest declares and refuses a feature the manifest does not declare.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/status.md § Windows authority split

A feature declares that it requires another when its payload cannot be
honest without it; a selection that dropped the requirement would deploy a
payload that names a program the host does not have. Closure is computed
from the manifest, reported as "added by dependency", and a dependency stays
selectable on its own. An unknown feature name is refused rather than
ignored, because a silently ignored selection is a host the operator
believes to be different from what it is. The fixtures hold closure, the
report, standalone selection, and the refusal.
