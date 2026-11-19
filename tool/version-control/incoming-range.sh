# Resolve the incoming commit set for ownership, messages and secret scanning.
# The empty tree is the only non-commit base (initial publication).
incoming_range() {
  if [ "$(git rev-parse --is-shallow-repository)" != false ]; then
    echo 'Incoming history requires a complete checkout' >&2
    return 1
  fi
  range_tip=$(git rev-parse --verify --end-of-options "$2^{commit}") || return
  if [ "$1" = "$(git hash-object -t tree --stdin </dev/null)" ]; then
    range_base=$1
    range_walk=$range_tip
  else
    range_base=$(git rev-parse --verify --end-of-options "$1^{commit}") || return
    range_walk="$range_base..$range_tip"
  fi
}
