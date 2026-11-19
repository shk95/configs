# Tool supply is separate from configuration ownership

date: 2026-11-14
scope: unixlike
status: accepted
reopen-when: A chosen supplier cannot safely provide a required tool or maintained settings cannot be separated from its installation lifecycle.

Nix manages the environment, including settings for programs installed by
supplementary suppliers. Homebrew on macOS and mise for selected Linux tools
let application updates follow the supplier's releases. Version constraints
are optional. A configuration rollback cannot revert an external program
update, so supplier changes need an explicit installation owner, duplicate
command checks, and native compatibility evidence.

A program's stable ID, settings, supported platforms, and supplier choices
live in one module. The first directory under `modules/programs/` names the
host selection group. Environment profiles set defaults. Host group choices
and individual choices override those defaults in that order, subject to
platform eligibility and available native classes. Deployment remains a
property of the declaration and effective supply.

Darwin's reusable formulae and casks belong to the provider. The consumer
owns the App Store choices, `mas`, Homebrew preparation, and lifecycle.
Actual package and cask declarations determine inventory and the settings
tied to their presence. Existing session integration owns its dependent
components.

Supported Linux homes use Nix-supplied mise for Claude Code and Codex.
macOS keeps their Nix packages. Nix owns their mise configuration fragment,
while local tool configuration stays writable. Configuration application
installs missing requests. Updates use `mise upgrade --global` explicitly,
and old versions are retained. SDKMAN keeps its existing ownership and shell
order.

The ownership and compatibility contract is in
[Tool supply and configuration](../../architecture.md#tool-supply-and-configuration).
