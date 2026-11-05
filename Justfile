# Unix-like operations grouped by work and effects. Use just --list.
# INV unixlike/provider-entry-boundary
# Host-changing utilities still require an explicit request (AGENTS.md).
default:
    @just --list

# Compatibility helpers never select a synthetic provider output as a host.
[private]
_provider-host-refusal:
    @echo 'This flake exports synthetic fixtures only. Use the host flake in configs-hosts.' >&2; exit 1

[private]
_home-target:
    @just _provider-host-refusal

[private]
_darwin-target:
    @just _provider-host-refusal

[private]
_nixos-target host="":
    @just _provider-host-refusal

[private]
_nixos-host:
    @just _provider-host-refusal

# Inspect the broader clone/host capability inventory.
[group('environment')]
doctor:
    tool/doctor.sh

# Run formatting, lint and the complete provider verification suite.
[group('provider-verification')]
check:
    unixlike/tool/checks/format
    unixlike/tool/checks/lint
    unixlike/tool/checks/test

# Check provider Nix formatting.
[group('provider-verification')]
format-check:
    unixlike/tool/checks/format

# Lint provider Nix source.
[group('provider-verification')]
lint:
    unixlike/tool/checks/lint

# Parse every declared Unix-like source payload with its own native tool.
[group('provider-verification')]
payloads:
    unixlike/tool/checks/payloads

# The same check plus the fixtures that prove it rejects what it must.
[group('provider-verification')]
payloads-test:
    unixlike/tool/checks/payloads-test

# Prove each Unix-like check reports a missing Nix as unverified, not failed.
[group('provider-verification')]
prerequisite-test:
    unixlike/tool/checks/prerequisite-test

# Prove the flake's typed identity and class composition refuse what they must.
[group('provider-verification')]
flake-test:
    unixlike/tool/checks/flake-test

# Prove a feature file names no host and forces no value, and that the check refuses one that does.
[group('provider-verification')]
composition-test:
    unixlike/tool/checks/composition-test

# Prove what the evaluation check reaches, refuses and builds.
[group('provider-verification')]
eval-coverage-test:
    unixlike/tool/checks/eval-coverage-test

# Compose every host in walk order and reversed; the toplevels must match.
[group('provider-verification')]
import-order:
    unixlike/tool/checks/import-order

# The same check plus the order-dependent pair it must refuse.
[group('provider-verification')]
import-order-test:
    unixlike/tool/checks/import-order-test

# Run provider contract, payload, tooling and synthetic composition checks.
[group('provider-verification')]
test:
    unixlike/tool/checks/test

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
home-eval:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
home-build:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
home-switch:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
home-bootstrap: home-switch

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
home-news:
    @just _provider-host-refusal

# List all home-manager generations
[group('host-observation')]
home-generations:
    home-manager generations

# Refresh provider inputs except explicitly documented exclusions
[group('provider-inputs')]
up:
    "{{justfile_directory()}}/unixlike/tool/refresh-inputs"

# Update one explicitly named provider input using Nix, e.g. just upp nixpkgs.
[group('provider-inputs')]
[positional-arguments]
upp input:
    #!/usr/bin/env bash
    set -euo pipefail
    case "$1" in
      ''|-*) echo 'upp requires one input name, not an option' >&2; exit 64 ;;
    esac
    nix flake update "$1" --flake {{ quote(justfile_directory() + "/unixlike") }}

# Format the nix code in this flake
[group('source-formatting')]
fmt:
    cd {{ quote(justfile_directory() + "/unixlike") }} && nix fmt .

