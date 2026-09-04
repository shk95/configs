# Drops the repository context git exports to a hook. Git sets an absolute
# GIT_DIR (and, for some invocations, GIT_WORK_TREE) when it runs a hook from
# a linked worktree; left in place, every `git -C <fixture>` this domain's
# suite runs resolves against the real repository instead of the fixture and
# rewrites it. tool/version-control/test carries the same defence for the
# repository suite (#45); this is the Windows domain's own copy.
#
# Dot-source this before any git command in a test or check:
#   . (Join-Path $PSScriptRoot 'isolate-git.ps1')
#
# INV windows/no-inherited-git-context
foreach ($name in @(
        'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR',
        'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
        'GIT_NAMESPACE', 'GIT_CEILING_DIRECTORIES', 'GIT_PREFIX')) {
    if (Test-Path -LiteralPath "Env:$name") { Remove-Item -LiteralPath "Env:$name" }
}
