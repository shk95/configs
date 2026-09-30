#!/bin/sh
# Test-only environment setup. Source this before any fixture Git invocation;
# never source it in an operator command or a production hook.
# INV repository/fixture-git-isolation

# Git -c settings reach hook children as GIT_CONFIG_PARAMETERS; environment
# settings also have the numbered COUNT/KEY/VALUE encoding. Neither belongs
# to a synthetic repository. Enumerate exported numbered keys without eval.
MSYS_NO_PATHCONV=1
MSYS2_ARG_CONV_EXCL='*'
export MSYS_NO_PATHCONV MSYS2_ARG_CONV_EXCL
for fixture_git_config_name in $(env | awk -F= \
  '$1 ~ /^GIT_CONFIG_(KEY|VALUE)_[0-9]+$/ { print $1 }'); do
  unset "$fixture_git_config_name"
done
unset fixture_git_config_name
unset GIT_CONFIG_PARAMETERS GIT_CONFIG_COUNT GIT_CONFIG \
  GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE GIT_PREFIX \
  GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE \
  GIT_CEILING_DIRECTORIES GIT_SHALLOW_FILE GIT_EXEC_PATH \
  GIT_SSH GIT_SSH_COMMAND GIT_SSH_VARIANT GIT_PROXY_COMMAND

# Keep the caller's HOME intact. Ignore system/user configuration, including
# includes, rewrite rules, push URLs, credentials, hooks and init templates.
# Fixture commands write only their own local config after this boundary.
GIT_CONFIG_NOSYSTEM=1
GIT_CONFIG_SYSTEM=/dev/null
GIT_CONFIG_GLOBAL=/dev/null
GIT_TEMPLATE_DIR=
GIT_ALLOW_PROTOCOL=file
GIT_PROTOCOL_FROM_USER=0
GIT_TERMINAL_PROMPT=0
export GIT_CONFIG_NOSYSTEM GIT_CONFIG_SYSTEM GIT_CONFIG_GLOBAL \
  GIT_TEMPLATE_DIR GIT_ALLOW_PROTOCOL GIT_PROTOCOL_FROM_USER GIT_TERMINAL_PROMPT
