#!/bin/sh
#
# Checks this machine can work in a requested scope and says plainly what is
# missing. Foreign-domain capabilities do not block a scoped change.
#
# Run it at the start of a session. The failure it exists to prevent is the
# quiet one: a clone with no git hooks commits without a secret scan, and a
# machine with flakes disabled fails every command in a way that looks like a
# broken flake rather than a missing setting.

cd "$(dirname "$0")/.." || exit 1

scope=${1:-all}
case "$scope" in
  all|unixlike|windows|common|repository) ;;
  *)
    echo "usage: tool/doctor.sh [unixlike|windows|common|repository]" >&2
    exit 2
    ;;
esac

red='\033[31m'; yellow='\033[33m'; green='\033[32m'; dim='\033[2m'; off='\033[0m'
failed=0

ok()   { printf "  ${green}✓${off} %s\n" "$1"; }
warn() { printf "  ${yellow}!${off} %s\n     ${dim}%s${off}\n" "$1" "$2"; }
bad()  { printf "  ${red}✗${off} %s\n     ${dim}%s${off}\n" "$1" "$2"; failed=1; }

echo "Toolchain ($scope)"

if [ "$scope" = all ] || [ "$scope" = unixlike ]; then
  if command -v nix >/dev/null 2>&1; then
    ok "nix $(nix --version | awk '{print $NF}')"
  else
    bad "nix not on PATH" "Install it: https://docs.determinate.systems (recommended on WSL) or https://nixos.org/download/"
  fi

# `nix config show` needs nix-command itself to inspect nix-command, so it
# cannot tell you whether nix-command is enabled. Asking the flake in this
# repository to resolve its own metadata tests both flags at once, the way
# every other command here actually needs them.
#
# The error is kept rather than discarded. Every other way this probe can fail
# — no network, an untracked flake.nix, a read-only ~/.cache/nix — used to be
# reported as "flakes are not enabled", which sends you to export a variable
# that cannot help. Not knowing is its own answer, and it stays a ✗ because the
# question being asked is whether this machine can build.
  if command -v nix >/dev/null 2>&1; then
    if err=$(nix flake metadata --no-write-lock-file 2>&1 >/dev/null); then
      ok "nix-command and flakes enabled"
    else
      case "$err" in
        *"experimental Nix feature"*)
          bad "nix-command/flakes not enabled by default" \
              'export NIX_CONFIG="experimental-features = nix-command flakes" until the first home-manager switch writes it for you (see modules/nix-conf.nix)'
          ;;
        *)
          detail=$(printf '%s\n' "$err" \
                   | grep -v '^[[:space:]]*$' \
                   | tail -1 \
                   | sed 's/^[[:space:]]*//' \
                   | cut -c1-200)
          bad "could not ask the flake whether nix-command works" \
              "Not the experimental-features flag, so exporting NIX_CONFIG will not help. $detail"
          ;;
      esac
    fi
  fi

  command -v direnv >/dev/null 2>&1 && ok "direnv" \
    || warn "direnv not installed" "Optional. programs.direnv expects it once you switch; install via your OS package manager."
else
  ok "Unix-like toolchain is not required for the $scope scope"
fi

if [ "$scope" = windows ] || [ "$scope" = all ]; then
  # Only `pwsh.exe`, matching .githooks/pre-push. A Unix-like `pwsh` is present
  # in every home this repository configures, so accepting it here would report
  # a capability the hook does not agree exists.
  if command -v pwsh.exe >/dev/null 2>&1; then
    ok "native pwsh.exe available for Windows checks"
  else
    # Not a failure even when the scope is windows. Windows work is authored on
    # Linux and macOS clones, and the windows-latest CI job is its merge gate.
    warn "native PowerShell is unavailable" \
      "Windows checks stay unverified here; CI supplies that evidence."
  fi
fi

