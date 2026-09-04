id: windows/font-state-total
statement: A font on a host is in exactly one of the declared install states, and a state that could only be finished by overwriting a file or registration this repository did not write is a conflict, never a repair.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/status.md § Font install states

The states form a partition so the check and Apply can branch on them in
any order; a host that satisfied two would be acted on twice. The decision
record explains the fifth state, `Incomplete`, and the rule that bounds the
two states that write: nothing on this path overwrites a file or a
registration the repository did not put there, so a present file whose
bytes are not the pinned ones and a registration naming another path are
conflicts, not repairs. The fixtures inject the three host observations the
status function reads and hold the partition across six hosts, the
incomplete-not-conflict shape that caused the original regression, the
foreign file, and the foreign registration.
