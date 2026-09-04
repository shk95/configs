# Decision records

One file per decision that is expensive to reverse or that a reviewer will
ask about. `docs/status.md` holds current state and links here;
`docs/architecture.md` holds the model; a record holds one choice, why it
was made, what was rejected, and what it costs. A record is cited by path
(`docs/decisions/<slug>.md`); a registry entry cites it as
`decision: docs/decisions/<slug>.md § <Title>`, which
`tool/version-control/invariants` checks (rule C4).

## Format

Line 1 is `# <Title>`, the text a registry pointer names. Then a header of
`key: value` lines up to the first blank line, parsed the way registry
entries are (`invariants/README.md`); a list is a repeated key. Then prose.

| Key | Count | Meaning |
|---|---|---|
| `date` | 1 | `YYYY-MM-DD` of the decision; later elaborations carry their own date in prose. |
| `scope` | 1+ | `unixlike`, `windows`, `repository` or `common`; repeated for a decision spanning domains; a record with two scopes lists both in the index, comma-separated. |
| `status` | 1 | `accepted` or `superseded`. |
| `issue` | 0+ | `#<n>`. |
| `reopen-when` | 0–1 | One sentence naming the condition under which the decision is revisited. |
| `supersedes`, `superseded-by` | 0–1 each | A record path. |
| `source` | 0+ | Provenance of an extracted record, `<commit>:<path> § <heading>`; never checked. |

Extending or correcting a decision edits its record and appends a dated
paragraph. Reversing one creates a new record, sets the old one to
`status: superseded` with `superseded-by`, and moves every `decision:`
pointer in the same commit, because the checker cannot tell a superseded
record from a live one. Prose and code cite a record by path only; a quoted
heading is checked by nothing and rots. `CONTRIBUTING.md § Record a
decision` is the procedure.

## Index

| Date | Scope | Title | Status | Record |
|---|---|---|---|---|
| 2026-08-11 | repository | The monorepo starts a clean history | accepted | monorepo-starts-clean-history.md |
| 2026-08-12 | unixlike | Home Manager platform classes are overlays | accepted | home-manager-platform-classes.md |
| 2026-08-12 | unixlike | Homebrew owns Mac App Store and macOS GUI applications | accepted | homebrew-owns-mac-apps.md |
| 2026-08-12 | unixlike | The identity contract and its values are separate | accepted | identity-contract-values-separated.md |
| 2026-08-13 | unixlike, windows | PowerShell is configured per domain by copying | accepted | powershell-copied-per-domain.md |
| 2026-08-16 | unixlike | SDKMAN is adopted but not owned | accepted | sdkman-adopted-not-owned.md |
| 2026-08-16 | unixlike | Every payload declares its format and is parsed | accepted | payloads-declared-and-parsed.md |
| 2026-08-16 | repository | A check reports verified, failed or unverified | accepted | check-evidence-three-states.md |
| 2026-08-16 | repository | CI runs the suites and adds no hosted runner | accepted | ci-evidence-without-hosted-runners.md |
| 2026-08-18 | windows | Feature selection is closed over declared dependencies | accepted | feature-selection-closed.md |
| 2026-08-30 | windows | Windows adopts Catppuccin Latte by copying | accepted | windows-adopts-catppuccin-latte.md |
| 2026-08-30 | windows | Windows Terminal's generated profiles are tolerated on read | accepted | terminal-generated-profiles-tolerated.md |
| 2026-08-30 | windows | Font install states | accepted | font-install-states.md |
| 2026-08-30 | windows | Terminal delegation is unverified below the documented boundary | accepted | terminal-delegation-unverified-below-boundary.md |
| 2026-08-30 | windows | Undecidable Appx detection is unverified, not absent | accepted | appx-detection-unverified-not-absent.md |
| 2026-08-30 | windows | `.wslconfig` content is selected by the host's Windows build | accepted | wslconfig-selected-by-windows-build.md |
| 2026-08-30 | windows | Drift outranks unverified in the check exit status | accepted | drift-outranks-unverified.md |
| 2026-08-30 | windows | Capture moves a host change into desired state | accepted | capture-moves-host-changes.md |
| 2026-08-30 | windows | Capture restores exactly one placeholder | accepted | capture-restores-one-placeholder.md |
| 2026-08-30 | repository | The hygiene tool owns desired-state hygiene | accepted | hygiene-tool-owns-enforcement.md |
| 2026-08-31 | windows | Windows checks run only under the host's own pwsh | accepted | windows-checks-run-under-native-pwsh.md |
| 2026-08-31 | windows | A JsonSubset payload is captured by projection | accepted | jsonsubset-captured-by-projection.md |
| 2026-08-31 | repository | Hooks run under Git for Windows | accepted | hooks-run-under-git-for-windows.md |
| 2026-09-03 | unixlike | A package is owned by the module that configures it | accepted | package-ownership-by-generating-module.md |
| 2026-09-03 | repository | The invariant registry is created with pending entries | accepted | invariant-registry-created.md |
| 2026-09-04 | repository | A fixture tag names only an invariant its case proves | accepted | fixture-tags-name-proven-invariants.md |
| 2026-09-04 | repository | The local gate selects checks by effect | accepted | local-gate-selects-by-effect.md |
