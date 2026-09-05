id: windows/entry-point-forwards-status
statement: The Windows entry point runs exactly one existing script for each verb and returns that script's exit status unchanged, and refuses a verb it does not know with a status no check outcome uses.
rationale: AGENTS.md § Governance design
enforced-by: fixture windows/tests/WinEnv.Tests.ps1
decision: docs/decisions/windows-entry-point-in-domain.md § The Windows entry point is one script inside the domain

The entry point exists so the domain reads as one tool rather than a
collection of scripts, and it is held to adding nothing: a verb is a name
for a script and its fixed named arguments, the rest of the command line
reaches the script as typed, and the status the operator sees is the
script's. The fixtures run the real file in a child shell with no
prerequisite reachable, where a forwarded check can only end at 69, so an
unknown verb's 64 proves both the refusal and that nothing ran; they also
hold that a script refusing its arguments ends the run at 1 rather than
letting a non-terminating binding error fall through as 0, and that every
verb names a file that exists under the tools directory and ends in an
explicit exit, because a script run in-process that falls off its end
leaves the status at whatever its last child process set. The usage status
is 64 because 2 is drift and 69 is unverified.
