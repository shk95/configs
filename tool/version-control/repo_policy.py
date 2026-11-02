"""Read the repository-owned mechanical contract; no host-local overrides."""
# INV repository/mechanical-policy
import json
from pathlib import Path
import re


def load():
    path = Path(__file__).with_name('policy.json')
    if path.is_symlink(): raise ValueError('Policy must be tracked local content, not an external symlink')
    value = json.loads(path.read_text())
    expected = {'schema', 'base_branch', 'scopes', 'topic_kinds', 'merge_method', 'workspace_choices',
                'workspace_record', 'remote', 'ci', 'history_rewrite'}
    if set(value) != expected:
        raise ValueError('Unknown or missing mechanical policy fields')
    if value['schema'] != 1 or value['base_branch'] != 'master' or value['merge_method'] != 'no-ff':
        raise ValueError('Unsupported policy schema or merge method')
    for key in ('base_branch', 'workspace_record'):
        if not re.fullmatch('[a-zA-Z0-9_.-]+', value[key]):
            raise ValueError('Unsafe policy identifier: ' + key)
    if len(value['workspace_choices']) != len(set(value['workspace_choices'])):
        raise ValueError('Duplicate workspace choice')
    for key in ('scopes', 'topic_kinds', 'workspace_choices'):
        if not value[key] or any(not isinstance(x, str) or not re.fullmatch('[a-z][a-z0-9-]*', x) for x in value[key]):
            raise ValueError('Invalid policy choices: ' + key)
    if set(value['workspace_choices']) != {'current', 'linked'}:
        raise ValueError('Unsupported workspace operation')
    nested = {
        'remote': {'enforce_admins', 'allow_deletions', 'required_status_checks',
                   'required_pull_request_reviews', 'required_conversation_resolution',
                   'allow_merge_commit', 'allow_squash_merge', 'allow_rebase_merge',
                   'lock_branch', 'required_linear_history', 'restrictions'},
        'ci': {'workflow', 'gate', 'artifact', 'events', 'suite_commands'},
        'history_rewrite': {'workflow', 'ruleset', 'environment', 'app_id_variable', 'app_node_variable',
                            'attempts'}}
    for key, fields in nested.items():
        if set(value[key]) != fields: raise ValueError('Unknown or missing policy section fields: ' + key)
    if value['history_rewrite']['attempts'] != 1:
        raise ValueError('Approval cannot be reused by reruns')
    if not re.fullmatch('[a-z][a-z0-9-]*', value['history_rewrite']['ruleset']):
        raise ValueError('Invalid maintenance ruleset name')
    if set(value['ci']['events']) != {'push', 'pull_request', 'workflow_dispatch'}:
        raise ValueError('Unsupported CI event contract')
    for commands in value['ci']['suite_commands'].values():
        if not commands or any(not command or not all(isinstance(arg, str) and arg for arg in command)
                               or '..' in Path(command[0]).parts or Path(command[0]).is_absolute() or not command[0].startswith(('tool/', 'unixlike/', 'windows/')) for command in commands):
            raise ValueError('Unsafe suite command')
    return value


def topic_pattern(policy):
    kinds = '|'.join(re.escape(x) for x in policy['topic_kinds'])
    scopes = '|'.join(re.escape(x) for x in policy['scopes'])
    return rf'({kinds})/({scopes})-[a-z0-9][a-z0-9-]*'


def authoring(branch, policy=None):
    policy = policy or load()
    return branch == policy['base_branch'] or bool(re.fullmatch(topic_pattern(policy), branch))
