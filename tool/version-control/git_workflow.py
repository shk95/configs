"""Git identity and operation state shared by repository workflow tools."""
# INV repository/workspace-preservation
# INV repository/workspace-choice
# INV repository/local-development-integration
import os
from pathlib import Path
import re
import subprocess


TOPIC_SLUG = r'[a-z0-9][a-z0-9-]*'
TOPIC_PREFIX = 'topic/'
TOPIC_SEPARATOR = '+'


def topic_pattern(policy):
    kinds = '|'.join(re.escape(x) for x in policy['topic_kinds'])
    scopes = '|'.join(re.escape(x) for x in policy['scopes'])
    legacy = rf'(?:{kinds})/(?P<scope>{scopes})-{TOPIC_SLUG}'
    child = re.escape(TOPIC_SEPARATOR) + TOPIC_SLUG
    topic = rf'{TOPIC_PREFIX}{TOPIC_SLUG}(?:{child})*'
    return f'(?:{topic}|{legacy})'


def topic_destination(branch, policy):
    if re.fullmatch(topic_pattern(policy), branch):
        return branch.rpartition(TOPIC_SEPARATOR)[0] or policy['base_branch']
    return None


def authoring(branch, policy):
    return branch == policy['base_branch'] or bool(re.fullmatch(topic_pattern(policy), branch))


def git(*args, cwd=None):
    return subprocess.check_output(['git', *args], cwd=cwd,
                                   env=dict(os.environ, GIT_OPTIONAL_LOCKS='0')).decode().strip()


def unfinished_operations(cwd):
    markers = ('MERGE_HEAD', 'rebase-merge', 'rebase-apply', 'CHERRY_PICK_HEAD',
               'REVERT_HEAD', 'sequencer', 'BISECT_START')
    return [marker for marker in markers
            if Path(git('rev-parse', '--path-format=absolute', '--git-path', marker, cwd=cwd)).exists()]


def linked_workspace():
    return git('rev-parse', '--git-dir') != git('rev-parse', '--git-common-dir')
