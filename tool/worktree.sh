#!/bin/sh
# Optional workspace interface; all preservation decisions use tracked tooling.
# INV repository/local-development-integration
# INV repository/workspace-preservation
set -eu
exec "$(dirname "$0")/version-control/workspaces" "$@"
