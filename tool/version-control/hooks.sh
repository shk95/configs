#!/bin/sh
# Shared tracked-hook directory decision. Source from the worktree root;
# callers retain their own diagnostics and explicit setup mutation.
# INV repository/hooks-are-the-tracked-ones

MSYS_NO_PATHCONV=1
MSYS2_ARG_CONV_EXCL='*'
export MSYS_NO_PATHCONV MSYS2_ARG_CONV_EXCL

# Git prints relative hook paths relative to the current directory. Resolve
# directories rather than comparing configuration strings, including links.
hooks_actual() {
  hooks_actual_dir=$(git rev-parse --git-path hooks 2>/dev/null) || return 1
  case "$hooks_actual_dir" in
    /*) ;;
    *) hooks_actual_dir="$(git rev-parse --show-toplevel)/$hooks_actual_dir" ;;
  esac
  (CDPATH= cd -- "$hooks_actual_dir" 2>/dev/null && pwd -P)
}

# A linked worktree can use the primary worktree's tracked hook directory.
# Unset, missing and foreign directories do not count as an enabled gate.
hooks_enabled() {
  hooks_enabled_actual=$(hooks_actual) || return 1
  git worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p' |
    while IFS= read -r hooks_enabled_root; do
      hooks_enabled_expected=$(CDPATH= cd -- "$hooks_enabled_root/.githooks" 2>/dev/null && pwd -P) || continue
      [ "$hooks_enabled_actual" = "$hooks_enabled_expected" ] && echo yes
    done | grep -q yes
}
