id: windows/external-profile-blocks-preserved
statement: Writing the managed profile block preserves every block another owner placed in the same file and refuses a file whose markers do not pair.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

The profile file is host state more than one owner writes: a monitoring
agent, a package manager, and this repository each keep a region there. The
writer therefore edits only its own marked region, and a file whose markers
do not pair is refused rather than guessed at, because the guess would
overwrite someone else's block. The fixture writes a foreign region, runs the
writer twice, and holds both the single managed region and the foreign one;
its negative case is a lone opening marker. `AGENTS.md` states the same rule
for a session editing the file by hand ("Preserve externally managed
PowerShell profile blocks"); that row stays `none`, since this fixture holds
the domain's writer, not an agent. The same `Describe` carries a regression
guard that the committed profile is silent in a non-interactive process; it
proves no rule and names no invariant.
