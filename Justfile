# List all the just commands
default:
    @just --list

[private]
_home-target:
    @nix eval --raw path:./unixlike#homeConfigurations --apply 'configs: let names = builtins.attrNames configs; in assert builtins.length names == 1; builtins.head names'

[private]
_darwin-target:
    @nix eval --raw path:./unixlike#darwinConfigurations --apply 'configs: let names = builtins.attrNames configs; in assert builtins.length names == 1; builtins.head names'

# The flake exports one NixOS output per host of the typed inventory
# (unixlike/modules/flake/inventory.nix), so a recipe names the host it means.
# Prints the name when the flake exports it; refuses, listing the names it
# does export, when it does not or when none was given.
[private]
_nixos-target host="":
    #!/usr/bin/env bash
    set -euo pipefail
    host={{ quote(host) }}
    names=$(nix eval --raw path:./unixlike#nixosConfigurations --apply 'configs: builtins.concatStringsSep " " (builtins.attrNames configs)')
    for name in ${names}; do
      if [ "${name}" = "${host}" ]; then
        printf '%s\n' "${name}"
        exit 0
      fi
    done
    if [ -z "${host}" ]; then
      echo "Name the NixOS host: ${names}." >&2
    else
      echo "The flake exports no NixOS host '${host}'. It exports: ${names}." >&2
    fi
    exit 1

# The recipes that touch a NixOS system act on the output named after the
# host they run on, and on no other: a rebuild under another name would
# activate, or list, another machine's system. Prints the target for the
# caller.
[private]
_nixos-host:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -e /etc/NIXOS ]; then
      echo "This host is not NixOS (/etc/NIXOS is absent); the nixos-* recipes that rebuild, roll back or list generations run inside the NixOS distribution. 'just nixos-eval <host>' and 'just nixos-build <host>' run anywhere." >&2
      exit 1
    fi
    host=$(cat /proc/sys/kernel/hostname)
    if ! target=$(just _nixos-target "${host}"); then
      echo "This NixOS host is '${host}'; refusing to act on another host's system." >&2
      exit 1
    fi
    printf '%s\n' "${target}"

############################################################################
#
#  repository checks
#
############################################################################

[group('repository')]
doctor:
    tool/doctor.sh

# Run formatting, lint, payload parsing, and evaluation/native-build coverage.
# The checks a change needs; the fixtures that prove each check refuses what it
# must have recipes of their own below and run in CI.
[group('repository')]
check:
    unixlike/tool/checks/format
    unixlike/tool/checks/lint
    unixlike/tool/checks/payloads
    unixlike/tool/checks/test

[group('repository')]
format-check:
    unixlike/tool/checks/format

[group('repository')]
lint:
    unixlike/tool/checks/lint

# Parse every declared Unix-like source payload with its own native tool.
[group('repository')]
payloads:
    unixlike/tool/checks/payloads

# The same check plus the fixtures that prove it rejects what it must.
[group('repository')]
payloads-test:
    unixlike/tool/checks/payloads-test

# Prove each Unix-like check reports a missing Nix as unverified, not failed.
[group('repository')]
prerequisite-test:
    unixlike/tool/checks/prerequisite-test

# Prove the flake's typed identity and class composition refuse what they must.
[group('repository')]
flake-test:
    unixlike/tool/checks/flake-test

# Prove a feature file names no host and forces no value, and that the check refuses one that does.
[group('repository')]
composition-test:
    unixlike/tool/checks/composition-test

# Prove what the evaluation check reaches, refuses and builds.
[group('repository')]
eval-coverage-test:
    unixlike/tool/checks/eval-coverage-test

# Compose every host in walk order and reversed; the toplevels must match.
[group('repository')]
import-order:
    unixlike/tool/checks/import-order

# The same check plus the order-dependent pair it must refuse.
[group('repository')]
import-order-test:
    unixlike/tool/checks/import-order-test

[group('repository')]
test:
    unixlike/tool/checks/test

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
    drv=$(nix eval --raw "path:./unixlike#homeConfigurations.${target}.activationPackage.drvPath")
    printf '%s\n' "${drv}"

