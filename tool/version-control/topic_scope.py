"""Use one topic ownership check for local integration and optional PRs."""
# INV repository/local-development-integration
# INV repository/topic-source
from pathlib import Path
import re
import subprocess
from repo_policy import load, topic_pattern


def validate(branch, base, head, policy=None):
    policy = policy or load()
    if not re.fullmatch(topic_pattern(policy), branch):
        raise ValueError('Invalid topic source: ' + branch)
    if any(not re.fullmatch('[0-9a-f]{40}', value) for value in (base, head)):
        raise ValueError('Use full topic base/head SHA identities')
    # Optional PRs test a synthetic merge and may have a newer base than the
    # topic contains. Judge the topic's own changes, not unrelated base work.
    source_base = subprocess.check_output(['git', 'merge-base', base, head], text=True).strip()
    classifier = Path(__file__).with_name('classify')
    scopes = subprocess.check_output([str(classifier), '--range', source_base, head], text=True).splitlines()
    # A reverted edit still belongs to the topic's authored history. Exclude
    # commits already accepted on the target base, including newer PR base work.
    authored = subprocess.check_output(['git', 'log', '--no-merges', '--format=', '--name-only',
                                        base + '..' + head], text=True)
    authored_scopes = subprocess.check_output([str(classifier), '--stdin'], input=authored,
                                              text=True).splitlines() if authored.strip() else []
    scope = branch.split('/', 1)[1].split('-', 1)[0]
    if scopes != [scope] or any(value != scope for value in authored_scopes):
        raise ValueError('A topic must contain exactly its named owning scope.')
