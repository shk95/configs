# List all the just commands
default:
    @just --list

[private]
_home-target:
    @nix eval --raw path:.#homeConfigurations --apply 'configs: let names = builtins.attrNames configs; in assert builtins.length names == 1; builtins.head names'

[private]
_darwin-target:
    @nix eval --raw path:.#darwinConfigurations --apply 'configs: let names = builtins.attrNames configs; in assert builtins.length names == 1; builtins.head names'

############################################################################
#
#  repository checks
#
############################################################################

[group('repository')]
doctor:
    tool/doctor.sh

# Run formatting, lint, payload parsing, and evaluation/native-build coverage.
[group('repository')]
check:
    tool/checks/format
    tool/checks/lint
    tool/checks/payloads
    tool/checks/test

[group('repository')]
format-check:
    tool/checks/format

[group('repository')]
lint:
    tool/checks/lint

# Parse every declared Unix-like source payload with its own native tool.
[group('repository')]
payloads:
    tool/checks/payloads

# The same check plus the fixtures that prove it rejects what it must.
[group('repository')]
payloads-test:
    tool/checks/payloads-test

# Prove each Unix-like check reports a missing Nix as unverified, not failed.
[group('repository')]
prerequisite-test:
    tool/checks/prerequisite-test

# Prove the flake's typed identity and class composition refuse what they must.
[group('repository')]
flake-test:
    tool/checks/flake-test

# Prove a feature file names no host and forces no value, and that the check refuses one that does.
[group('repository')]
composition-test:
    tool/checks/composition-test

# Prove the evaluation check fails when it reaches no configuration.
[group('repository')]
eval-coverage-test:
    tool/checks/eval-coverage-test

# Compose every host in walk order and reversed; the toplevels must match.
[group('repository')]
import-order:
    tool/checks/import-order

# The same check plus the order-dependent pair it must refuse.
[group('repository')]
import-order-test:
    tool/checks/import-order-test

[group('repository')]
test:
    tool/checks/test

############################################################################
#
#  standalone home-manager (Ubuntu WSL)
#
############################################################################

# Evaluate without building or activating.
[group('home-manager')]
home-eval:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _home-target)
    drv=$(nix eval --raw "path:.#homeConfigurations.${target}.activationPackage.drvPath")
    printf '%s\n' "${drv}"

# Build the standalone Home Manager generation without activating it.
[group('home-manager')]
home-build:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _home-target)
    nix build --no-link --print-out-paths "path:.#homeConfigurations.${target}.activationPackage"

# Activation: run only on the intended Ubuntu WSL host.
[group('home-manager')]
home-switch:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _home-target)
    generation=$(nix build --no-link --print-out-paths "path:.#homeConfigurations.${target}.activationPackage")
    "${generation}/activate"

# First activation without requiring a pre-existing home-manager command.
[group('home-manager')]
home-bootstrap: home-switch

# Show news for the standalone Home Manager configuration.
[group('home-manager')]
home-news:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _home-target)
    home-manager news --flake "path:.#${target}"

# List all home-manager generations
[group('home-manager')]
home-generations:
    home-manager generations

# Compatibility names for the previous standalone Home Manager commands.
alias bootstrap := home-bootstrap
alias build := home-build
alias switch := home-switch
alias news := home-news
alias generations := home-generations

############################################################################
#
#  nix
#
############################################################################

# Update all the flake inputs
[group('nix')]
up:
    nix flake update

# Update a single input, e.g. `just upp nixpkgs`
[group('nix')]
upp input:
    nix flake update {{ input }}

# Format the nix code in this flake
[group('nix')]
fmt:
    nix fmt .

############################################################################
#
#  nix-darwin
#
############################################################################

# Evaluate the Darwin toplevel without building or activating.
[group('darwin')]
darwin-eval:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _darwin-target)
    drv=$(nix eval --raw "path:.#darwinConfigurations.${target}.config.system.build.toplevel.drvPath")
    printf '%s\n' "${drv}"

# Build the Darwin system without creating a result symlink or activating it.
[group('darwin')]
darwin-build:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _darwin-target)
    nix build --no-link --print-out-paths "path:.#darwinConfigurations.${target}.config.system.build.toplevel"