# Build the standalone Home Manager generation without activating it.
[group('home-manager')]
home-build:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _home-target)
    nix build --no-link --print-out-paths "path:./unixlike#homeConfigurations.${target}.activationPackage"

# NixOS composes its home into the system, so the standalone home is refused
# there; 'just nixos-switch' is that host's activation.

# Activation: run only on the intended Ubuntu WSL host; refused on NixOS.
[group('home-manager')]
home-switch:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -e /etc/NIXOS ]; then
      echo "NixOS composes Home Manager into the system; activating the standalone home here would put the Ubuntu home over it. Use 'just nixos-switch'." >&2
      exit 1
    fi
    target=$(just _home-target)
    generation=$(nix build --no-link --print-out-paths "path:./unixlike#homeConfigurations.${target}.activationPackage")
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
    home-manager news --flake "path:./unixlike#${target}"

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

# PROV unixlike/zellij-combining-marks
# Check that the zellij combining-marks patch applies with no fuzz: with no argument to the lock's zellij as nixpkgs builds it, or to an upstream tag, e.g. `just zellij-patch-check v0.45.1`.
[group('nix')]
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
    drv=$(nix eval --raw "path:./unixlike#darwinConfigurations.${target}.config.system.build.toplevel.drvPath")
    printf '%s\n' "${drv}"

# Build the Darwin system without creating a result symlink or activating it.
[group('darwin')]
darwin-build:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _darwin-target)
    nix build --no-link --print-out-paths "path:./unixlike#darwinConfigurations.${target}.config.system.build.toplevel"

# Evaluate and natively build the Darwin system without activating it.
[group('darwin')]
darwin-check: darwin-eval darwin-build

# First Darwin activation without requiring an installed darwin-rebuild.
[group('darwin')]
darwin-bootstrap:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _darwin-target)
    system=$(nix build --no-link --print-out-paths "path:./unixlike#darwinConfigurations.${target}.config.system.build.toplevel")
    sudo "${system}/sw/bin/darwin-rebuild" switch --flake "path:./unixlike#${target}"

# Rebuild and activate the target Mac.
[group('darwin')]
darwin-switch:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _darwin-target)
    sudo darwin-rebuild switch --flake "path:./unixlike#${target}"

# List nix-darwin generations on an already configured Mac.
[group('darwin')]
darwin-generations:
    darwin-rebuild --list-generations

# Compare this Mac's Karabiner file and symbolic hotkeys with the payloads.
[group('darwin')]
karabiner-check:
    unixlike/modules/programs/karabiner/tool check

# Read this Mac's Karabiner drift back into the payloads and commit it.
[group('darwin')]
karabiner-capture *args:
    tool/version-control/commit {{args}} capture karabiner

# Prove the Karabiner projection tolerates runtime members and refuses drift.
[group('darwin')]
karabiner-test:
    unixlike/tool/checks/karabiner-test

# Garbage collect unused nix store entries older than 7 days
[group('nix')]
gc:
    nix-collect-garbage --delete-older-than 7d

############################################################################
#
#  nixos
#
############################################################################

# Evaluate a NixOS host's toplevel without building or activating. Runs anywhere.
[group('nixos')]
nixos-eval host="":
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _nixos-target {{ quote(host) }})
    drv=$(nix eval --raw "path:./unixlike#nixosConfigurations.${target}.config.system.build.toplevel.drvPath")
    printf '%s\n' "${drv}"

# `unixlike/tool/checks/test` builds a NixOS output only on the host it names,
# because nothing anywhere else can activate the result. This is the
# deliberate way to ask for it; `CHECKS_BUILD_ALL=1 unixlike/tool/checks/test`
# is the other. An aarch64 host builds natively or on a remote builder, never
# under emulation (unixlike/modules/flake/systems.nix).

# Build a NixOS host's closure (the NixOS-WSL one is ~1.9 GiB)
[group('nixos')]
nixos-build host="":
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _nixos-target {{ quote(host) }})
    nix build --no-link --print-out-paths "path:./unixlike#nixosConfigurations.${target}.config.system.build.toplevel"

