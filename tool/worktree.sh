#!/bin/sh
#
# One working directory per branch, so several sessions can run at once without
# checking out over each other.
#
#   tool/worktree.sh new unixlike-shell feature
#   tool/worktree.sh list
#   tool/worktree.sh done unixlike-shell
#
# Worktrees are created as siblings of the repository, never inside it. A copy
# of the project within the project gets picked up by file watchers and language
# servers, producing duplicate-definition errors and a much slower analyse.
#
# They share .git, so `core.hooksPath` carries over — a new worktree has working
# hooks with no setup.
#
# A worktree made for an implementer is due for removal only after the pull
# request from its branch has merged: review feedback returns to the same
# worktree, and one removed earlier costs a fresh setup for every fix. That
# rule is the skill's (.agents/skills/run-version-control-workflow/SKILL.md,
# Start and Integrate). `done` performs the removal and does not check the
# merge, because whether a pull request has merged is a remote question this
# tool does not ask; it says when the removal was due instead.

set -e

# Guards text-tool arguments from Git for Windows' MSYS argument conversion,
# which can rewrite a leading-`/` argv element into a Windows path. See
# tool/version-control/hygiene for the full explanation and the observed
# failure (#79). Inert everywhere else.
MSYS_NO_PATHCONV=1
MSYS2_ARG_CONV_EXCL='*'
export MSYS_NO_PATHCONV MSYS2_ARG_CONV_EXCL

# Resolve the primary checkout even when this script is invoked from one of
# its linked worktrees. All task worktrees share one sibling directory.
cd "$(dirname "$0")/.." || exit 1
root=$(git worktree list --porcelain | sed -n '1s/^worktree //p')
[ -n "$root" ] || { echo "cannot find the primary worktree" >&2; exit 1; }
wt_root="$(dirname "$root")/$(basename "$root")-wt"
integration=dev

usage() {
  echo "usage: tool/worktree.sh new <name> [feature|fix]"
  echo "       tool/worktree.sh list"
  echo "       tool/worktree.sh done <name>    (once its pull request has merged)"
  exit 1
}

validate_name() {
  if ! printf '%s\n' "$1" | grep -Eq '^(unixlike|windows|common|repository)-[a-z0-9][a-z0-9-]*$'; then
    echo "name must be <unixlike|windows|common|repository>-<topic>" >&2
    exit 1
  fi
}

case "${1:-}" in
  new)
    name=${2:?"name required"}
    kind=${3:-feature}
    case "$kind" in feature|fix) ;; *) echo "kind must be feature or fix" >&2; exit 1 ;; esac
    validate_name "$name"

    git fetch -q origin "$integration"
    git worktree add -b "$kind/$name" "$wt_root/$kind-$name" "origin/$integration"

    echo
    echo "Worktree ready:"
    echo "  cd $wt_root/$kind-$name"
    echo "  branch $kind/$name (from origin/$integration)"
    ;;

  list)
    echo "Worktrees in play:"
    git worktree list
    echo
    echo "Shared resources do not parallelise: a connected device, a running"
    echo "instance of the app, anything writing to one fixed path. Only one"
    echo "session at a time may hold those."
    ;;

  done)
    name=${2:?"name required"}
    validate_name "$name"
    # Find the branch, not the directory name. A worktree pinned to a user's
    # base commit can have a different directory name and still be removable
    # once its pull request has merged.
    dir=$(git worktree list --porcelain | awk -v name="$name" '
      /^worktree / { path = substr($0, 10) }
      /^branch / && ($2 == "refs/heads/feature/" name || $2 == "refs/heads/fix/" name) {
        print path; exit
      }
    ')
    [ -n "$dir" ] || { echo "no worktree matching '$name'" >&2; exit 1; }

    git worktree remove "$dir"
    echo "Removed $dir"
    echo "The branch is kept; delete it once its pull request has merged."
    echo "That merge is also when this removal was due (run-version-control-workflow, Integrate)."
    ;;

  *) usage ;;
esac
