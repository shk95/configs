#!/bin/sh
# Local execution checkpoints, never integration state.
# INV repository/worker-checkpoint
set -eu
umask 077
MSYS_NO_PATHCONV=1
MSYS2_ARG_CONV_EXCL='*'
export MSYS_NO_PATHCONV MSYS2_ARG_CONV_EXCL
usage() {
  echo 'usage: tool/configs session start <plan-path|-> <lane>'
  echo '       tool/configs session recover <plan-path|-> <lane> [verified-original-base]'
  echo '       tool/configs session replan <plan-path> < handoff.md'
  echo '       tool/configs session checkpoint <active|suspended|handed-off|abandoned> < handoff.md'
  echo '       tool/configs session inspect'
}
command=${1:-}
case "$command" in help|--help|'') usage; exit 0 ;; esac
root=$(git rev-parse --show-toplevel)
cd "$root"
state=.work-session.md
if [ "$command" = inspect ]; then
  git worktree list --porcelain | while IFS= read -r line; do
    case "$line" in
      'worktree '*)
        path=${line#worktree }
        printf '\nWorkspace: %s\n' "$path"
        if [ -f "$path/$state" ] && [ ! -L "$path/$state" ]; then
          cat "$path/$state"
          id=$(sed -n 's/^session-id: //p' "$path/$state" | head -1)
          case "$id" in
            ????????-????-????-????-????????????)
              case "$id" in *[!a-fA-F0-9-]*) ;; *)
                quoted=$(printf '%s' "$path" | sed "s/'/'\\\\''/g")
                printf "Resume guidance (liveness unknown): codex -C '%s' resume '%s'\n" "$quoted" "$id"
              ;; esac ;;
          esac
        else
          echo 'Checkpoint: unknown; do not infer abandoned or removable.'
        fi
        if [ -d "$path/.work-session.lock" ] && [ ! -L "$path/.work-session.lock" ]; then
          echo 'Checkpoint write lock exists; preserve partial data and confirm ownership before recovery.'
          if [ -f "$path/.work-session.lock/owner" ] && [ ! -L "$path/.work-session.lock/owner" ]; then cat "$path/.work-session.lock/owner"; fi
        fi
        git -C "$path" status --short 2>/dev/null || echo 'Git state unavailable.'
        ;;
    esac
  done
  exit 0
fi
"$root/tool/version-control/require-linked-worktree"
[ ! -L "$state" ] || { echo 'refuse symlink checkpoint' >&2; exit 1; }
git check-ignore -q "$state" || { echo 'checkpoint must be ignored' >&2; exit 1; }
[ -z "$(git ls-files -- "$state")" ] || { echo 'checkpoint must not be tracked' >&2; exit 1; }
# A short write lock protects only atomic note replacement, not integration.
lock=.work-session.lock
mkdir "$lock" 2>/dev/null || { echo 'checkpoint writer exists; inspect lock before retry' >&2; exit 1; }
trap 'rm -f "$lock/note" "$lock/body" "$lock/owner"; rmdir "$lock"' EXIT
trap 'exit 1' HUP INT TERM
printf 'pid: %s\ncreated: %s\n' "$$" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$lock/owner"
read_plan() {
  revision=- digest=-
  if [ "$plan" != - ]; then
    case "$plan" in docs/work/*/spec.md) ;; *) echo 'plan must name a docs/work spec' >&2; exit 2 ;; esac
    [ -f "$plan" ] && [ ! -L "$plan" ] || { echo 'plan missing or symlinked' >&2; exit 1; }
    revision=$(git log -1 --format=%H -- "$plan")
    revision=${revision:-uncommitted}
    digest=$(git hash-object "$plan")
  fi
}
case "$command" in
  start|recover)
    { [ "$#" -eq 3 ] || { [ "$command" = recover ] && [ "$#" -eq 4 ]; }; } || { usage >&2; exit 2; }
    [ ! -e "$state" ] || { echo 'checkpoint exists; inspect and resume it' >&2; exit 1; }
    plan=$2 lane=$3
    case "$lane" in ''|*[!a-zA-Z0-9_-]*) echo 'lane must be a simple identifier' >&2; exit 2 ;; esac
    branch=$(git symbolic-ref --short HEAD)
    case "$branch" in feature/*|fix/*) ;; *) echo 'worker requires a feature or fix branch' >&2; exit 1 ;; esac
    start_head=$(git rev-parse HEAD)
    base=$start_head
    if [ "$command" = recover ]; then
      base=${4:-unknown}
      if [ "$base" != unknown ]; then
        base=$(git rev-parse --verify "$base^{commit}")
        git merge-base --is-ancestor "$base" HEAD || { echo 'original base is not an ancestor' >&2; exit 1; }
      fi
    fi
    read_plan
    id=${CODEX_THREAD_ID:-unknown}
    case "$id" in *[!a-zA-Z0-9-]*|'') id=unknown ;; esac
    {
      echo '# Worker checkpoint'
      echo 'state: active'
      printf 'start-head: %s\n' "$start_head"
      printf 'lane: %s\nbase: %s\nplan: %s\nplan-revision: %s\nplan-content: %s\nsession-id: %s\n' "$lane" "$base" "$plan" "$revision" "$digest" "$id"
      printf 'updated: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo 'Started; record goal, progress, evidence and next action before interruption.'
    } > "$lock/note"
    ;;
  replan)
    [ "$#" -eq 2 ] || { usage >&2; exit 2; }
    [ -f "$state" ] || { echo 'no checkpoint; start first' >&2; exit 1; }
    [ "$(sed -n 's/^state: //p' "$state" | head -1)" = suspended ] || { echo 'suspend before replanning' >&2; exit 1; }
    plan=$2
    [ "$plan" != - ] || { echo 'replanning requires a spec' >&2; exit 1; }
    read_plan
    cat > "$lock/body"
    grep -q '[^[:space:]]' "$lock/body" || { echo 'replan handoff must not be empty' >&2; exit 1; }
    awk 'NF == 0 {exit} !/^plan: / && !/^plan-revision: / && !/^plan-content: / && !/^updated: / {print}' "$state" > "$lock/note"
    printf 'plan: %s\nplan-revision: %s\nplan-content: %s\nupdated: %s\n\n' "$plan" "$revision" "$digest" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$lock/note"
    cat "$lock/body" >> "$lock/note"
    printf '\nPrevious checkpoint before replan:\n' >> "$lock/note"
    cat "$state" >> "$lock/note"
    ;;
  checkpoint)
    [ "$#" -eq 2 ] || { usage >&2; exit 2; }
    [ -f "$state" ] || { echo 'no checkpoint; start first' >&2; exit 1; }
    current=$(sed -n 's/^state: //p' "$state" | head -1)
    next=$2
    case "$current:$next" in
      active:active|active:suspended|active:handed-off|active:abandoned|suspended:active|suspended:suspended|suspended:abandoned|handed-off:active) ;;
      *) echo "invalid worker transition: $current -> $next" >&2; exit 1 ;;
    esac
    cat > "$lock/body"
    grep -q '[^[:space:]]' "$lock/body" || { echo 'handoff must not be empty' >&2; exit 1; }
    # Only preserve the original header; the remainder is human-readable data.
    awk 'NF == 0 {exit} !/^state: / && !/^updated: / {print}' "$state" > "$lock/note"
    printf 'state: %s\nupdated: %s\n\n' "$next" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$lock/note"
    cat "$lock/body" >> "$lock/note"
    ;;
  *) usage >&2; exit 2 ;;
esac
mv "$lock/note" "$state"
printf 'Worker checkpoint: %s\n' "$root/$state"