# The directory Git will run hooks from, canonical. Relative values are
# relative to the worktree root; an unset value resolves to .git/hooks, which
# is never the tracked directory. Comparing directories rather than strings
# is what lets an absolute core.hooksPath naming .githooks count as enabled.
hooks_actual() {
  hooks_actual_dir=$(git rev-parse --git-path hooks 2>/dev/null) || return 1
  case "$hooks_actual_dir" in
    /*) ;;
    *) hooks_actual_dir="$(git rev-parse --show-toplevel)/$hooks_actual_dir" ;;
  esac
  (CDPATH= cd -- "$hooks_actual_dir" 2>/dev/null && pwd -P)
}
hooks_expected=$(CDPATH= cd -- "$(git rev-parse --show-toplevel)/.githooks" 2>/dev/null && pwd -P)

echo
echo "Version control"

if [ -n "$hooks_expected" ] && [ "$(hooks_actual)" = "$hooks_expected" ]; then
  ok "git hooks enabled"
else
  # A hard failure: without this a clone commits with no local policy or secret
  # scan. CI remains a backstop, not the primary feedback loop.
  bad "git hooks are NOT enabled" "Inspect with 'tool/setup', then enable with 'tool/setup --fix'."
fi

git_name=$(git config --get user.name 2>/dev/null || true)
git_email=$(git config --get user.email 2>/dev/null || true)
if [ -n "$git_name" ] && [ -n "$git_email" ]; then
  ok "git identity configured ($git_name <$git_email>)"
else
  bad "git identity is incomplete" "Set user.name and user.email at the appropriate local or user scope before committing."
fi

command -v gitleaks >/dev/null 2>&1 && ok "gitleaks" \
  || warn "gitleaks not installed — commits will not be scanned for secrets" "CI scans too, but only after you have pushed."

if command -v gh >/dev/null 2>&1; then
  if gh auth status --hostname github.com >/dev/null 2>&1; then
    ok "gh authenticated for github.com"
  else
    warn "gh installed but not authenticated for github.com" "Run 'gh auth login' before reading issues or publishing work."
  fi
else
  warn "gh not installed — cannot read or file blocked issues" "Install: https://cli.github.com"
fi

if [ "$scope" = all ] || [ "$scope" = unixlike ]; then
  echo
  echo "Flavours declared by the flake"
# tool/checks/test builds every configuration on the host it runs on, so what
# matters here is only whether each one can also be *activated* from this
# machine. Building and activating are different questions: a NixOS closure
# builds on any Linux box, and only switching to it needs the real host.

found=0

if grep -Rqs --include='*.nix' 'homeConfigurations' flake.nix modules 2>/dev/null; then
  found=1
  ok "homeConfigurations — build and switch here"
fi

if grep -Rqs --include='*.nix' 'nixosConfigurations' flake.nix modules 2>/dev/null; then
  found=1
  if [ -r /etc/os-release ] && grep -q '^ID=nixos' /etc/os-release; then
    ok "nixosConfigurations — build and switch here"
  else
    warn "nixosConfigurations — build here, but not switch" \
         "nixos-rebuild switch needs the target host. The closure still builds and is still verified; only activation is out of reach."
  fi
fi

if grep -Rqs --include='*.nix' 'darwinConfigurations' flake.nix modules 2>/dev/null; then
  found=1
  if [ "$(uname -s)" = Darwin ]; then
    ok "darwinConfigurations — build and switch here"
  else
    warn "darwinConfigurations — evaluate here, but build and switch on Darwin" \
         "The Linux check evaluates its complete derivation; native build and activation remain Darwin evidence."
  fi
fi

  [ "$found" -eq 1 ] || warn "no Unix-like host configurations in the flake sources" \
       "tool/checks/test has nothing to verify."
fi

echo
if [ "$failed" -eq 1 ]; then
  printf "${red}Not ready.${off} Fix the ✗ items above before starting work.\n"
  exit 1
fi
printf "${green}Ready.${off} Warnings above only limit which flavours you can build or switch here.\n"