# Evaluate and natively build the Darwin system without activating it.
[group('darwin')]
darwin-check: darwin-eval darwin-build

# First Darwin activation without requiring an installed darwin-rebuild.
[group('darwin')]
darwin-bootstrap:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _darwin-target)
    system=$(nix build --no-link --print-out-paths "path:.#darwinConfigurations.${target}.config.system.build.toplevel")
    sudo "${system}/sw/bin/darwin-rebuild" switch --flake "path:.#${target}"

# Rebuild and activate the target Mac.
[group('darwin')]
darwin-switch:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _darwin-target)
    sudo darwin-rebuild switch --flake "path:.#${target}"

# List nix-darwin generations on an already configured Mac.
[group('darwin')]
darwin-generations:
    darwin-rebuild --list-generations

# Garbage collect unused nix store entries older than 7 days
[group('nix')]
gc:
    nix-collect-garbage --delete-older-than 7d

############################################################################
#
#  nixos-wsl  (M3 experiment)
#
############################################################################

# `tool/checks/test` skips this build by default, because nothing on a
# non-NixOS host can activate the result. This is the deliberate way to ask
# for it; `CHECKS_BUILD_ALL=1 tool/checks/test` is the other.

# Build the NixOS-WSL closure (~1.9 GiB)
[group('nixos-wsl')]
nixos-build:
    nix build --no-link --print-out-paths path:.#nixosConfigurations.wsl.config.system.build.toplevel

# NixOS-WSL's builder refuses to run unless EUID is 0 — it chowns paths inside
# the rootfs it assembles — so this needs a password and an agent cannot run
# it. It takes several minutes, because it runs a real `nixos-install` into a
# temporary root before archiving it.
#
# The output path is passed explicitly rather than left to the builder's
# default, which is `nixos.wsl` relative to whatever the cwd happens to be. It
# lands in the repo root and is gitignored; it is owned by root, so removing it
# needs sudo as well.

# Produce the rootfs archive that `wsl --import` takes (needs sudo)
[group('nixos-wsl')]
nixos-tarball:
    sudo $(nix build --no-link --print-out-paths path:.#nixosConfigurations.wsl.config.system.build.tarballBuilder)/bin/nixos-wsl-tarball-builder nixos.wsl
    @echo
    @echo "Wrote ./nixos.wsl (root-owned, gitignored). Now run: just nixos-stage"

# `wsl --import` will not take a UNC source path. `\\wsl.localhost\...` reads
# perfectly from `dir`, so it is not a permissions or 9p problem — the importer
# specifically does not accept one, and the failure does not say so. Copying the
# image onto a real Windows drive first is what makes the path plain and the
# command work. About four seconds over drvfs, not the minute you would expect.

# Copy the rootfs archive somewhere `wsl --import` will actually read it
[group('nixos-wsl')]
nixos-stage dest="/mnt/c/WSL":
    #!/usr/bin/env bash
    set -euo pipefail
    [ -f nixos.wsl ] || { echo "No ./nixos.wsl — run 'just nixos-tarball' first." >&2; exit 1; }
    [ -d "$(dirname "{{ dest }}")" ] || { echo "{{ dest }} is not reachable — is that drive mounted?" >&2; exit 1; }
    mkdir -p "{{ dest }}"
    cp nixos.wsl "{{ dest }}/nixos.wsl"
    gzip -t "{{ dest }}/nixos.wsl"
    win=$(printf '%s' "{{ dest }}/nixos.wsl" | sed 's|^/mnt/\([a-z]\)|\U\1:|; s|/|\\|g')
    echo
    echo "Staged and verified. From PowerShell or CMD — not from in here:"
    echo
    echo "  wsl --import NixOS C:\\WSL\\NixOS $win"
    echo "  wsl -d NixOS"
    echo
    echo "That registers a NEW distribution. Ubuntu is untouched;"
    echo "rollback is: wsl --unregister NixOS"

############################################################################
#
#  setup
#
############################################################################

# Make the home-manager-managed zsh the login shell
[group('setup')]
switch-shell:
    #!/usr/bin/env bash
    set -euo pipefail

    TARGET_SHELL="$HOME/.nix-profile/bin/zsh"

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
