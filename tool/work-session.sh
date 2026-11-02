#!/bin/sh
# Optional local handoff notes, never policy, approval or integration state.
# INV repository/worker-checkpoint
set -eu
umask 077
MSYS_NO_PATHCONV=1
MSYS2_ARG_CONV_EXCL='*'
export MSYS_NO_PATHCONV MSYS2_ARG_CONV_EXCL
usage() {
  echo 'usage: tool/configs session save < handoff.md'
  echo '       tool/configs session inspect'
}
command=${1:-}
case "$command" in help|--help|'') usage; exit 0 ;; esac
[ "$#" -eq 1 ] || { usage >&2; exit 2; }
case "$command" in save|inspect) ;; *) usage >&2; exit 2 ;; esac
root=$(git rev-parse --show-toplevel)
cd "$root"
state=.work-session.md
if [ "$command" = inspect ]; then
  echo 'Local handoff notes are not policy, approval, liveness or cleanup permission.'
  git worktree list --porcelain | while IFS= read -r line; do
    case "$line" in
      'worktree '*)
        path=${line#worktree }
        printf '\nWorkspace: %s\n' "$path"
        if [ -f "$path/$state" ] && [ ! -L "$path/$state" ]; then
          cat "$path/$state"
        else
          echo 'Checkpoint: unavailable; preserve any existing data and inspect explicitly.'
        fi
        if [ -e "$path/.work-session.lock" ] || [ -L "$path/.work-session.lock" ]; then
          echo 'Checkpoint write lock exists; preserve partial data and confirm ownership before recovery.'
        fi
        git -C "$path" status --short 2>/dev/null || echo 'Git state unavailable.'
        ;;
    esac
  done
  exit 0
fi
"$root/tool/version-control/authoring"
[ ! -L "$state" ] || { echo 'refuse symlink checkpoint' >&2; exit 1; }
[ ! -e "$state" ] || [ -f "$state" ] || { echo 'checkpoint must be a regular file' >&2; exit 1; }
[ -z "$(git ls-files -- "$state")" ] || { echo 'checkpoint must not be tracked' >&2; exit 1; }
git check-ignore -q "$state" || { echo 'checkpoint must be ignored' >&2; exit 1; }
# A short lock protects the note replacement only; it says nothing about work.
lock=.work-session.lock
mkdir "$lock" 2>/dev/null || { echo 'checkpoint writer exists; inspect lock before retry' >&2; exit 1; }
trap 'rm -f "$lock/note" "$lock/owner"; rmdir "$lock"' EXIT
trap 'exit 1' HUP INT TERM
printf 'pid: %s\ncreated: %s\n' "$$" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$lock/owner"
cat > "$lock/note"
grep -q '[^[:space:]]' "$lock/note" || { echo 'handoff must not be empty' >&2; exit 1; }
# Save is the explicit request to replace the old note, including legacy notes.
[ ! -L "$state" ] || { echo 'refuse symlink checkpoint' >&2; exit 1; }
[ ! -e "$state" ] || [ -f "$state" ] || { echo 'checkpoint must be a regular file' >&2; exit 1; }
mv "$lock/note" "$state"
printf 'Handoff saved: %s\n' "$root/$state"
