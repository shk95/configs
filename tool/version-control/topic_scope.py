"""Use one topic ownership check for local integration and optional PRs."""
# INV repository/local-development-integration
# INV repository/topic-source
from pathlib import Path
import re
import subprocess
from git_workflow import shell_command, topic_pattern
from repo_policy import load


def validate(branch, base, head, policy=None):
    policy = policy or load()
    topic = re.fullmatch(topic_pattern(policy), branch)
    if not topic:
        raise ValueError('Invalid topic source: ' + branch)
    if any(not re.fullmatch('[0-9a-f]{40}', value) for value in (base, head)):
        raise ValueError('Use full topic base/head SHA identities')
    # Optional PRs test a synthetic merge and may have a newer base than the
    # topic contains. Judge the topic's own changes, not unrelated base work.
    source_base = subprocess.check_output(['git', 'merge-base', base, head], text=True).strip()
    classifier = shell_command(Path(__file__).with_name('classify'))
    scopes = subprocess.check_output([*classifier, '--range', source_base, head], text=True).splitlines()
    if scopes == ['none'] or 'unclassified' in scopes:
        raise ValueError('A topic must contain classified source changes.')
    scope = topic.group('scope')
    if scope is None:
        return scopes
    # A reverted edit still belongs to a legacy topic's authored history. Exclude
    # commits already accepted on the target base, including newer PR base work.
    authored = subprocess.check_output(['git', 'log', '--full-history', '--diff-merges=first-parent',
                                        '--no-renames', '--format=', '--name-only',
                                        base + '..' + head], text=True)
    authored_scopes = subprocess.check_output([*classifier, '--stdin'], input=authored,
                                              text=True).splitlines() if authored.strip() else []
    if scopes != [scope] or any(value != scope for value in authored_scopes):
        raise ValueError('A topic must contain exactly its named owning scope.')
    return scopes