# Write a reviewable wrapper flake for one explicit persistent disk. This
# writes only the named plan directory and never touches the target device.
[group('nixos')]
nixos-install-plan host disk plan:
    unixlike/tool/install-plan {{ quote(host) }} {{ quote(disk) }} {{ quote(plan) }}

# Run the same disko installation proof that nixos-anywhere --vm-test selects,
# then boot the installed result on disposable QEMU disks. The portable form
# lets QEMU fall back to TCG when the builder has no nested KVM; it never
# connects to or activates a real host.
[group('nixos')]
nixos-install-vm-test host="":
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _nixos-target {{ quote(host) }})
    unixlike/tool/install-vm-test "${target}"

# NixOS-WSL's builder refuses to run unless EUID is 0 — it chowns paths inside
# the rootfs it assembles — so this needs a password and an agent cannot run
# it. It takes several minutes, because it runs a real `nixos-install` into a
# temporary root before archiving it.
#
# The output path is passed explicitly rather than left to the builder's
# default, which is `nixos.wsl` relative to whatever the cwd happens to be. It
# lands in the repo root and is gitignored; it is owned by root, so removing it
# needs sudo as well.

# The registered distribution is updated in place, from a clone inside it:
# build and activate without touching the boot profile, then switch. WSL has
# no boot loader, so a rollback is a switch to the previous generation, and it
# is possible only while that generation is inside the garbage collector's
# window (unixlike/modules/foundation/nix/shared.nix). CONTRIBUTING.md, "Update the
# registered NixOS-WSL distribution", is the procedure.

# Build and activate the NixOS system without making it the boot default.
[group('nixos')]
nixos-test:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _nixos-host)
    sudo nixos-rebuild test --flake "path:./unixlike#${target}"

# Activation: rebuild and switch the NixOS host this clone sits on.
[group('nixos')]
nixos-switch:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _nixos-host)
    sudo nixos-rebuild switch --flake "path:./unixlike#${target}"

# Activation: switch back to the previous NixOS generation.
[group('nixos')]
nixos-rollback:
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _nixos-host)
    sudo nixos-rebuild switch --rollback --flake "path:./unixlike#${target}"

# List the NixOS system generations on this host.
[group('nixos')]
nixos-generations:
    #!/usr/bin/env bash
    set -euo pipefail
    just _nixos-host >/dev/null
    nixos-rebuild list-generations

# Produce the rootfs archive that `wsl --import` takes (needs sudo)
[group('nixos-wsl')]
nixos-tarball host="":
    #!/usr/bin/env bash
    set -euo pipefail
    target=$(just _nixos-target {{ quote(host) }})
    kind=$(nix eval --raw "path:./unixlike#nixosConfigurations.${target}.config.host.kind")
    if [ "${kind}" != wsl ]; then
      echo "'${target}' is a host of kind ${kind}; only a host of kind wsl has a WSL rootfs archive." >&2
      exit 1
    fi
    builder=$(nix build --no-link --print-out-paths "path:./unixlike#nixosConfigurations.${target}.config.system.build.tarballBuilder")
    sudo "${builder}/bin/nixos-wsl-tarball-builder" nixos.wsl
    echo
    echo "Wrote ./nixos.wsl (root-owned, gitignored). Now run: just nixos-stage"

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
    [ -f nixos.wsl ] || { echo "No ./nixos.wsl — run 'just nixos-tarball <host>' first." >&2; exit 1; }
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
    echo "Then follow CONTRIBUTING.md § Import the NixOS-WSL distribution: the"
    echo "account is created locked, and ssh needs an authorized_keys copied in."
    echo
    echo "That registers a NEW distribution. Ubuntu is untouched;"
    echo "rollback is: wsl --unregister NixOS"

############################################################################
#
#  setup
#
############################################################################

# Make the Home Manager zsh the login shell — standalone Ubuntu and Darwin.
# NixOS selects it declaratively (unixlike/modules/foundation/shell/wsl.nix) and is refused here.
[group('setup')]
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
