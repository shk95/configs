id: unixlike/tool-supply-ownership
statement: The domain evaluator remains central to configuration and program supply, and each supplementary tool has one installation owner within its declared platform scope.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: schema unixlike/modules/foundation/program-supply/catalog.nix
enforced-by: schema unixlike/modules/flake/configurations.nix
enforced-by: fixture unixlike/tool/checks/programs-test
enforced-by: manual Unix-like maintainer review of platform, installation and configuration owners, version constraints, duplicate commands and native compatibility evidence
owner: Unix-like maintainer
decision: docs/policy/decisions/unixlike/tool-supply-separated-from-configuration.md § Tool supply is separate from configuration ownership

The review item is in the Unix-like definition of done. Homebrew's adopted
platform scope is macOS, supplementing Nix for rapid updates and temporary
installation and management. Linux uses Nix-supplied mise for selected coding agents. Other suppliers
are selected per platform and tool; no external manager is universally required. Settings can
remain evaluator-owned and version pinning is optional for supplementary tools. The existing package-ownership
check covers evaluator-supplied packages, not external installation state.
Review must not infer native execution from evaluation or package presence.

Program definitions supply stable IDs independently of their provider
identifiers. Platform support and required host classes bound program
selection. A requested selection with no eligible module class is refused.