# PROV unixlike/zellij-combining-marks
# Check that the zellij combining-marks patch applies with no fuzz: with no argument to the lock's zellij as nixpkgs builds it, or to an upstream tag, e.g. `just zellij-patch-check v0.45.1`.
[group('provider-verification')]
zellij-patch-check tag="":
    #!/usr/bin/env bash
    set -euo pipefail
    system=$(nix eval --raw --impure --expr builtins.currentSystem)
    check="path:./unixlike#checks.${system}.zellij-combining-marks"
    if [[ -z '{{ tag }}' ]]; then
      # The flake check itself: nixpkgs' source and patches, the range applied
      # by stdenv's patch phase with -F0, and the vendor Cargo.lock comparison.
      nix build --no-link "${check}"
      printf 'the pinned range applies with -F0 to the lock'\''s zellij %s\n' "$(nix eval --raw "${check}.version")"
      exit 0
    fi
    patch=$(nix build --no-link --print-out-paths "${check}.patch")
    gnupatch=$(nix build --no-link --print-out-paths --inputs-from path:./unixlike nixpkgs#gnupatch)
    work=$(mktemp -d)
    trap 'rm -rf "${work}"' EXIT
    git -c advice.detachedHead=false clone --quiet --depth 1 --branch '{{ tag }}' https://github.com/zellij-org/zellij "${work}/zellij"
    # A real apply in the throwaway clone, not --dry-run: the range patches
    # grid.rs three times, and a dry run never applies the earlier sections
    # the later ones build on. --forward refuses an already-applied hunk
    # instead of asking whether to reverse it.
    "${gnupatch}/bin/patch" -d "${work}/zellij" -p1 -F0 --forward --quiet -i "${patch}" </dev/null
    printf 'the pinned range applies with -F0 to %s\n' '{{ tag }}'

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
darwin-eval:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
darwin-build:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
darwin-check: darwin-eval darwin-build

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
darwin-bootstrap:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
darwin-switch:
    @just _provider-host-refusal

# List nix-darwin generations on an already configured Mac.
[group('host-observation')]
darwin-generations:
    darwin-rebuild --list-generations

# Compare this Mac's Karabiner file and symbolic hotkeys with the payloads.
[group('host-observation')]
karabiner-check:
    unixlike/modules/programs/karabiner/tool check

# Retired publication entry; use explicit pinned host-document preview/review/save.
[group('compatibility')]
karabiner-capture *args:
    @echo 'karabiner-capture is retired. Use the pinned preview/review/save workflow in unixlike/tool/darwin-capture/README.md with explicit host-owned document destinations; connect and publish them separately.' >&2; exit 1

# Prove the Karabiner projection tolerates runtime members and refuses drift.
[group('provider-verification')]
karabiner-test:
    unixlike/tool/checks/karabiner-test

# Garbage collect unused nix store entries older than 7 days
[group('host-maintenance')]
gc:
    nix-collect-garbage --delete-older-than 7d

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
nixos-eval host="":
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
nixos-build host="":
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
nixos-test:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
nixos-switch:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
nixos-rollback:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
nixos-generations:
    @just _provider-host-refusal

# Compatibility refusal: real hosts belong to configs-hosts.
[group('compatibility')]
nixos-tarball host="":
    @just _provider-host-refusal

# Copy the rootfs archive somewhere `wsl --import` will actually read it
[group('host-transfer')]
nixos-stage dest="/mnt/c/WSL":
    #!/usr/bin/env bash
    set -euo pipefail
    [ -f nixos.wsl ] || { echo "Supply a reviewed consumer-built ./nixos.wsl archive first." >&2; exit 1; }
    [ -d "$(dirname "{{ dest }}")" ] || { echo "{{ dest }} is not reachable — is that drive mounted?" >&2; exit 1; }
    mkdir -p "{{ dest }}"
    cp nixos.wsl "{{ dest }}/nixos.wsl"
    gzip -t "{{ dest }}/nixos.wsl"
    win=$(printf '%s' "{{ dest }}/nixos.wsl" | sed 's|^/mnt/\([a-z]\)|\U\1:|; s|/|\\|g')
    echo
    echo "Staged and verified. From PowerShell or CMD — not from in here:"
    echo
    echo "  wsl --import NixOS C:\\WSL\\NixOS $win"
    echo
    echo "Then follow the consumer's reviewed installation procedure: the"
    echo "account is created locked, and ssh needs an authorized_keys copied in."
    echo
    echo "That registers a NEW distribution. Ubuntu is untouched;"
    echo "rollback is: wsl --unregister NixOS"

# Change the login shell, registering it if needed; refused on NixOS.
[group('host-maintenance')]
switch-shell:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ -e /etc/NIXOS ]; then
      echo "NixOS selects the login shell in unixlike/modules/foundation/shell/wsl.nix; nothing to switch here." >&2
      exit 1
    fi

    case "$(uname -s)" in
      # Registered in /etc/shells by unixlike/modules/foundation/shell/darwin.nix; the store path
      # behind it changes with every zsh update, this one does not.
      Darwin) TARGET_SHELL="/run/current-system/sw/bin/zsh" ;;
      # The standalone Home Manager profile.
      *)      TARGET_SHELL="$HOME/.nix-profile/bin/zsh" ;;
    esac

    if [ ! -x "$TARGET_SHELL" ]; then
      echo "$TARGET_SHELL does not exist yet; activate the home (or the Darwin system) first." >&2
      exit 1
    fi

    if [ "$SHELL" = "$TARGET_SHELL" ]; then
      echo "Current shell is already $TARGET_SHELL"
      exit 0
    fi

    if ! grep -Fxq "$TARGET_SHELL" /etc/shells; then
      echo "Registering $TARGET_SHELL in /etc/shells (needs sudo)"
      echo "$TARGET_SHELL" | sudo tee -a /etc/shells
    fi

    chsh -s "$TARGET_SHELL"
    echo "Login shell updated. Restart the WSL terminal for it to take effect."

# Write the local consumer checkout/host connection in Git metadata.
[group('consumer-development')]
dev-connect consumer host:
    @unixlike/tool/dev-host/run connect {{ quote(consumer) }} {{ quote(host) }}

# Disconnect local consumer development.
[group('consumer-development')]
dev-disconnect:
    @unixlike/tool/dev-host/run disconnect

# Read development state without initializing a session.
[group('consumer-development')]
dev-info:
    @unixlike/tool/dev-host/run info

# Write a local development recipe from the supplied file.
[group('consumer-development')]
dev-configure recipe:
    @unixlike/tool/dev-host/run configure {{ quote(recipe) }}

# Evaluate the connected consumer using the local provider.
[group('consumer-development')]
[positional-arguments]
dev-eval *args:
    @unixlike/tool/dev-host/run eval "$@"

# Build the connected consumer using the local provider.
[group('consumer-development')]
[positional-arguments]
dev-build *args:
    @unixlike/tool/dev-host/run build "$@"

# Explicit activation of the connected consumer using the local provider.
[group('consumer-development')]
dev-apply:
    @unixlike/tool/dev-host/run apply

# Verify the connected consumer using the local provider.
[group('consumer-development')]
[positional-arguments]
dev-verify *args:
    @unixlike/tool/dev-host/run verify "$@"

# Review with --plan; execute/resume the reviewed publication with --execute.
[group('consumer-development')]
[positional-arguments]
dev-promote *args:
    @unixlike/tool/dev-host/run promote "$@"

# Compatibility aliases retain their destinations.
alias bootstrap := home-bootstrap
alias build := home-build
alias switch := home-switch
alias news := home-news
alias generations := home-generations
