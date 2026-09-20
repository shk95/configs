id: windows/selected-precondition-evaluated
statement: The check and Apply evaluate the preconditions of every selected feature and of no other, and no loop in a Windows script rebinds a parameter of the script block it runs in.
rationale: docs/policy/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

Found on 2026-09-20: the loop that evaluates preconditions iterated with
`$feature` under a `[string[]] $Feature` parameter. PowerShell names are
case-insensitive and a parameter keeps its type constraint, so every declared
feature became a string, no Id matched the selection, and no precondition was
evaluated from the change that added the parameter onward; the functions'
own fixtures passed throughout because they call the evaluator directly. The
check past the prerequisites needs a Windows host, so the fixture reads every
script of the domain for the collision and holds the loop to handing the
evaluator the item it iterates over. `windows/tools/setup.ps1` carries the
tag beside the loop, for the reader.
